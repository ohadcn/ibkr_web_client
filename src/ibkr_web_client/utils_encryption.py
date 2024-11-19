import random
import base64

from pathlib import Path
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Cipher import PKCS1_v1_5


class DiffieHellmanResolver:
    def __init__(self, dhparams: Path, random_value: int = None) -> None:
        with open(dhparams, "rb") as f:
            dh_parameters = serialization.load_pem_parameters(f.read(), backend=default_backend())
            dh_parameters_numbers = dh_parameters.parameter_numbers()
            dh_prime = dh_parameters_numbers.p  # Also known as DH Modulus
            dh_generator = dh_parameters_numbers.g

        self.__dh_prime = dh_prime
        self.__dh_generator = dh_generator
        self.__dh_random = random_value or self.__get_random_value()

    def get_challenge(self) -> int:
        """
        Returns hex value of A = g^a mod p, where g and p are the generator and prime from the registration step and $a is a random integer
        """
        return pow(base=self.__dh_generator, exp=self.__dh_random, mod=self.__dh_prime)

    def get_k(self, dh_response: str) -> bytes:
        B = int(dh_response, 16)
        K = pow(B, self.__dh_random, self.__dh_prime)

        # Generate hex string representation of integer K.
        hex_str_K = hex(K)[2:]
        # If hex string K has odd number of chars, add a leading 0, because all Python hex bytes must contain two hex digits  (0x01 not 0x1).
        if len(hex_str_K) % 2:
            hex_str_K = "0" + hex_str_K
        # Generate hex bytestring from hex string K.
        hex_bytes_K = bytes.fromhex(hex_str_K)
        # Prepend a null byte to hex bytestring K if lacking sign bit.
        if len(bin(K)[2:]) % 8 == 0:
            hex_bytes_K = bytes(1) + hex_bytes_K
        return hex_bytes_K

    def __get_random_value(self) -> int:
        return random.getrandbits(256)

def get_decrypted_text(private_encryption: Path, text: str) -> str:
    """
    Returns decrypted text as hex string
    """
    with open(private_encryption, "rb") as f:
        encryption_key = RSA.importKey(f.read())
    
    bytes_decrypted_secret = PKCS1_v1_5.new(key=encryption_key).decrypt(
        base64.b64decode(text),
        sentinel=None,
    )
    return bytes_decrypted_secret.hex()


def create_rsa_signer(private_signature: Path):
    with open(private_signature, "rb") as f:
        private_signature_key = RSA.importKey(f.read())

    return pkcs1_15.new(private_signature_key)


def get_sha256_hash(encoded_string: str):
    return SHA256.new(data=encoded_string)
