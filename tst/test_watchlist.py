from .test_base import client
from ibkr_web_client.client import IBKRHttpClient

WATCHLIST_ID = "123450101"
WATCHLIST_NAME = "Test Watchlist"
CONTRACT_ID_LST = [8314, 8894]


def test_00_create_watchlist(client: IBKRHttpClient):
    response = client.create_watchlist(
        watchlist_id=WATCHLIST_ID, watchlist_name=WATCHLIST_NAME, contract_id_lst=CONTRACT_ID_LST
    )

    assert response["id"] == WATCHLIST_ID
    assert len(response["hash"]) > 0
    assert response["name"] == WATCHLIST_NAME
    assert isinstance(response["readOnly"], bool)
    assert len(response["instruments"]) == 0
    assert isinstance(response["instruments"], list)


def test_01_get_all_watchlists(client: IBKRHttpClient):
    response = client.get_all_watchlists()

    assert "data" in response
    assert "user_lists" in response["data"]
    # only one watchlist is created in this test
    assert len(response["data"]["user_lists"]) == 1
    assert response["data"]["user_lists"][0]["id"] == WATCHLIST_ID
    assert response["data"]["user_lists"][0]["name"] == WATCHLIST_NAME
    assert response["data"]["user_lists"][0]["type"] == "watchlist"
    assert isinstance(response["data"]["user_lists"][0]["is_open"], bool)
    assert isinstance(response["data"]["user_lists"][0]["read_only"], bool)


def test_02_get_watchlist_info(client: IBKRHttpClient):
    response = client.get_watchlist_info(watchlist_id=WATCHLIST_ID)

    assert response["id"] == WATCHLIST_ID
    assert response["name"] == WATCHLIST_NAME
    assert isinstance(response["readOnly"], bool)
    assert len(response["instruments"]) == 2
    for instrument_obj in response["instruments"]:
        assert int(instrument_obj["C"]) in CONTRACT_ID_LST
        assert instrument_obj["conid"] in CONTRACT_ID_LST


def test_03_delete_watchlist(client: IBKRHttpClient):
    response = client.delete_watchlist(watchlist_id=WATCHLIST_ID)

    assert response["data"] == {"deleted": WATCHLIST_ID}
    assert response["action"] == "context"
