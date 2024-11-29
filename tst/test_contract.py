import pytest

from tst.test_base import client, account_id
from ibkr_web_client.client import IBKRHttpClient


def test_get_futures_by_symbol(client: IBKRHttpClient):
    response = client.get_futures_by_symbol(["ES", "MES"])

    assert len(response) == 2
    assert "ES" in response
    assert response["ES"][0]["symbol"] == "ES"
    assert response["ES"][0]["conid"] > 0
    assert "MES" in response
    assert response["MES"][0]["symbol"] == "MES"
    assert response["MES"][0]["conid"] > 0


def test_get_futures_by_invalid_symbol(client: IBKRHttpClient):
    response = client.get_futures_by_symbol(["INVALID"])

    assert "INVALID" in response
    assert len(response["INVALID"]) == 0


def test_get_stocks_by_symbol(client: IBKRHttpClient):
    response = client.get_stocks_by_symbol(["AAPL", "MSFT"])

    assert len(response) == 2
    assert "AAPL" in response
    assert response["AAPL"][0]["name"] == "APPLE INC"
    assert response["AAPL"][0]["assetClass"] == "STK"
    assert len(response["AAPL"][0]["contracts"]) > 0
    assert "MSFT" in response
    assert response["MSFT"][0]["name"] == "MICROSOFT CORP"
    assert response["MSFT"][0]["assetClass"] == "STK"
    assert len(response["MSFT"][0]["contracts"]) > 0


def test_get_stocks_by_invalid_symbol(client: IBKRHttpClient):
    response = client.get_stocks_by_symbol(["INVALID"])

    assert "INVALID" in response
    assert len(response["INVALID"]) == 0


def test_get_security_definition(client: IBKRHttpClient):
    response = client.get_security_definition([265598, 272093])

    assert len(response["secdef"]) == 2
    assert response["secdef"][0]["conid"] == 265598
    assert response["secdef"][0]["ticker"] == "AAPL"
    assert response["secdef"][1]["conid"] == 272093
    assert response["secdef"][1]["ticker"] == "MSFT"
