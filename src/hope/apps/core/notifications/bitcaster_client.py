from dataclasses import dataclass
import logging
from typing import Any
from urllib.parse import urlparse

from django.conf import settings

logger = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class BitcasterClientConfig:
    api_url: str | None = None
    api_key: str | None = None
    organization_slug: str | None = None
    project_slug: str | None = None
    application_slug: str | None = None
    request_timeout: int | None = None


class BitcasterClient:
    def __init__(self, config: BitcasterClientConfig | None = None) -> None:
        config = config or BitcasterClientConfig()
        self.api_url = config.api_url or settings.BITCASTER_API_URL
        self.api_key = config.api_key or settings.BITCASTER_API_KEY
        self.organization_slug = config.organization_slug or settings.BITCASTER_ORGANIZATION_SLUG
        self.project_slug = config.project_slug or settings.BITCASTER_PROJECT_SLUG
        self.application_slug = config.application_slug or settings.BITCASTER_APPLICATION_SLUG
        self.request_timeout = config.request_timeout or settings.BITCASTER_REQUEST_TIMEOUT

    @property
    def is_configured(self) -> bool:
        return bool(
            self.api_url and self.api_key and self.organization_slug and self.project_slug and self.application_slug
        )

    def _build_bae(self) -> str:
        parsed = urlparse(self.api_url)
        return f"{parsed.scheme}://{self.api_key}@{parsed.netloc}/api/o/{self.organization_slug}/"

    def trigger_event(
        self,
        event_name: str,
        payload: dict[str, Any],
        options: dict[str, Any] | None = None,
        cid: str | None = None,
    ) -> bool:
        if not self.is_configured:
            logger.warning("Bitcaster client is not fully configured. Skipping event '%s'.", event_name)
            return False

        from bitcaster_sdk.client import Client as SDKClient

        sdk_client = SDKClient(bae=self._build_bae())
        self._configure_request_timeout(sdk_client)
        sdk_client.trigger(
            project=self.project_slug,
            application=self.application_slug,
            event=event_name,
            context=payload,
            options=options or {},
            cid=cid,
        )
        logger.info("Successfully triggered Bitcaster event: %s", event_name)
        return True

    def _configure_request_timeout(self, sdk_client: Any) -> None:
        original_request = sdk_client.transport.session.request

        def request_with_timeout(method: str, url: str, **kwargs: Any) -> Any:
            kwargs.setdefault("timeout", self.request_timeout)
            return original_request(method, url, **kwargs)

        sdk_client.transport.session.request = request_with_timeout
