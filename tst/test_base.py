import os
from pathlib import Path
import pytest
from datetime import datetime
from ibkr_web_client import IBKRConfig, IBKRHttpClient
from ibkr_web_client.ibkr_types import Alert, GTDAlert, GTCAlert, AlertCondition, PriceCondition, LogicBind, Operator

ACCOUNT_KEY_TYPE_MAP = {
    "id": [str],
    "PrepaidCrypto-Z": [bool],
    "PrepaidCrypto-P": [bool],
    "brokerageAccess": [bool],
    "accountId": [str],
    "accountVan": [str],
    "accountTitle": [str],
    "displayName": [str],
    "accountAlias": [str, type(None)],
    "accountStatus": [int],
    "currency": [str],
    "type": [str],
    "tradingType": [str],
    "businessType": [str],
    "category": [str],
    "ibEntity": [str],
    "faclient": [bool],
    "clearingStatus": [str],
    "covestor": [bool],
    "noClientTrading": [bool],
    "trackVirtualFXPortfolio": [bool],
    "acctCustType": [str],
    "parent": [dict],
    "desc": [str],
}

METADATA_ACCOUNT_KEY_TYPE_MAP = {
    "total": [int],
    "pageSize": [int],
    "pageNum": [int],
}

LONG_SHORT_KEY_TYPE_MAP = {
    "long": [dict],
    "short": [dict],
}

LEDGER_KEY_TYPE_MAP = {
    "commoditymarketvalue": [float, int],
    "futuremarketvalue": [float, int],
    "settledcash": [float, int],
    "exchangerate": [float, int],
    "sessionid": [int],
    "cashbalance": [float, int],
    "corporatebondsmarketvalue": [float, int],
    "warrantsmarketvalue": [float, int],
    "netliquidationvalue": [float, int],
    "interest": [float, int],
    "unrealizedpnl": [float, int],
    "stockmarketvalue": [float, int],
    "moneyfunds": [float, int],
    "currency": [str],
    "realizedpnl": [float, int],
    "funds": [float, int],
    "acctcode": [str],
    "issueroptionsmarketvalue": [float, int],
    "key": [str],
    "timestamp": [int],
    "severity": [int],
    "stockoptionmarketvalue": [float, int],
    "futuresonlypnl": [float, int],
    "tbondsmarketvalue": [float, int],
    "futureoptionmarketvalue": [float, int],
    "cashbalancefxsegment": [float, int],
    "secondkey": [str],
    "tbillsmarketvalue": [float, int],
    "endofbundle": [int],
    "dividends": [float, int],
}


@pytest.fixture(scope="session")
def client() -> IBKRHttpClient:
    config = IBKRConfig(
        token_access=os.getenv("PAPER_API_IBKR_TOKEN"),
        token_secret=os.getenv("PAPER_API_IBKR_SECRET"),
        consumer_key=os.getenv("PAPER_API_IBKR_CONSUMER_KEY"),
        dh_param_path=Path(os.getenv("PAPER_API_IBKR_DH_PARAM")),
        dh_private_encryption_path=Path(os.getenv("PAPER_API_IBKR_DH_PRIVATE_ENCRYPTION")),
        dh_private_signature_path=Path(os.getenv("PAPER_API_IBKR_DH_PRIVATE_SIGNATURE")),
    )
    return IBKRHttpClient(config)


@pytest.fixture(scope="session")
def account_id(client: IBKRHttpClient) -> str:
    return client.portfolio_subaccounts()[0]["id"]


def assert_response_obj(response_obj: dict, key_type_map: dict, debug: bool = False):
    if debug:
        print("RESPONSE OBJECT: ", response_obj)
        for key in key_type_map.keys():
            if key not in response_obj:
                print(f"(!!!) {key} not in response_obj")

        for key, check_type_lst in key_type_map.items():
            any_type_check = False
            for check_type in check_type_lst:
                if isinstance(response_obj[key], check_type):
                    any_type_check = True
                    break
            if not any_type_check:
                print(f"(!!!) {key} wrong type, should be {check_type_lst} but is {type(response_obj[key])}")

    assert all(key in response_obj for key in key_type_map.keys())
    assert all(
        any(isinstance(response_obj[key], check_type) for check_type in check_type_lst)
        for key, check_type_lst in key_type_map.items()
    )


@pytest.fixture(scope="session")
def base_currency(client: IBKRHttpClient, account_id: str) -> str:
    return client.portfolio_account_metadata(account_id)["currency"]


@pytest.fixture(scope="session")
def alert() -> Alert:
    condition = AlertCondition(
        contract_id=265598,
        exchange="SMART",
        logic_bind=LogicBind.END,
        operator=Operator.GREATER_THAN,
        condition=PriceCondition(500),
    )
    return Alert(
        alert_name="test_alert",
        alert_message="test_alert",
        alert_repeatable=False,
        outside_rth=False,
        send_message=False,
        email="test@test.com",
        # tif_alert=GTDAlert(expireTime=datetime(year=2027, month=1, day=1, hour=12, minute=0, second=0)),
        tif_alert=GTCAlert(),
        conditions=[condition],
    )
