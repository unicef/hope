from datetime import datetime, timedelta
from typing import Any, Optional

from django.utils import timezone
import pytest
import requests_mock as requests_mock_lib

from hope.apps.core.exchange_rates import ExchangeRateClientAPI, ExchangeRates
from hope.apps.core.exchange_rates.api import ExchangeRateClientDummy

EXCHANGE_RATES_WITH_HISTORICAL_DATA = {
    "ROWSET": {
        "ROW": [
            {
                "CURRENCY_CODE": "XEU",
                "CURRENCY_NAME": "European Currency Unit",
                "X_RATE": ".867",
                "VALID_FROM": "01-DEC-98",
                "VALID_TO": "31-DEC-99",
                "RATIO": "1",
                "NO_OF_DECIMAL": "2",
                "PAST_XRATE": {
                    "PAST_XRATE_ROW": [
                        {
                            "VALID_FROM": "01-JAN-98",
                            "VALID_TO": "31-JAN-98",
                            "PAST_XRATE": ".906",
                            "PAST_RATIO": "1",
                        },
                        {
                            "VALID_FROM": "01-FEB-98",
                            "VALID_TO": "28-FEB-98",
                            "PAST_XRATE": ".926",
                            "PAST_RATIO": "1",
                        },
                        {
                            "VALID_FROM": "01-MAR-98",
                            "VALID_TO": "31-MAR-98",
                            "PAST_XRATE": ".909",
                            "PAST_RATIO": "1",
                        },
                    ]
                },
            },
            {
                "CURRENCY_CODE": "CUP1",
                "CURRENCY_NAME": "Cuban Peso (non convertible)",
                "X_RATE": "24",
                "VALID_FROM": "15-AUG-06",
                "VALID_TO": "31-DEC-99",
                "RATIO": "1",
                "NO_OF_DECIMAL": "2",
                "PAST_XRATE": None,
            },
        ]
    }
}

EXCHANGE_RATES_WITH_SHORT_HISTORICAL_DATA = {
    "ROWSET": {
        "ROW": [
            {
                "CURRENCY_CODE": "XEU",
                "CURRENCY_NAME": "European Currency Unit",
                "X_RATE": ".867",
                "VALID_FROM": "01-DEC-98",
                "VALID_TO": "31-DEC-99",
                "RATIO": "1",
                "NO_OF_DECIMAL": "2",
                "PAST_XRATE": {
                    "PAST_XRATE_ROW": [
                        {
                            "VALID_FROM": "01-JAN-98",
                            "VALID_TO": "31-JAN-98",
                            "PAST_XRATE": ".906",
                            "PAST_RATIO": "1",
                        },
                        {
                            "VALID_FROM": "01-FEB-98",
                            "VALID_TO": "28-FEB-98",
                            "PAST_XRATE": ".926",
                            "PAST_RATIO": "1",
                        },
                    ]
                },
            },
            {
                "CURRENCY_CODE": "CUP1",
                "CURRENCY_NAME": "Cuban Peso (non convertible)",
                "X_RATE": "24",
                "VALID_FROM": "15-AUG-06",
                "VALID_TO": "31-DEC-99",
                "RATIO": "1",
                "NO_OF_DECIMAL": "2",
                "PAST_XRATE": None,
            },
        ]
    }
}

EXCHANGE_RATES_WITH_LATEST_12_HISTORICAL_DATA = {
    "ROWSET": {
        "ROW": [
            {
                "CURRENCY_CODE": "XEU",
                "CURRENCY_NAME": "European Currency Unit",
                "X_RATE": ".867",
                "VALID_FROM": "01-DEC-98",
                "VALID_TO": "31-DEC-99",
                "RATIO": "1",
                "NO_OF_DECIMAL": "2",
                "PAST_XRATE": {
                    "PAST_XRATE_ROW": [
                        {
                            "VALID_FROM": "01-JAN-98",
                            "VALID_TO": "31-JAN-98",
                            "PAST_XRATE": ".906",
                            "PAST_RATIO": "1",
                        },
                        {
                            "VALID_FROM": "01-FEB-98",
                            "VALID_TO": "28-FEB-98",
                            "PAST_XRATE": ".926",
                            "PAST_RATIO": "1",
                        },
                    ]
                },
            },
            {
                "CURRENCY_CODE": "CUP1",
                "CURRENCY_NAME": "Cuban Peso (non convertible)",
                "X_RATE": "24",
                "VALID_FROM": "15-AUG-06",
                "VALID_TO": "31-DEC-99",
                "RATIO": "1",
                "NO_OF_DECIMAL": "2",
                "PAST_XRATE": None,
            },
        ]
    }
}

EXCHANGE_RATES_WITHOUT_HISTORICAL_DATA = {
    "ROWSET": {
        "ROW": [
            {
                "CURRENCY_CODE": "XEU",
                "CURRENCY_NAME": "European Currency Unit",
                "X_RATE": ".867",
                "VALID_FROM": "01-DEC-98",
                "VALID_TO": "31-DEC-99",
                "RATIO": "1",
                "NO_OF_DECIMAL": "2",
                "PAST_XRATE": None,
            },
            {
                "CURRENCY_CODE": "CUP1",
                "CURRENCY_NAME": "Cuban Peso (non convertible)",
                "X_RATE": "24",
                "VALID_FROM": "15-AUG-06",
                "VALID_TO": "31-DEC-99",
                "RATIO": "1",
                "NO_OF_DECIMAL": "2",
                "PAST_XRATE": None,
            },
        ]
    }
}


@pytest.fixture
def api_key_in_settings(settings):
    settings.EXCHANGE_RATES_API_KEY = "TEST_API_KEY"
    return settings


