from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from hope.models import SurprisePageConfig


class SurprisePageConfigView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request: Request) -> Response:
        try:
            config = SurprisePageConfig.objects.get(pk=1)
        except SurprisePageConfig.DoesNotExist:
            config = None
        return Response(
            {
                "image": config.image.url if config and config.image else None,
                "heading": config.heading if config else "",
                "subheading": config.subheading if config else "",
            }
        )
