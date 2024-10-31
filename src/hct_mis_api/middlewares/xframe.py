from typing import List, Optional

from django.http import HttpRequest, HttpResponse
from django.utils.deprecation import MiddlewareMixin


class AllowSpecificIframeDomainsMiddleware(MiddlewareMixin):
    ALLOWED_IFRAME_DOMAINS: List[str] = [
        "https://localhost:3000",
        "https://dev-hope.unitst.org",
        "https://trn-hope.unitst.org",
        "https://stg-hope.unitst.org",
        "https://hope.unitst.org",
    ]

    def process_response(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        origin: Optional[str] = request.META.get("HTTP_ORIGIN")
        referer: Optional[str] = request.META.get("HTTP_REFERER")

        if origin in self.ALLOWED_IFRAME_DOMAINS or (
            referer and any(domain in referer for domain in self.ALLOWED_IFRAME_DOMAINS)
        ):
            response["X-Frame-Options"] = "ALLOW-FROM " + (origin or referer or "")

        return response