@pytest.fixture
def api_key_in_env(monkeypatch):
    monkeypatch.setenv("EXCHANGE_RATES_API_KEY", "TEST_API_KEY")


def test_api_default_initialization(api_key_in_settings):
    api_client = ExchangeRateClientAPI()
    assert api_client.api_key == "TEST_API_KEY"
    assert api_client.api_url == "https://uniapis.unicef.org/biapi/v1/exchangerates"


def test_api_key_provided_as_arg(api_key_in_settings):
    api_client = ExchangeRateClientAPI(api_key="API_KEY")
    assert api_client.api_key == "API_KEY"


def test_api_url_provided_as_arg(api_key_in_settings):
    api_client = ExchangeRateClientAPI(api_url="https://uni-apis.org")
    assert api_client.api_url == "https://uni-apis.org"


@pytest.mark.parametrize(
    ("url", "history_mode", "json_data"),
    [
        (
            "https://uniapis.unicef.org/biapi/v1/exchangerates?history=yes",
            ExchangeRateClientAPI.HISTORY_MODE_PARAM_LONG,
            EXCHANGE_RATES_WITH_HISTORICAL_DATA,
        ),
        (
            "https://uniapis.unicef.org/biapi/v1/exchangerates?history=short",
            ExchangeRateClientAPI.HISTORY_MODE_PARAM_SHORT,
            EXCHANGE_RATES_WITH_SHORT_HISTORICAL_DATA,
        ),
        (
            "https://uniapis.unicef.org/biapi/v1/exchangerates?history=12",
            ExchangeRateClientAPI.HISTORY_MODE_PARAM_LATEST_12,
            EXCHANGE_RATES_WITH_LATEST_12_HISTORICAL_DATA,
        ),
        (
            "https://uniapis.unicef.org/biapi/v1/exchangerates",
            None,
            EXCHANGE_RATES_WITHOUT_HISTORICAL_DATA,
        ),
    ],
    ids=["history_long", "history_short", "history_latest_12", "no_history"],
)
def test_fetch_exchange_rates(url: str, history_mode: Optional[str], json_data: dict):
    with requests_mock_lib.Mocker() as adapter:
        adapter.register_uri("GET", url=url, json=json_data)
        api_client = ExchangeRateClientAPI(api_key="TEST_API_KEY")
        response_dict = api_client.fetch_exchange_rates(history_mode=history_mode)
        assert json_data == response_dict


def test_convert_response_json_to_exchange_rates(api_key_in_env):
    exchange_rates_client = ExchangeRateClientDummy(EXCHANGE_RATES_WITH_HISTORICAL_DATA)
    converted_response = ExchangeRates(api_client=exchange_rates_client)._convert_response_json_to_exchange_rates()
    xeu = converted_response.get("XEU")
    cup1 = converted_response.get("CUP1")

    assert len(converted_response) == 2

    assert xeu.currency_code == "XEU"
    assert xeu.ratio == 1.0
    assert xeu.x_rate == 0.867
    assert datetime(1998, 12, 1, 0, 0) == xeu.valid_from
    assert datetime(9999, 12, 31) == xeu.valid_to

    assert len(xeu.historical_exchange_rates) == 3

    xeu_second_historical_rate = xeu.historical_exchange_rates[1]
    assert xeu_second_historical_rate.valid_to == datetime(1998, 2, 28)
    assert xeu_second_historical_rate.valid_from == datetime(1998, 2, 1)
    assert xeu_second_historical_rate.past_xrate == 0.926
    assert xeu_second_historical_rate.past_ratio == 1

    assert xeu.get_exchange_rate_by_dispersion_date(dispersion_date=None) == xeu.x_rate * xeu.ratio
    assert (
        xeu.get_exchange_rate_by_dispersion_date(dispersion_date=datetime(1998, 12, 15, 0, 0)) == xeu.x_rate * xeu.ratio
    )
    assert xeu.get_exchange_rate_by_dispersion_date(dispersion_date=datetime(1998, 2, 15, 0, 0)) == float(
        xeu_second_historical_rate.past_xrate
    ) * float(xeu_second_historical_rate.past_ratio)

    assert cup1.currency_code == "CUP1"
    assert cup1.ratio == 1.0
    assert cup1.x_rate == 24
    assert datetime(2006, 8, 15, 0, 0) == cup1.valid_from
    assert datetime(9999, 12, 31) == cup1.valid_to

    assert cup1.historical_exchange_rates == []


@pytest.mark.parametrize(
    ("currency_code", "dispersion_date", "expected_result"),
    [
        pytest.param("XEU", None, 0.867, id="xeu_without_dispersion_date"),
        pytest.param("XEU", datetime(1994, 3, 1), None, id="xeu_out_of_range_date"),
        pytest.param("XEU", datetime(1998, 2, 7), 0.926, id="xeu_historical_date_1"),
        pytest.param("XEU", datetime(1998, 3, 1), 0.909, id="xeu_historical_date_2"),
        pytest.param("CUP1", timezone.now() + timedelta(weeks=200), 24, id="cup1_future_date"),
    ],
)
def test_get_exchange_rate_for_currency_code(
    api_key_in_env,
    currency_code: str,
    dispersion_date: Optional[datetime],
    expected_result: Any,
):
    with requests_mock_lib.Mocker() as adapter:
        adapter.register_uri(
            "GET",
            "https://uniapis.unicef.org/biapi/v1/exchangerates?history=yes",
            json=EXCHANGE_RATES_WITH_HISTORICAL_DATA,
        )
        exchange_rates_client = ExchangeRates()
        exchange_rate = exchange_rates_client.get_exchange_rate_for_currency_code(currency_code, dispersion_date)
        assert expected_result == exchange_rate
