import pytest

from tst.test_base import client
from ibkr_web_client.client import IBKRHttpClient
from ibkr_web_client.ibkr_types import MarketDataField


def test_get_live_market_data_snapshot(client: IBKRHttpClient):
    response = client.get_live_market_data_snapshot(
        [265598], [MarketDataField.LAST_PRICE, MarketDataField.ASK_PRICE, MarketDataField.BID_PRICE]
    )

    assert len(response) == 1
    assert response[0]["conid"] == 265598
    assert float(response[0][str(MarketDataField.LAST_PRICE.value)]) > 0
    assert float(response[0][str(MarketDataField.ASK_PRICE.value)]) > 0
    assert float(response[0][str(MarketDataField.BID_PRICE.value)]) > 0
    assert isinstance(response[0]["6509"], str)
