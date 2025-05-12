from typing import Optional

from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.utils.deprecation import MiddlewareMixin


class AllowSpecificIframeDomainsMiddleware(MiddlewareMixin):
    def process_response(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        origin: Optional[str] = request.META.get("HTTP_ORIGIN")
        referer: Optional[str] = request.META.get("HTTP_REFERER")

        if origin in settings.ALLOWED_IFRAME_DOMAINS or (
            referer and any(domain in referer for domain in settings.ALLOWED_IFRAME_DOMAINS)
        ):
            response["X-Frame-Options"] = "ALLOW-FROM " + (origin or referer or "")

        return response
