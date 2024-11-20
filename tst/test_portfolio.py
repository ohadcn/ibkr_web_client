from .test_base import client, account_id, assert_response_obj, ACCOUNT_KEY_TYPE_MAP, METADATA_ACCOUNT_KEY_TYPE_MAP
from ibkr_web_client import IBKRHttpClient


def test_portfolio_accounts(client: IBKRHttpClient):
    response = client.portfolio_accounts()

    assert len(response) > 0
    for account_obj in response:
        assert_response_obj(account_obj, ACCOUNT_KEY_TYPE_MAP)


def test_portfolio_subaccounts(client: IBKRHttpClient):
    response = client.portfolio_subaccounts()

    assert len(response) > 0
    for account_obj in response:
        assert_response_obj(account_obj, ACCOUNT_KEY_TYPE_MAP)


def test_portfolio_subaccounts_large_page_0(client: IBKRHttpClient):
    response = client.portfolio_subaccounts_large(0)

    assert "metadata" in response
    assert "subaccounts" in response

    metadata = response["metadata"]
    assert_response_obj(metadata, METADATA_ACCOUNT_KEY_TYPE_MAP)

    for account_obj in response["subaccounts"]:
        assert_response_obj(account_obj, ACCOUNT_KEY_TYPE_MAP)


def test_portfolio_subaccounts_large_page_1(client: IBKRHttpClient):
    response = client.portfolio_subaccounts_large(1)

    assert len(response) == 0


def test_account_metadata(client: IBKRHttpClient, account_id: str):
    response = client.portfolio_account_metadata(account_id)

    assert len(response) > 0
    assert_response_obj(response, ACCOUNT_KEY_TYPE_MAP)


def test_account_allocation(client: IBKRHttpClient, account_id: str):
    response = client.portfolio_account_allocation(account_id)

    assert len(response) > 0
    assert_response_obj(response, ACCOUNT_KEY_TYPE_MAP)
