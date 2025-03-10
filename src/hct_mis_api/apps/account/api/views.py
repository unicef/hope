from typing import TYPE_CHECKING, Any

from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from hct_mis_api.apps.account.api.serializers import ProfileSerializer
from hct_mis_api.apps.account.models import User
from hct_mis_api.apps.core.api.mixins import BaseViewSet

if TYPE_CHECKING:
    from rest_framework.request import Request


class UserViewSet(BaseViewSet):
    queryset = User.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["get"], url_path="profile", url_name="profile")
    def profile(self, request: "Request", *args: Any, **kwargs: Any) -> Response:
        user = request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data)
