import abc
import json
import logging
import os
from typing import Dict, Optional

from django.conf import settings

from requests import session
from requests.adapters import HTTPAdapter
from urllib3 import Retry

logger = logging.getLogger(__name__)


class ExchangeRateClient(abc.ABC):
    @abc.abstractmethod
    def fetch_exchange_rates(self, with_history: bool = True) -> Dict:
        pass


class ExchangeRateClientDummy(ExchangeRateClient):
    def __init__(self, exchange_rates: Optional[Dict] = None):
        self.exchange_rates = exchange_rates or self.populate_from_file()

    def fetch_exchange_rates(self, with_history: bool = True) -> Dict:
        return self.exchange_rates

    def populate_from_file(self) -> Dict:
        exchange_rates_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "exchange_rates.json")
        with open(exchange_rates_file_path, "r") as exchange_rates_file:
            return json.load(exchange_rates_file)


class ExchangeRateClientAPI(ExchangeRateClient):
    def __init__(self, api_key: Optional[str] = None, api_url: Optional[str] = None) -> None:
        self.api_key = api_key or os.getenv("EXCHANGE_RATES_API_KEY")
        self.api_url: str = (
            api_url or os.getenv("EXCHANGE_RATES_API_URL") or "https://uniapis.unicef.org/biapi/v1/exchangerates"
        )

        if self.api_key is None:
            raise ValueError("Missing Ocp Apim Subscription Key")

        self._client = session()
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504], allowed_methods=None)
        self._client.mount(self.api_url, HTTPAdapter(max_retries=retries))
        self._client.headers.update({"Ocp-Apim-Subscription-Key": self.api_key})

    def fetch_exchange_rates(self, with_history: bool = True) -> Dict:
        params = {}

        if with_history is True:
            params["history"] = "yes"
        response = self._client.get(self.api_url, params=params)

        try:
            response.raise_for_status()
        except Exception as e:
            logger.exception(e)
            raise
        return response.json()


def get_exchange_rate_client() -> ExchangeRateClient:
    if settings.USE_DUMMY_EXCHANGE_RATES is True:
        return ExchangeRateClientDummy()
    return ExchangeRateClientAPI()
