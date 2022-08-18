from datetime import datetime
from django.utils import timezone
from typing import Optional

from dateutil.parser import parse

from hct_mis_api.apps.core.exchange_rates.api import ExchangeRateAPI


class HistoryExchangeRate:
    def __init__(self, VALID_FROM: str, VALID_TO: str, PAST_XRATE: str, PAST_RATIO: str):
        self.valid_from = parse(VALID_FROM)
        self.valid_to = parse(VALID_TO)
        self.past_xrate = float(PAST_XRATE)
        self.past_ratio = float(PAST_RATIO)

    def __repr__(self):
        return (
            f"HistoryExchangeRate(valid_from: {self.valid_from.isoformat()}, valid_to: {self.valid_to.isoformat()}, "
            f"ratio: {self.past_ratio}, x_rate: {self.past_xrate})"
        )

    def is_valid_for_provided_dispersion_date(self, dispersion_date: datetime) -> bool:
        return self.valid_from <= dispersion_date <= self.valid_to


class SingleExchangeRate:
    def __init__(
        self,
        CURRENCY_CODE: str,
        CURRENCY_NAME: str,
        X_RATE: str,
        VALID_FROM: str,
        VALID_TO: str,
        RATIO: str,
        NO_OF_DECIMAL: str,
        PAST_XRATE: str,
    ):
        self.currency_code = CURRENCY_CODE
        self.currency_name = CURRENCY_NAME
        self.x_rate = float(X_RATE)
        self.valid_from = parse(VALID_FROM)
        self.valid_to = datetime(9999, 12, 31) if VALID_TO == "31-DEC-99" else parse(VALID_TO)
        self.ratio = float(RATIO)
        self.no_of_decimal = int(NO_OF_DECIMAL)

        past_xrates = PAST_XRATE["PAST_XRATE_ROW"] if PAST_XRATE is not None else []
        if isinstance(past_xrates, dict):
            past_xrates = [past_xrates]
        else:
            past_xrates.reverse()

        self.historical_exchange_rates = [HistoryExchangeRate(**past_xrate) for past_xrate in past_xrates]

    def __repr__(self):
        return f"SingleExchangeRate(currency_code: {self.currency_code}, ratio: {self.ratio}, x_rate: {self.x_rate})"

    def get_exchange_rate_by_dispersion_date(self, dispersion_date: datetime) -> Optional[float]:
        today = timezone.now()

        dispersion_date_is_not_provided = dispersion_date is None
        if dispersion_date_is_not_provided:
            return self.x_rate * self.ratio

        dispersion_date = datetime.combine(dispersion_date, datetime.min.time())
        dispersion_date_is_in_current_date_range = (
            self.valid_from <= dispersion_date <= (today if self.valid_to is None else self.valid_to)
        )
        if dispersion_date_is_in_current_date_range:
            return self.x_rate * self.ratio

        for historical_exchange_rate in self.historical_exchange_rates:
            if historical_exchange_rate.is_valid_for_provided_dispersion_date(dispersion_date):
                return historical_exchange_rate.past_xrate * historical_exchange_rate.past_ratio

        return None


class ExchangeRates:
    def __init__(self, with_history: bool = True, api_client: ExchangeRateAPI = None):
        if api_client is None:
            api = ExchangeRateAPI()
        else:
            api = api_client

        self.exchange_rates_dict = self._convert_response_json_to_exchange_rates(
            api.fetch_exchange_rates(with_history=with_history)
        )

    @staticmethod
    def _convert_response_json_to_exchange_rates(
        response_json: dict,
    ) -> dict[str, SingleExchangeRate]:
        raw_exchange_rates = response_json.get("ROWSET", {}).get("ROW", [])

        return {
            raw_exchange_rate["CURRENCY_CODE"]: SingleExchangeRate(**raw_exchange_rate)
            for raw_exchange_rate in raw_exchange_rates
        }

    def get_exchange_rate_for_currency_code(
        self, currency_code: str, dispersion_date: datetime = None
    ) -> Optional[float]:
        currency: SingleExchangeRate = self.exchange_rates_dict.get(currency_code)

        if currency is None:
            return None

        return currency.get_exchange_rate_by_dispersion_date(dispersion_date)
