import logging
import datetime
import random
import base64
import requests
from Crypto.Hash import SHA1, HMAC, SHA256
from urllib.parse import quote_plus, quote

from .utils_encryption import DiffieHellmanResolver, get_decrypted_text, get_sha256_hash, create_rsa_signer
from .config import IBKRConfig


class IBKRAuthenticator:
    def __init__(self, config: IBKRConfig, logger: logging.Logger):
        self.__config = config
        self.__logger = logger
        self.__dh_resolver = DiffieHellmanResolver(self.__config.dh_param_path)
        self.__live_session_token = None
        self.__live_session_token_expiration = datetime.datetime.now().timestamp()

    def get_headers(self, method: str, url: str) -> dict:
        self.__update_live_session_token()
        return self.__generate_standard_headers(method, url)

    def __update_live_session_token(self):
        fetchLst = False
        if self.__live_session_token is None:
            self.__logger.info("Live session token is not set, fetching new one")
            fetchLst = True
        elif (
            self.__live_session_token_expiration
            < datetime.datetime.now().timestamp() + self.__config.update_session_interval
        ):
            self.__logger.info("Live session token is expired, fetching new one")
            fetchLst = True
        if fetchLst:
            self.__logger.info("Fetching new live session token")
            self.__live_session_token, self.__live_session_token_expiration = self.__fetch_live_session_token()
            self.__logger.info(
                f"New live session token expires at {datetime.datetime.fromtimestamp(self.__live_session_token_expiration/1000)}"
            )

    def __generate_standard_headers(self, method: str, url: str) -> dict:
        oauth_params = {
            "oauth_consumer_key": self.__config.consumer_key,
            "oauth_nonce": hex(random.getrandbits(128))[2:],
            "oauth_signature_method": "HMAC-SHA256",
            "oauth_timestamp": str(int(datetime.datetime.now().timestamp())),
            "oauth_token": self.__config.token_access,
        }

        params_string = "&".join([f"{k}={v}" for k, v in sorted(oauth_params.items())])
        base_string = f"{method}&{quote_plus(url)}&{quote(params_string)}"
        encoded_base_string = base_string.encode("utf-8")

        # Generate bytestring HMAC hash of base string bytestring.
        # Hash key is base64-decoded LST bytestring, method is SHA256.
        bytes_hmac_hash = HMAC.new(
            key=base64.b64decode(self.__live_session_token),
            msg=encoded_base_string,
            digestmod=SHA256,
        ).digest()

        # Generate str from base64-encoded bytestring hash.
        b64_str_hmac_hash = base64.b64encode(bytes_hmac_hash).decode("utf-8")

        # URL-encode the base64 hash str and add to oauth params dict.
        oauth_params["oauth_signature"] = quote_plus(b64_str_hmac_hash)
        oauth_params["realm"] = self.__config.realm
        # Assemble oauth params into auth header value as comma-separated str.
        oauth_header = "OAuth " + ", ".join([f'{k}="{v}"' for k, v in sorted(oauth_params.items())])
        # Create dict for LST request headers including OAuth Authorization header.
        headers = {
            "Authorization": oauth_header,
        }
        self.set_default_headers(headers)
        return headers

    # TODO: move to a proper place
    def set_default_headers(self, headers: dict):
        headers["User-Agent"] = f"python/{self.__config.python_version}"
        headers["Host"] = "api.ibkr.com"
        headers["Accept"] = "*/*"
        headers["Accept-Encoding"] = "gzip,deflate"
        headers["Connection"] = "Keep-Alive"

    def __fetch_live_session_token(self):
        self.__logger.info("Starting fetching live session token")

        method = "POST"
        url = f"{self.__config.base_url}/oauth/live_session_token"

        self.__logger.debug("Getting Diffie Hellman challenge")
        dh_challenge = hex(self.__dh_resolver.get_challenge())[2:]
        self.__logger.debug("Got Diffie Hellman challenge value")

        oauth_params = {
            "diffie_hellman_challenge": dh_challenge,
            "oauth_consumer_key": self.__config.consumer_key,
            "oauth_token": self.__config.token_access,
            "oauth_signature_method": "RSA-SHA256",
            "oauth_timestamp": str(int(datetime.datetime.now().timestamp())),
            "oauth_nonce": hex(random.getrandbits(128))[2:],
        }

        #  lexicographical order is important
        params_string = "&".join([f"{k}={v}" for k, v in sorted(oauth_params.items())])

        self.__logger.debug("Getting prepend for base signature string")
        # Secret must be added to signature base string
        prepend = get_decrypted_text(self.__config.dh_private_encryption_path, self.__config.token_secret)
        self.__logger.debug("Secret is obtained")

        base_string = f"{prepend}{method}&{quote_plus(url)}&{quote(params_string)}"
        encoded_base_string = base_string.encode("utf-8")

        # Generate SHA256 hash of base string bytestring.
        sha256_hash = get_sha256_hash(encoded_base_string)
        signer = create_rsa_signer(self.__config.dh_private_signature_path)
        bytes_pkcs115_signature = signer.sign(sha256_hash)
        b64_str_pkcs115_signature = base64.b64encode(bytes_pkcs115_signature).decode("utf-8")
        self.__logger.debug("signature base string is signed")

        # URL-encode the base64 signature str and add to oauth params dict.
        oauth_params["oauth_signature"] = quote_plus(b64_str_pkcs115_signature)
        oauth_params["realm"] = self.__config.realm

        oauth_header = "OAuth " + ", ".join([f'{k}="{v}"' for k, v in sorted(oauth_params.items())])
        # Create dict for LST request headers including OAuth Authorization header.
        headers = {"Authorization": oauth_header}
        # Add User-Agent header, required for all requests. Can have any value.
        self.set_default_headers(headers)

        self.__logger.info(f"Calling url={url} to get live session token")
        lst_response = requests.post(url=url, headers=headers)
        # Check if request returned 200, proceed to compute LST if true, exit if false.
        if not lst_response.ok:
            self.__logger.error("ERROR: Request to /live_session_token failed. Exiting...")
            self.__logger.debug(
                f"response from live session token: status-code: {lst_response.status_code}, content: {lst_response.content}"
            )
            raise SystemExit(0)  # TODO <- maybe add retry mechanism
        self.__logger.info("Successfully received live session token response")

        response_data = lst_response.json()
        dh_response = response_data["diffie_hellman_response"]
        lst_signature = response_data["live_session_token_signature"]
        lst_expiration = response_data["live_session_token_expiration"]
        self.__logger.debug(f"Live session token will expire at {datetime.datetime.fromtimestamp(lst_expiration/1000)}")

        return (
            self.__compute_live_session_token(dh_response, lst_signature, prepend),
            lst_expiration,
        )

    def __compute_live_session_token(self, dh_response: str, lst_signature: str, prepend: str) -> str:
        self.__logger.debug("Starting computing live session token")

        prepend_bytes = bytes.fromhex(prepend)
        self.__logger.debug("Starting getting K")
        hex_bytes_K = self.__dh_resolver.get_k(dh_response)

        bytes_hmac_hash_K = HMAC.new(
            key=hex_bytes_K,
            msg=prepend_bytes,
            digestmod=SHA1,
        ).digest()

        # The computed LST is the base64-encoded HMAC hash of the hex prepend bytestring. Converted here to str.
        computed_lst = base64.b64encode(bytes_hmac_hash_K).decode("utf-8")
        self.__logger.debug(f"Computed live session token")

        if self.__validate_lst_token(computed_lst, lst_signature):
            return computed_lst
        else:
            raise SystemExit(0)

    def __validate_lst_token(self, computed_lst_token: str, lst_signature: str) -> bool:
        # Generate hex-encoded str HMAC hash of consumer key bytestring.
        # Hash key is base64-decoded LST bytestring, method is SHA1.
        hex_str_hmac_hash_lst = HMAC.new(
            key=base64.b64decode(computed_lst_token),
            msg=self.__config.consumer_key.encode("utf-8"),
            digestmod=SHA1,
        ).hexdigest()

        # If our hex hash of our computed LST matches the LST signature received in response, we are successful.
        if hex_str_hmac_hash_lst == lst_signature:
            self.__logger.info("Live session token computation and validation successful.")
        else:
            self.__logger.error("Live session token validation failed.")
            return False
        return True
