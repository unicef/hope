import abc
import json
import logging
import os

from django.conf import settings
from django.core.cache import cache

from requests import session
from requests.adapters import HTTPAdapter
from urllib3 import Retry

logger = logging.getLogger(__name__)


class ExchangeRateClient(abc.ABC):
    @abc.abstractmethod
    def fetch_exchange_rates(self, with_history: bool = True) -> dict:
        pass


class ExchangeRateClientDummy(ExchangeRateClient):
    def fetch_exchange_rates(self, with_history: bool = True) -> dict:
        exchange_rates_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "exchange_rates.json")
        with open(exchange_rates_file_path, "r") as exchange_rates_file:
            return json.load(exchange_rates_file)


class ExchangeRateClientAPI(ExchangeRateClient):
    CACHE_KEY = "exchange_rates"

    def __init__(self, api_key: str = None, api_url: str = None):
        self.api_key = api_key or os.getenv("EXCHANGE_RATES_API_KEY")
        self.api_url = api_url or os.getenv(
            "EXCHANGE_RATES_API_URL", "https://uniapis.unicef.org/biapi/v1/exchangerates"
        )

        if self.api_key is None:
            raise ValueError("Missing Ocp Apim Subscription Key")

        self._client = session()
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504], method_whitelist=False)
        self._client.mount(self.api_url, HTTPAdapter(max_retries=retries))
        self._client.headers.update({"Ocp-Apim-Subscription-Key": self.api_key})

    def fetch_exchange_rates(self, with_history: bool = True) -> dict:
        if settings.USE_DUMMY_EXCHANGE_RATES is True:
            exchange_rates_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "exchange_rates.json")
            with open(exchange_rates_file_path, "r") as exchange_rates_file:
                return json.load(exchange_rates_file)

        params = {}

        if settings.EXCHANGE_RATE_CACHE_EXPIRY > 0:
            cached_response = cache.get(self.CACHE_KEY)
            if cached_response is not None:
                return cached_response
        if with_history is True:
            params["history"] = "yes"
        response = self._client.get(self.api_url, params=params)

        try:
            response.raise_for_status()
        except Exception as e:
            logger.exception(e)
            raise
        response_json = response.json()
        if settings.EXCHANGE_RATE_CACHE_EXPIRY > 0:
            cache.set(self.CACHE_KEY, response_json, settings.EXCHANGE_RATE_CACHE_EXPIRY)
        return response_json


def get_exchange_rate_client() -> ExchangeRateClient:
    if settings.USE_DUMMY_EXCHANGE_RATES is True:
        return ExchangeRateClientDummy()
    return ExchangeRateClientAPI()
