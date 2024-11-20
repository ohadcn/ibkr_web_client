import os
from pathlib import Path
import pytest

from ibkr_web_client import IBKRConfig, IBKRHttpClient

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


def assert_response_obj(response_obj: dict, key_type_map: dict):
    assert all(key in response_obj for key in key_type_map.keys())
    assert all(
        any(isinstance(response_obj[key], check_type) for check_type in check_type_lst)
        for key, check_type_lst in key_type_map.items()
    )
