from .test_base import (
    client,
    account_id,
    base_currency,
    assert_response_obj,
    ACCOUNT_KEY_TYPE_MAP,
    METADATA_ACCOUNT_KEY_TYPE_MAP,
    LONG_SHORT_KEY_TYPE_MAP,
    LEDGER_KEY_TYPE_MAP,
)
from ibkr_web_client import IBKRHttpClient
from ibkr_web_client.ibkr_types import SortingOrder


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
    assert "assetClass" in response
    assert "sector" in response
    assert "group" in response
    assert_response_obj(response["assetClass"], LONG_SHORT_KEY_TYPE_MAP)
    assert_response_obj(response["sector"], LONG_SHORT_KEY_TYPE_MAP)
    assert_response_obj(response["group"], LONG_SHORT_KEY_TYPE_MAP)


def test_portfolio_account_positions(client: IBKRHttpClient, account_id: str):
    response = client.portfolio_account_positions(account_id)

    # TODO: create position, vanilla paper trading account has no positions
    assert len(response) == 0


def test_portfolio_all_allocation(client: IBKRHttpClient, account_id: str):
    response = client.portfolio_all_allocation([account_id])

    assert len(response) > 0
    assert "assetClass" in response
    assert "sector" in response
    assert "group" in response
    assert_response_obj(response["assetClass"], LONG_SHORT_KEY_TYPE_MAP)
    assert_response_obj(response["sector"], LONG_SHORT_KEY_TYPE_MAP)
    assert_response_obj(response["group"], LONG_SHORT_KEY_TYPE_MAP)


def test_get_positions_page0(client: IBKRHttpClient, account_id: str):
    response = client.get_positions(account_id, 0)

    # TODO: create position, vanilla paper trading account has no positions
    assert len(response) == 0


def test_get_positions_page1(client: IBKRHttpClient, account_id: str):
    response = client.get_positions(account_id, 1)

    assert len(response) == 0


def test_get_all_positions(client: IBKRHttpClient, account_id: str):
    response = client.get_all_positions(account_id, SortingOrder.ASCENDING)

    # TODO: create position, vanilla paper trading account has no positions
    assert len(response) == 0


def get_positions_by_valid_contract_id(client: IBKRHttpClient, account_id: str):
    conid = 756733
    response = client.get_positions_by_contract_id(account_id, str(conid))

    # TODO: create position, vanilla paper trading account has no positions
    assert len(response) == 0


def test_get_positions_by_invalid_contract_id(client: IBKRHttpClient, account_id: str):
    response = client.get_positions_by_contract_id(account_id, "INVALID_CONTRACT_ID")

    assert response["statusCode"] == 400
    assert response["error"] == "Bad Request"


def test_invalidate_backend_portfolio_cache(client: IBKRHttpClient, account_id: str):
    response = client.invalidate_backend_portfolio_cache(account_id)

    assert "message" in response
    assert response["message"] == "success"
    # TODO: create scenario to test that cache indeed got updated


def test_get_portfolio_summary(client: IBKRHttpClient, account_id: str):
    response = client.get_portfolio_summary(account_id)

    # TODO: figure out structure of the response
    assert len(response) > 0


def test_get_portfolio_ledger(client: IBKRHttpClient, account_id: str, base_currency: str):
    response = client.get_portfolio_ledger(account_id)

    assert base_currency in response
    assert_response_obj(response[base_currency], LEDGER_KEY_TYPE_MAP)


def test_get_position_info_by_contract_id(client: IBKRHttpClient, account_id: str):
    conid = 756733
    response = client.get_position_info_by_contract_id(str(conid))

    # TODO: create position, vanilla paper trading account has no positions
    assert len(response) == 1
    assert account_id in response
    assert len(response[account_id]) == 0
