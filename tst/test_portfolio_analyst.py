import pytest
from ibkr_web_client import IBKRHttpClient
from ibkr_web_client.ibkr_types import Period, BaseCurrency
from .test_base import client, account_id


def test_get_account_performance(client: IBKRHttpClient, account_id: str):
    response = client.get_accounts_performance([account_id,], Period.ONE_DAY)

    assert len(response) > 0


def test_get_transaction_history(client: IBKRHttpClient, account_id: str):
    response = client.get_accounts_transactions([account_id,], [265598,], BaseCurrency.USD, 1)

    assert len(response) > 0
    assert response["id"] == "getTransactions"
    assert response["currency"] == "USD"
