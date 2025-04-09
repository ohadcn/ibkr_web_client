import requests
from requests.adapters import HTTPAdapter, Retry
import logging
import json
from typing import List

from .config import IBKRConfig
from .auth import IBKRAuthenticator

from .ibkr_types import SortingOrder, Period, Alert, Exchange, OrderRule, BaseCurrency, MarketDataField

from time import sleep

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
        # The endpoint /iserver/accounts must be called prior to /iserver/marketdata/snapshot
        self.get_brokerage_accounts()

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
    
    def get_brokerage_accounts(self):
        """
        Source: https://www.interactivebrokers.com/campus/ibkr-api-page/cpapi-v1/#get-brokerage-accounts
        """
        endpoint = "/iserver/accounts"

        return self.__get(endpoint)

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
        self, account_ids: List[str], contract_ids: List[int], currency: BaseCurrency = BaseCurrency.USD, days: int = 90
    ):
        """
        Source: https://www.interactivebrokers.com/campus/ibkr-api-page/cpapi-v1/#pa-account-transactions
        """
        endpoint = f"/pa/transactions"
        json_content = {"acctIds": account_ids, "conids": contract_ids, "currency": currency.value, "days": days}

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

    def get_contract_info_and_rules(self, contract_id: int, order_rule: OrderRule):
        """
        Source: https://www.interactivebrokers.com/campus/ibkr-api-page/cpapi-v1/#info-rules-contract
        """
        endpoint = f"/iserver/contract/{contract_id}/info-and-rules"
        params = {"isBuy": order_rule == OrderRule.BUY}

        return self.__get(endpoint, params=params)

    def get_currency_pairs(self, currency: BaseCurrency):
        """
        Source: https://www.interactivebrokers.com/campus/ibkr-api-page/cpapi-v1/#get-currency-pairs
        """
        endpoint = f"/iserver/currency/pairs"
        params = {"currency": currency.value}

        return self.__get(endpoint, params=params)

    def get_currency_exchange_rate(self, target_currency: BaseCurrency, source_currency: BaseCurrency):
        """
        Source: https://www.interactivebrokers.com/campus/ibkr-api-page/cpapi-v1/#get-exchange-rate
        """
        endpoint = f"/iserver/exchangerate"
        params = {"target": target_currency.value, "source": source_currency.value}

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
    
    def get_live_market_data_snapshot(self, contract_id_lst: List[int], field_lst: List[MarketDataField]):
        """
        Source: https://www.interactivebrokers.com/campus/ibkr-api-page/cpapi-v1/#md-snapshot
        """
        endpoint = "/iserver/marketdata/snapshot"
        params = {"conids": ",".join(map(str, contract_id_lst)), "fields": ",".join(map(lambda x: str(x.value), field_lst))}

        return self.__get(endpoint, params=params)
    
    def get_historical_data(self, contract_id: str, bar_size: str = "1hrs", outsideRth: bool = True, period: str = "7d", barType: str = "Last"):
        """
        Source: https://www.interactivebrokers.com/campus/ibkr-api-page/cpapi-v1/#hist-md-beta
        See also: https://www.interactivebrokers.com/campus/ibkr-api-page/cpapi-v1/#hmds-period-bar-size
        Sometimes this API call require a preflight request to get the data, done automatically by the client.
        """

        endpoint = f"/hmds/history"
        params = {"bar": bar_size, "conid": contract_id, "period": period, "outsideRth": outsideRth, "barType": barType}

        retries = 3

        while retries > 0:
            try:
                response = self.__get(endpoint, params=params)
                if type(response) is dict and response.get("data"):
                    return response
                retries -= 1
                if retries == 0:
                    raise ValueError("No data found in response")
            except Exception as e:
                self._logger.error(f"Exception occurred: {e}")
                retries -= 1
                if retries == 0:
                    raise
    
    def get_orders(self, filters: str = None, force: bool = None):
        """
        Source: https://www.interactivebrokers.com/campus/ibkr-api-page/cpapi-v1/#live-orders
        :param filters: str = None
            The filters to apply to the orders. This can be a comma-separated list of values.
            The possible values are:
            active, inactive, filled, cancelled, pending_submit, WarnState, etc
          : https://www.interactivebrokers.com/campus/ibkr-api-page/cpapi-v1/#order-status-value
        :param force: bool = None
            If True, it will force a refresh of the orders. If False, it will return the cached orders.
            If None, It will request refreshing the orders and then return the new list.
            Default is None.
        """
        endpoint = f"/iserver/account/orders"
        if force is not None:
            params = {"force": force}
        else:
            self.get_orders(filters = filters, force = True)
            sleep(1)
            return self.get_orders(filters = filters, force = False)
        if filters is not None:
            params["filters"] = filters

        return self.__get(endpoint, params=params)
        
    def get_trades(self, days: int = 7, force: bool = None):
        """
        Source: https://www.interactivebrokers.com/campus/ibkr-api-page/cpapi-v1/#trades

        :param days: int = 7
            The number of days to get trades for. Default is 7.
            The maximum value is 7.

        :param force: bool = None
            The base call require a pre-flight request to get the data
            If None the client will run the pre-flight request, wait for a second and than the real request.
            Default is None.
        """
        if force is None:
            self.get_trades(days=days, force=True)
            sleep(1)
            return self.get_trades(days=days, force=False)

        endpoint = f"/iserver/account/trades"
        params = {"days": days}

        return self.__get(endpoint, params=params)
        
    def switch_account(self, account_id: str):
        """
        Switch the account for the IBKR API client
        for example: "U1234567"
        Source: https://www.interactivebrokers.com/campus/ibkr-api-page/cpapi-v1/#switch-account
        for requests like #get_orders and #get_trades
        """
        self._logger.debug(f"Switching account to {account_id}")
        endpoint = f"/iserver/account"
        params = {"acctId": account_id}
        response = self.__post(endpoint, json_content=params)
        self._logger.debug(f"Response: {response}")
        return response

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
