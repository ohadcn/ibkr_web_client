import requests
from requests.adapters import HTTPAdapter, Retry
import logging
import json
from typing import List

from .config import IBKRConfig
from .auth import IBKRAuthenticator

from .ibkr_types import SortingOrder, Period, Alert


class IBKRHttpClient:
    def __init__(self, config: IBKRConfig, logger: logging.Logger = None):
        self.__config = config
        if logger is None:
            self.__logger = logging.getLogger(__name__)
            formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            self.__logger.setLevel(logging.DEBUG)
            stream_handler = logging.StreamHandler()
            file_handler = logging.FileHandler("api_client.log")
            stream_handler.setFormatter(formatter)
            file_handler.setFormatter(formatter)
            self.__logger.addHandler(stream_handler)
            self.__logger.addHandler(file_handler)
        else:
            self.__logger = logger
        self.__authenticator = IBKRAuthenticator(config, self.__logger)

        self.headers = {}
        self.__authenticator.set_default_headers(self.headers)

        # Create an internal Session instance
        self.session = requests.Session()
        self.session.headers = self.headers
        # Attach a retry strategy for handling retries
        retries = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
        adapter = HTTPAdapter(max_retries=retries)
        self.session.mount("https://", adapter)

        # Initialize brokerage session to get access to trading and market data (/iserver/* endpoints)
        self.init_brokerage_session()

    def init_brokerage_session(self):
        """
        Source: https://www.interactivebrokers.com/campus/ibkr-api-page/cpapi-v1/#ssodh-init
        NOTE: This is essential for using all /iserver endpoints, including access to trading and market data,
        """
        endpoint = "/iserver/auth/ssodh/init"
        json_content = {"publish": True, "compete": True}

        return self.__post(endpoint, json_content)

    def logout(self):
        """
        Source: https://www.interactivebrokers.com/campus/ibkr-api-page/cpapi-v1/#logout
        """
        endpoint = "/logout"

        return self.__post(endpoint)

    def portfolio_accounts(self):
        """
        Source: https://www.interactivebrokers.com/campus/ibkr-api-page/cpapi-v1/#portfolio-accounts
        """
        endpoint = "/portfolio/accounts"

        return self.__get(endpoint)

    def portfolio_subaccounts(self):
        """
        Source: https://www.interactivebrokers.com/campus/ibkr-api-page/cpapi-v1/#portfolio-subaccounts
        """
        endpoint = "/portfolio/subaccounts"

        return self.__get(endpoint)

    def portfolio_subaccounts_large(self, page_number: int = 0):
        """
        Source: https://www.interactivebrokers.com/campus/ibkr-api-page/cpapi-v1/#portfolio-subaccounts
        """
        endpoint = "/portfolio/subaccounts2"
        params = {"page": page_number}

        return self.__get(endpoint, params=params)

    def portfolio_account_metadata(self, account_id: str):
        """
        Source: https://www.interactivebrokers.com/campus/ibkr-api-page/cpapi-v1/#portfolio-meta
        """
        endpoint = f"/portfolio/{account_id}/meta"

        return self.__get(endpoint)

    def portfolio_account_allocation(self, account_id: str):
        """
        Source: https://www.interactivebrokers.com/campus/ibkr-api-page/cpapi-v1/#portfolio-allocation-single
        """
        endpoint = f"/portfolio/{account_id}/allocation"

        return self.__get(endpoint)

    def portfolio_account_positions(self, account_id: str):
        """
        Source: https://www.interactivebrokers.com/campus/ibkr-api-page/cpapi-v1/#portfolio-combo
        """
        endpoint = f"/portfolio/{account_id}/combo/positions"
        params = {"nocache": True}

        return self.__get(endpoint, params=params)

    def portfolio_all_allocation(self, account_ids: List[str]):
        """
        Source: https://www.interactivebrokers.com/campus/ibkr-api-page/cpapi-v1/#portfolio-allocation-all
        """
        endpoint = "/portfolio/allocation"
        json_content = {"acctIds": account_ids}

        return self.__post(endpoint, json_content=json_content)

    def get_positions(self, account_id: str, page_id: int = 0):
        """
        Source: https://www.interactivebrokers.com/campus/ibkr-api-page/cpapi-v1/#positions
        """
        endpoint = f"/portfolio/{account_id}/positions/{page_id}"

        return self.__get(endpoint)

    def get_all_positions(self, account_id: str, sorting_order: SortingOrder):
        """
        Source: https://www.interactivebrokers.com/campus/ibkr-api-page/cpapi-v1/#positions
        """
        endpoint = f"/portfolio2/{account_id}/positions"
        params = {"direction": sorting_order.value, "sort": "position"}

        return self.__get(endpoint, params=params)

    def get_positions_by_contract_id(self, account_id: str, contract_id: str):
        """
        Source: https://www.interactivebrokers.com/campus/ibkr-api-page/cpapi-v1/#contract-positions
        """
        endpoint = f"/portfolio/{account_id}/position/{contract_id}"

        return self.__get(endpoint)

    def invalidate_backend_portfolio_cache(self, account_id: str):
        """
        Source: https://www.interactivebrokers.com/campus/ibkr-api-page/cpapi-v1/#portfolio-invalidate
        """
        endpoint = f"/portfolio/{account_id}/positions/invalidate"

        return self.__post(endpoint)

    def get_portfolio_summary(self, account_id: str):
        """
        Source: https://www.interactivebrokers.com/campus/ibkr-api-page/cpapi-v1/#portfolio-summary
        """
        endpoint = f"/portfolio/{account_id}/summary"

        return self.__get(endpoint)

    def get_portfolio_ledger(self, account_id: str):
        """
        Source: https://www.interactivebrokers.com/campus/ibkr-api-page/cpapi-v1/#portfolio-ledger
        """
        endpoint = f"/portfolio/{account_id}/ledger"

        return self.__get(endpoint)

    def get_position_info_by_contract_id(self, contract_id: str):
        """
        Source: https://www.interactivebrokers.com/campus/ibkr-api-page/cpapi-v1/#position-contract-info
        """
        endpoint = f"/portfolio/positions/{contract_id}"

        return self.__get(endpoint)

    def get_accounts_performance(self, account_ids: List[str], period: Period):
        """
        Source: https://www.interactivebrokers.com/campus/ibkr-api-page/cpapi-v1/#pa-account-performance
        """
        endpoint = f"/pa/performance"
        json_content = {"acctIds": account_ids, "period": period.value}

        return self.__post(endpoint, json_content)

    def get_accounts_transactions(
        self, account_ids: List[str], contract_ids: List[int], currency: str = "USD", days: int = 90
    ):
        """
        Source: https://www.interactivebrokers.com/campus/ibkr-api-page/cpapi-v1/#pa-account-transactions
        """
        endpoint = f"/pa/transactions"
        json_content = {"acctIds": account_ids, "conids": contract_ids, "currency": currency, "days": str(days)}

        return self.__post(endpoint, json_content)

    def create_alert(
        self,
        account_id: str,
        alert: Alert,
    ):
        """
        Source: https://www.interactivebrokers.com/campus/ibkr-api-page/cpapi-v1/#create-alert
        """
        endpoint = f"/iserver/account/{account_id}/alert"
        json_content = alert.__dict__()

        return self.__post(endpoint, json_content=json_content)

    def get_alert_list(self, account_id: str):
        """
        Source: https://www.interactivebrokers.com/campus/ibkr-api-page/cpapi-v1/#get-alert-list
        """
        endpoint = f"/iserver/account/{account_id}/alerts"

        return self.__get(endpoint)

    def delete_alert(self, account_id: str, alert_id: str):
        """
        Source: https://www.interactivebrokers.com/campus/ibkr-api-page/cpapi-v1/#delete-alert
        """
        endpoint = f"/iserver/account/{account_id}/alert/{alert_id}"

        return self.__delete(endpoint)

    def __get(self, endpoint: str, json_content: dict = {}, params: dict = {}) -> dict:
        method = "GET"
        url = f"{self.__config.base_url}/{endpoint.lstrip('/')}"

        headers = self.__authenticator.get_headers(method, url)
        self.session.headers.update(headers)

        response = self.session.get(url=url, json=json_content, params=params)

        self._log_response(response)
        return json.loads(response.content.decode("utf-8"))

    def __post(self, endpoint: str, json_content: dict = {}, params: dict = {}) -> dict:
        method = "POST"
        url = f"{self.__config.base_url}/{endpoint.lstrip('/')}"

        headers = self.__authenticator.get_headers(method, url)
        self.session.headers.update(headers)

        response = self.session.post(url=url, json=json_content, params=params)

        self._log_response(response)
        return json.loads(response.content.decode("utf-8"))

    def __delete(self, endpoint: str, json_content: dict = {}, params: dict = {}):
        method = "DELETE"
        url = f"{self.__config.base_url}/{endpoint.lstrip('/')}"

        headers = self.__authenticator.get_headers(method, url)
        self.session.headers.update(headers)

        response = self.session.delete(url=url, json=json_content, params=params)

        self._log_response(response)
        return json.loads(response.content.decode("utf-8"))

    def _log_response(self, response: requests.Response):
        if response.ok:
            self.__logger.info(f"Request successful: {response.status_code}")
            self.__logger.debug(f"Response content: {response.content}")
        else:
            self.__logger.error(f"Request failed: {response.status_code}, content: {response.content}")
