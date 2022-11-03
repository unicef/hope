import os
from datetime import datetime, timedelta
from decimal import Decimal
from unittest import mock

from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

import requests_mock
from parameterized import parameterized

from hct_mis_api.apps.core.exchange_rates import ExchangeRateClientAPI, ExchangeRates
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.tests.test_files.exchange_rates_api_response import (
    EXCHANGE_RATES_API_RESPONSE,
)
from hct_mis_api.apps.household.fixtures import create_household
from hct_mis_api.apps.payment.fixtures import (
    RealCashPlanFactory,
    RealPaymentRecordFactory,
    RealProgramFactory,
    ServiceProviderFactory,
)
from hct_mis_api.apps.payment.models import PaymentRecord

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


class TestExchangeRatesAPI(TestCase):
    @mock.patch.dict(os.environ, clear=True)
    def test_test_api_class_initialization_key_not_in_env(self):
        self.assertRaisesMessage(ValueError, "Missing Ocp Apim Subscription Key", ExchangeRateClientAPI)

    @parameterized.expand(
        [
            ("default_initialization", None, None),
            ("api_provided_as_arg", "API_KEY", None),
            ("api_url_provided_as_arg", None, "https://uni-apis.org"),
        ]
    )
    def test_api_class_initialization(self, _, api_key, api_url):
        with mock.patch.dict(os.environ, {"EXCHANGE_RATES_API_KEY": "TEST_API_KEY"}, clear=True):
            api_client = ExchangeRateClientAPI(api_key=api_key, api_url=api_url)

            if api_key is not None:
                self.assertEqual(api_key, api_client.api_key)

            if api_url is not None:
                self.assertEqual(api_url, api_client.api_url)

            if api_url is None and api_key is None:
                self.assertEqual("TEST_API_KEY", api_client.api_key)
                self.assertEqual("https://uniapis.unicef.org/biapi/v1/exchangerates", api_client.api_url)

    @parameterized.expand(
        [
            ("with_history", True),
            ("without_history", False),
        ]
    )
    def test_fetch_exchange_rates(self, test_name, with_history):
        with requests_mock.Mocker() as adapter:
            if with_history is True:
                adapter.register_uri(
                    "GET",
                    "https://uniapis.unicef.org/biapi/v1/exchangerates?history=yes",
                    json=EXCHANGE_RATES_WITH_HISTORICAL_DATA,
                )
            else:
                adapter.register_uri(
                    "GET",
                    "https://uniapis.unicef.org/biapi/v1/exchangerates",
                    json=EXCHANGE_RATES_WITHOUT_HISTORICAL_DATA,
                )

            api_client = ExchangeRateClientAPI(api_key="TEST_API_KEY")
            response_dict = api_client.fetch_exchange_rates(with_history=with_history)

            if test_name == "with_history":
                self.assertEqual(EXCHANGE_RATES_WITH_HISTORICAL_DATA, response_dict)
            elif test_name == "without_history":
                self.assertEqual(EXCHANGE_RATES_WITHOUT_HISTORICAL_DATA, response_dict)


