import requests
from requests.adapters import HTTPAdapter, Retry
import logging
import json
from typing import List

from .config import IBKRConfig
from .auth import IBKRAuthenticator

from .ibkr_types import SortingOrder, Period, Alert, Exchange


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

    def create_alert(self, account_id: str, alert: Alert):
        """
        Source: https://www.interactivebrokers.com/campus/ibkr-api-page/cpapi-v1/#create-alert
        """
        endpoint = f"/iserver/account/{account_id}/alert"
        json_content = alert.__dict__

        return self.__post(endpoint, json_content=json_content)

    def modify_alert(self, account_id: str, alert_id: int, alert: Alert):
        """
        Source: https://www.interactivebrokers.com/campus/ibkr-api-page/cpapi-v1/#create-alert
        """
        endpoint = f"/iserver/account/{account_id}/alert"
        json_content = alert.__dict__
        json_content["order_id"] = alert_id

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

    def delete_all_alerts(self, account_id: str):
        """
        Source: https://www.interactivebrokers.com/campus/ibkr-api-page/cpapi-v1/#delete-alert
        """
        alert_id = 0
        endpoint = f"/iserver/account/{account_id}/alert/{alert_id}"

        return self.__delete(endpoint)

    def set_alert_activation(self, account_id: str, alert_id: int, active_active: bool):
        """
        Source: https://www.interactivebrokers.com/campus/ibkr-api-page/cpapi-v1/#activate-alert
        """
        endpoint = f"/iserver/account/{account_id}/alert/activate"
        json_content = {"alertId": alert_id, "alertActive": int(active_active)}

        return self.__post(endpoint, json_content=json_content)

    def get_alert_details(self, alert_id: int):
        """
        Source: https://www.interactivebrokers.com/campus/ibkr-api-page/cpapi-v1/#get-alert
        """
        endpoint = f"/iserver/account/alert/{alert_id}"
        params = {"type": "Q"}

        return self.__get(endpoint, params=params)

    def create_watchlist(self, watchlist_id: str, watchlist_name: str, contract_id_lst: List[int]):
        """
        Source: https://www.interactivebrokers.com/campus/ibkr-api-page/cpapi-v1/#create-watchlist
        """
        endpoint = f"/iserver/watchlist"
        json_content = {
            "id": watchlist_id,
            "name": watchlist_name,
            "rows": [{"C": contract_id} for contract_id in contract_id_lst],
        }

        return self.__post(endpoint, json_content=json_content)

    def get_all_watchlists(self):
        """
        Source: https://www.interactivebrokers.com/campus/ibkr-api-page/cpapi-v1/#all-watchlists
        """
        endpoint = f"/iserver/watchlists"
        params = {"SC": "USER_WATCHLIST"}

        return self.__get(endpoint, params=params)

    def get_watchlist_info(self, watchlist_id: str):
        """
        Source: https://www.interactivebrokers.com/campus/ibkr-api-page/cpapi-v1/#watchlist-info
        """
        endpoint = f"/iserver/watchlist"
        params = {"id": watchlist_id}

        return self.__get(endpoint, params=params)

    def delete_watchlist(self, watchlist_id: str):
        """
        Source: https://www.interactivebrokers.com/campus/ibkr-api-page/cpapi-v1/#delete-watchlist
        """
        endpoint = f"/iserver/watchlist"
        params = {"id": watchlist_id}

        return self.__delete(endpoint, params=params)

    def get_iserver_scanner_params(self):
        """
        Source: https://www.interactivebrokers.com/campus/ibkr-api-page/cpapi-v1/#iserver-scanner-parameters
        """
        endpoint = "/iserver/scanner/params"

        return self.__get(endpoint)

    def iserver_market_scanner(self, instrument: str, location: str, scan_type: str, filter_lst: List[dict]):
        """
        Source: https://www.interactivebrokers.com/campus/ibkr-api-page/cpapi-v1/#iserver-market-scanner
        """
        endpoint = "/iserver/scanner/run"
        json_content = {"instrument": instrument, "location": location, "type": scan_type, "filter": filter_lst}

        return self.__post(endpoint, json_content=json_content)

    def get_hmds_scanner_params(self):
        """
        Source: https://www.interactivebrokers.com/campus/ibkr-api-page/cpapi-v1/#hmds-scanner-parameters
        I think it is still not working: https://www.reddit.com/r/IBKR_Official/comments/1e86w89/cant_access_hmdsscannerparams_via_cpapi/
        """
        endpoint = "/hmds/scanner/params"

        return self.__get(endpoint)

    def get_security_definition(self, contract_id_lst: List[int]):
        """
        Source: https://www.interactivebrokers.com/campus/ibkr-api-page/cpapi-v1/#trsrv-conid-contract
        """
        endpoint = f"/trsrv/secdef"
        params = {"conids": ",".join(map(str, contract_id_lst))}

        return self.__get(endpoint, params=params)

    def get_all_contracts(self, exchange: Exchange):
        """
        Source: https://www.interactivebrokers.com/campus/ibkr-api-page/cpapi-v1/#exchange-conids
        """
        endpoint = f"/trsrv/all-conids"
        params = {"exchange": exchange.id}

        return self.__get(endpoint, params=params)
    
    def get_contract_info(self, contract_id: int): 
        """
        Source: https://www.interactivebrokers.com/campus/ibkr-api-page/cpapi-v1/#info-conid-contract
        """
        endpoint = f"/iserver/contract/{contract_id}/info"

        return self.__get(endpoint)

    def get_currency_pairs(self, currency: str):
        """
        Source: https://www.interactivebrokers.com/campus/ibkr-api-page/cpapi-v1/#get-currency-pairs
        """
        endpoint = f"/iserver/currency/pairs"
        params = {"currency": currency}

        return self.__get(endpoint, params=params)
    
    def get_currency_exchange_rate(self, base_currency: str, quote_currency: str):
        """
        Source: https://www.interactivebrokers.com/campus/ibkr-api-page/cpapi-v1/#get-exchange-rate
        """
        endpoint = f"/iserver/exchangerate"
        params = {"target": quote_currency, "source": base_currency}

        return self.__get(endpoint, params=params)

    def get_futures_by_symbol(self, future_symbol_lst: List[str]):
        """
        Source: https://www.interactivebrokers.com/campus/ibkr-api-page/cpapi-v1/#trsrv-future-contract
        """
        endpoint = f"/trsrv/futures"
        params = {"symbols": ",".join(future_symbol_lst)}

        return self.__get(endpoint, params=params)

    def get_stocks_by_symbol(self, stock_symbol_lst: List[str]):
        """
        Source: https://www.interactivebrokers.com/campus/ibkr-api-page/cpapi-v1/#trsrv-stock-contract
        """
        endpoint = f"/trsrv/stocks"
        params = {"symbols": ",".join(stock_symbol_lst)}

        return self.__get(endpoint, params=params)

    def __get(self, endpoint: str, json_content: dict = {}, params: dict = {}) -> dict:
        method = "GET"
        url = f"{self.__config.base_url}/{endpoint.lstrip('/')}"

        headers = self.__authenticator.get_headers(method, url)
        self.session.headers.update(headers)

        self.__logger.debug(f"{method} request to {url} with params: {params} and json_content: {json_content}")
        response = self.session.get(url=url, json=json_content, params=params)

        self._log_response(response)
        return json.loads(response.content.decode("utf-8"))

    def __post(self, endpoint: str, json_content: dict = {}, params: dict = {}) -> dict:
        method = "POST"
        url = f"{self.__config.base_url}/{endpoint.lstrip('/')}"

        headers = self.__authenticator.get_headers(method, url)
        self.session.headers.update(headers)

        self.__logger.debug(f"{method} request to {url} with params: {params} and json_content: {json_content}")
        response = self.session.post(url=url, json=json_content, params=params)

        self._log_response(response)
        return json.loads(response.content.decode("utf-8"))

    def __delete(self, endpoint: str, json_content: dict = {}, params: dict = {}):
        method = "DELETE"
        url = f"{self.__config.base_url}/{endpoint.lstrip('/')}"

        headers = self.__authenticator.get_headers(method, url)
        self.session.headers.update(headers)

        self.__logger.debug(f"{method} request to {url} with params: {params} and json_content: {json_content}")
        response = self.session.delete(url=url, json=json_content, params=params)

        self._log_response(response)
        return json.loads(response.content.decode("utf-8"))

    def _log_response(self, response: requests.Response):
        if response.ok:
            self.__logger.info(f"Request successful: {response.status_code}")
            self.__logger.debug(f"Response content: {response.content}")
        else:
            self.__logger.error(f"Request failed: {response.status_code}, content: {response.content}")
