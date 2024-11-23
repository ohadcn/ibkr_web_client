import pytest
from .test_base import client
from ibkr_web_client.client import IBKRHttpClient


def test_00_get_iserver_scanner_params(client: IBKRHttpClient):
    response = client.get_iserver_scanner_params()

    assert isinstance(response["scan_type_list"], list)
    assert isinstance(response["instrument_list"], list)
    assert isinstance(response["filter_list"], list)
    assert isinstance(response["location_tree"], list)


@pytest.mark.skip(reason="HMDS Scanner Params is not working")
def test_00_get_hmds_scanner_params(client: IBKRHttpClient):
    response = client.get_hmds_scanner_params()

    assert isinstance(response["scan_type_list"], list)
    assert isinstance(response["instrument_list"], list)
    assert isinstance(response["location_tree"], list)


def test_01_iserver_market_scanner(client: IBKRHttpClient):
    scanner_params = client.get_iserver_scanner_params()
    instrument = scanner_params["instrument_list"][0]["type"]
    location = next(filter(lambda x: x["type"] == instrument, scanner_params["location_tree"]))["locations"][0]["type"]
    scan_type = next(filter(lambda x: instrument in x["instruments"], scanner_params["scan_type_list"]))["code"]
    filter_lst = scanner_params["filter_list"][0]

    response = client.iserver_market_scanner(instrument, location, scan_type, [filter_lst])
    assert response["contracts"] is not None


def test_02_hmds_market_scanner(client: IBKRHttpClient):
    pass
