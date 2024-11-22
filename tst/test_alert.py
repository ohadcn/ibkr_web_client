import pytest

from tst.test_base import client, account_id, alert
from ibkr_web_client.ibkr_types import Alert
from ibkr_web_client.client import IBKRHttpClient


# TODO: check later, for now getting {"error":"Service Unavailable","statusCode":503}
def test_00_create_alert(client: IBKRHttpClient, account_id: str, alert: Alert):
    response = client.create_alert(account_id, alert)

    assert response["request_id"] is None
    assert response["success"] == True
    assert isinstance(response["order_id"], int)
    assert response["order_id"] > 0
    assert response["order_status"] is None
    assert response["warning_message"] is None


def test_01_get_alert_list(client: IBKRHttpClient, account_id: str, alert: Alert):
    response = client.get_alert_list(account_id)
    
    # there should be at least one alert
    assert len(response) > 0
    assert "order_id" in response[0]
    assert "account" in response[0]
    assert response[0]["account"] == account_id
    assert "alert_name" in response[0]
    # assert response[0]["alert_name"] == alert.alert_name
    assert "alert_active" in response[0]
    assert response[0]["alert_active"] == 1
    assert "order_time" in response[0]
    assert "alert_triggered" in response[0]
    assert "alert_repeatable" in response[0]
    # assert response[0]["alert_repeatable"] == alert.alert_repeatable


def test_03_delete_all_alarms(client: IBKRHttpClient, account_id: str):
    alerts_lst = client.get_alert_list(account_id)
    for alert in alerts_lst:
        response = client.delete_alert(account_id, str(alert["order_id"]))
        
        assert response["request_id"] is None
        assert response["success"] == True
        assert response["order_id"] == alert["order_id"]
        assert response["text"] == "Request was submitted"
        assert response["failure_list"] is None

    # Verify that all alarms are deleted
    response = client.get_alert_list(account_id)
    assert len(response) == 0
