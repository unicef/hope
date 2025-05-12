import dataclasses
from datetime import datetime

from django.conf import settings
from django.core.cache import cache
from django.utils import timezone

from dateutil.parser import parse

from hct_mis_api.apps.core.exchange_rates.api import (
    ExchangeRateClient,
    get_exchange_rate_client,
)


@dataclasses.dataclass(frozen=True)
class HistoryExchangeRate:
    valid_from: datetime
    valid_to: datetime
    past_xrate: float
    past_ratio: float

    @classmethod
    def from_dict(cls, data: dict) -> "HistoryExchangeRate":
        return cls(
            valid_from=parse(data["VALID_FROM"]),
            valid_to=parse(data["VALID_TO"]),
            past_xrate=float(data["PAST_XRATE"]),
            past_ratio=float(data["PAST_RATIO"]),
        )

    def is_valid(self, dispersion_date: datetime) -> bool:
        dispersion_date = datetime.combine(dispersion_date, datetime.min.time())
        return self.valid_from <= dispersion_date <= self.valid_to

    def calc_exchange_rate(self) -> float:
        return self.past_xrate * self.past_ratio


@dataclasses.dataclass(frozen=True)
class SingleExchangeRate:
    currency_code: str
    currency_name: str
    x_rate: float
    valid_from: datetime
    valid_to: datetime
    ratio: float
    no_of_decimal: int
    historical_exchange_rates: list[HistoryExchangeRate]

    @classmethod
    def from_dict(cls, data: dict) -> "SingleExchangeRate":
        valid_to = datetime(9999, 12, 31) if data["VALID_TO"] == "31-DEC-99" else parse(data["VALID_TO"])

        past_xrates = data["PAST_XRATE"]["PAST_XRATE_ROW"] if data["PAST_XRATE"] is not None else []
        if isinstance(past_xrates, dict):
            past_xrates = [past_xrates]
        else:
            past_xrates.reverse()
        return cls(
            currency_code=data["CURRENCY_CODE"],
            currency_name=data["CURRENCY_NAME"],
            x_rate=float(data["X_RATE"]),
            valid_from=parse(data["VALID_FROM"]),
            valid_to=valid_to,
            ratio=float(data["RATIO"]),
            no_of_decimal=int(data["NO_OF_DECIMAL"]),
            historical_exchange_rates=list(map(HistoryExchangeRate.from_dict, past_xrates)),
        )

    def get_exchange_rate_by_dispersion_date(self, dispersion_date: datetime) -> float | None:
        if self.is_valid(dispersion_date):
            return self.calc_exchange_rate()

        for historical_exchange_rate in self.historical_exchange_rates:
            if historical_exchange_rate.is_valid(dispersion_date):
                return historical_exchange_rate.calc_exchange_rate()

        return None

    def calc_exchange_rate(self) -> float:
        return self.x_rate * self.ratio

    def is_valid(self, dispersion_date: datetime) -> bool:
        if not dispersion_date:
            return True

        dispersion_date = datetime.combine(dispersion_date, datetime.min.time())
        valid_to = timezone.now() if self.valid_to is None else self.valid_to
        return self.valid_from <= dispersion_date <= valid_to


class ExchangeRates:
    CACHE_KEY = "exchange_rates"

    def __init__(self, api_client: ExchangeRateClient | None = None) -> None:
        self.api_client = api_client or get_exchange_rate_client()
        self.exchange_rates_dict = self._convert_response_json_to_exchange_rates()

    def _convert_response_json_to_exchange_rates(self) -> dict[str, SingleExchangeRate]:
        response_json = self._get_response()
        raw_exchange_rates = response_json.get("ROWSET", {}).get("ROW", [])

        exchange_rates = map(SingleExchangeRate.from_dict, raw_exchange_rates)
        return {exchange_rate.currency_code: exchange_rate for exchange_rate in exchange_rates}

    def _get_response(self) -> dict:
        if settings.EXCHANGE_RATE_CACHE_EXPIRY > 0:
            cached_response = cache.get(self.CACHE_KEY)
            if cached_response is not None:
                return cached_response

            response_json = self.api_client.fetch_exchange_rates()
            cache.set(self.CACHE_KEY, response_json, settings.EXCHANGE_RATE_CACHE_EXPIRY)
            return response_json
        return self.api_client.fetch_exchange_rates()

    def get_exchange_rate_for_currency_code(self, currency_code: str, dispersion_date: datetime) -> float | None:
        currency: SingleExchangeRate | None = self.exchange_rates_dict.get(currency_code)

        if currency is None:
            return None

        return currency.get_exchange_rate_by_dispersion_date(dispersion_date)
