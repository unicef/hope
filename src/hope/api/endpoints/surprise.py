import re

from constance import config
from django.core.files.storage import default_storage
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView


class SurprisePageConfigView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request: Request) -> Response:
        image_path = config.SURPRISE_PAGE_IMAGE
        image_url = default_storage.url(image_path) if image_path else None
        raw_body = config.SURPRISE_PAGE_BODY or ""
        paragraphs = [p.strip() for p in re.split(r"\n\s*\n", raw_body) if p.strip()]
        return Response(
            {
                "image": image_url,
                "heading": config.SURPRISE_PAGE_HEADING,
                "subheading": config.SURPRISE_PAGE_SUBHEADING,
                "paragraphs": paragraphs,
            }
        )