@mock.patch.dict(os.environ, {"EXCHANGE_RATES_API_KEY": "TEST_API_KEY"})
class TestExchangeRates(TestCase):
    def test_convert_response_json_to_exchange_rates(self):
        converted_response = ExchangeRates._convert_response_json_to_exchange_rates(EXCHANGE_RATES_WITH_HISTORICAL_DATA)
        xeu = converted_response.get("XEU")
        cup1 = converted_response.get("CUP1")

        self.assertEqual(2, len(converted_response))

        self.assertEqual("XEU", xeu.currency_code)
        self.assertEqual(1.0, xeu.ratio)
        self.assertEqual(0.867, xeu.x_rate)
        self.assertEqual(datetime(1998, 12, 1, 0, 0), xeu.valid_from)
        self.assertEqual(datetime(9999, 12, 31), xeu.valid_to)

        self.assertEqual(3, len(xeu.historical_exchange_rates))

        xeu_second_historical_rate = xeu.historical_exchange_rates[1]
        self.assertEqual(
            xeu_second_historical_rate,
            {
                "VALID_FROM": "01-FEB-98",
                "VALID_TO": "28-FEB-98",
                "PAST_XRATE": ".926",
                "PAST_RATIO": "1",
            },
        )

        # dispersion_date not provided, return current rate
        self.assertEqual(xeu.get_exchange_rate_by_dispersion_date(dispersion_date=None), xeu.x_rate * xeu.ratio)
        # dispersion_date from current valid date range, return current rate
        self.assertEqual(
            xeu.get_exchange_rate_by_dispersion_date(dispersion_date=datetime(1998, 12, 15, 0, 0)),
            xeu.x_rate * xeu.ratio,
        )
        # dispersion_date from past valid date range, return past rate
        self.assertEqual(
            xeu.get_exchange_rate_by_dispersion_date(dispersion_date=datetime(1998, 2, 15, 0, 0)),
            float(xeu_second_historical_rate["PAST_XRATE"]) * float(xeu_second_historical_rate["PAST_RATIO"]),
        )

        self.assertEqual("CUP1", cup1.currency_code)
        self.assertEqual(1.0, cup1.ratio)
        self.assertEqual(24, cup1.x_rate)
        self.assertEqual(datetime(2006, 8, 15, 0, 0), cup1.valid_from)
        self.assertEqual(datetime(9999, 12, 31), cup1.valid_to)

        self.assertEqual([], cup1.historical_exchange_rates)

    @parameterized.expand(
        [
            ("xeu_without_dispersion_date", "XEU", None, 0.867),
            ("xeu_out_of_range_date", "XEU", datetime(1994, 3, 1), None),
            ("xeu_historical_date_1", "XEU", datetime(1998, 2, 7), 0.926),
            ("xeu_historical_date_2", "XEU", datetime(1998, 3, 1), 0.909),
            ("cup1_future_date", "CUP1", timezone.now() + timedelta(weeks=200), 24),
        ]
    )
    def test_get_exchange_rate_for_currency_code(self, _, currency_code, dispersion_date, expected_result):
        with requests_mock.Mocker() as adapter:
            adapter.register_uri(
                "GET",
                "https://uniapis.unicef.org/biapi/v1/exchangerates?history=yes",
                json=EXCHANGE_RATES_WITH_HISTORICAL_DATA,
            )
            exchange_rates_client = ExchangeRates()
            exchange_rate = exchange_rates_client.get_exchange_rate_for_currency_code(currency_code, dispersion_date)
            self.assertEqual(expected_result, exchange_rate)


@mock.patch.dict(os.environ, {"EXCHANGE_RATES_API_KEY": "TEST_API_KEY"})
class TestFixExchangeRatesCommand(TestCase):
    @classmethod
    def setUpTestData(cls):
        business_area = BusinessArea.objects.create(
            code="0060",
            name="Afghanistan",
            long_name="THE ISLAMIC REPUBLIC OF AFGHANISTAN",
            region_code="64",
            region_name="SAR",
            has_data_sharing_agreement=True,
        )
        create_household(
            household_args={"size": 2, "business_area": business_area},
        )
        ServiceProviderFactory.create_batch(3)
        program = RealProgramFactory()
        cash_plans_with_currency = (
            (
                "PLN",
                RealCashPlanFactory(program=program, dispersion_date=timezone.make_aware(datetime(2021, 4, 4))),
            ),  # x_rate == 3.973
            (
                "AFN",
                RealCashPlanFactory(program=program, dispersion_date=timezone.make_aware(datetime(2020, 3, 3))),
            ),  # x_rate == 76.55
            (
                "USD",
                RealCashPlanFactory(program=program, dispersion_date=timezone.make_aware(datetime(2020, 3, 3))),
            ),  # x_rate ==  1
        )
        for currency, cash_plan in cash_plans_with_currency:
            RealPaymentRecordFactory(
                parent=cash_plan,
                currency=currency,
                delivered_quantity=200,
            )

    @requests_mock.Mocker()
    def test_modify_delivered_quantity_in_usd(self, mocker):
        mocker.register_uri(
            "GET",
            "https://uniapis.unicef.org/biapi/v1/exchangerates?history=yes",
            json=EXCHANGE_RATES_API_RESPONSE,
        )

        call_command("fixexchangerates", "--silent")

        all_payment_records = PaymentRecord.objects.all()

        expected_results = {
            "PLN": Decimal("50.34"),
            "AFN": Decimal("2.61"),
            "USD": Decimal("200"),
        }
        for payment_record in all_payment_records:
            self.assertEqual(expected_results[payment_record.currency], payment_record.delivered_quantity_usd)
