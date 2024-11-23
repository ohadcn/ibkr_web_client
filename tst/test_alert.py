import pytest

from tst.test_base import client, account_id
from ibkr_web_client.client import IBKRHttpClient
from ibkr_web_client.ibkr_types import Alert, GTCAlert, AlertCondition, PriceCondition, LogicBind, Operator


@pytest.fixture(scope="module")
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
        tif_alert=GTCAlert(),
        conditions=[condition],
    )


@pytest.fixture(scope="module")
def alert_obj(client: IBKRHttpClient, account_id: str, alert: Alert):
    alert.alert_name = "testing_alert"
    response = client.create_alert(account_id, alert)
    return alert, response["order_id"]


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
    assert response[0]["alert_name"] == alert.alert_name
    assert "alert_active" in response[0]
    assert response[0]["alert_active"] == 1
    assert "order_time" in response[0]
    assert "alert_triggered" in response[0]
    assert "alert_repeatable" in response[0]
    assert response[0]["alert_repeatable"] == alert.alert_repeatable


def test_02_modify_alert(client: IBKRHttpClient, account_id: str, alert_obj):
    _alert, alert_id = alert_obj
    _alert.alert_name = "modified_alert"
    response = client.modify_alert(account_id, alert_id, _alert)

    assert response["request_id"] is None
    assert response["success"] == True
    assert isinstance(response["order_id"], int)
    assert response["order_id"] > 0
    assert response["order_status"] is None
    assert response["warning_message"] is None


def test_03_deactivate_alert(client: IBKRHttpClient, account_id: str, alert_obj):
    _, alert_id = alert_obj
    response = client.set_alert_activation(account_id, alert_id, False)

    assert response["request_id"] is None
    assert response["success"] == True
    assert response["order_id"] == alert_id
    assert response["text"] == "Request was submitted"
    assert response["failure_list"] is None


def test_04_activate_alert(client: IBKRHttpClient, account_id: str, alert_obj):
    _, alert_id = alert_obj
    response = client.set_alert_activation(account_id, alert_id, True)

    assert response["request_id"] is None
    assert response["success"] == True
    assert response["order_id"] == alert_id
    assert response["text"] == "Request was submitted"
    assert response["failure_list"] is None


def test_05_get_alert_details(client: IBKRHttpClient, alert_obj):
    _alert, alert_id = alert_obj
    response = client.get_alert_details(alert_id)

    assert response["order_id"] == alert_id
    assert response["alert_active"] == 1


def test_06_delete_alert(client: IBKRHttpClient, account_id: str, alert_obj):
    _, alert_id = alert_obj
    response = client.delete_alert(account_id, alert_id)

    assert response["request_id"] is None
    assert response["success"] == True
    assert response["order_id"] == alert_id
    assert response["text"] == "Request was submitted"
    assert response["failure_list"] is None


def test_07_delete_all_alarms(client: IBKRHttpClient, account_id: str):
    response = client.delete_all_alerts(account_id)

    assert response["request_id"] is None
    assert response["success"] == True
    assert response["order_id"] == 0
    assert response["text"] == "Request was submitted"
    assert response["failure_list"] is None

    # Verify that all alarms are deleted
    response = client.get_alert_list(account_id)
    assert len(response) == 0
