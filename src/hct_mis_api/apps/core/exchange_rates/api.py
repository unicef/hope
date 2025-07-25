import abc
import json
import logging
import os

from django.conf import settings

from requests import session
from requests.adapters import HTTPAdapter
from urllib3 import Retry

logger = logging.getLogger(__name__)


class ExchangeRateClient(abc.ABC):
    @abc.abstractmethod
    def fetch_exchange_rates(self, mode: str = "short") -> dict:
        pass


class ExchangeRateClientDummy(ExchangeRateClient):
    def __init__(self, exchange_rates: dict | None = None):
        self.exchange_rates = exchange_rates or self.populate_from_file()

    def fetch_exchange_rates(self, mode: str = "short") -> dict:
        return self.exchange_rates

    def populate_from_file(self) -> dict:
        exchange_rates_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "exchange_rates.json")
        with open(exchange_rates_file_path) as exchange_rates_file:
            return json.load(exchange_rates_file)


class ExchangeRateClientAPI(ExchangeRateClient):
    def __init__(self, api_key: str | None = None, api_url: str | None = None) -> None:
        self.api_key = api_key or settings.EXCHANGE_RATES_API_KEY
        self.api_url: str = api_url or settings.EXCHANGE_RATES_API_URL
        if self.api_key is None:
            raise ValueError("Missing Ocp Apim Subscription Key")

        self._client = session()
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504], allowed_methods=None)
        self._client.mount(self.api_url, HTTPAdapter(max_retries=retries))
        self._client.headers.update({"Ocp-Apim-Subscription-Key": self.api_key})

    def fetch_exchange_rates(self, mode: str = "short") -> dict:
        params = {}

        if mode == "yes":
            params["history"] = "yes"
        elif mode == "short":
            params["history"] = "short"
        response = self._client.get(self.api_url, params=params)

        try:
            response.raise_for_status()
        except Exception as e:
            logger.warning(e)
            raise
        return response.json()


def get_exchange_rate_client() -> ExchangeRateClient:
    if settings.USE_DUMMY_EXCHANGE_RATES is True:
        return ExchangeRateClientDummy()
    return ExchangeRateClientAPI()
