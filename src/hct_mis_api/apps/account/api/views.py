from typing import TYPE_CHECKING, Any

from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from hct_mis_api.apps.account.api.serializers import ProfileSerializer

if TYPE_CHECKING:
    from rest_framework.request import Request


class UserProfileView(APIView):
    def get(self, request: "Request", *args: Any, **kwargs: Any) -> Response:
        user = request.user
        if not user.is_authenticated:
            raise PermissionDenied("Permission Denied: User is not authenticated.")

        serializer = ProfileSerializer(user, context={"request": request})
        return Response(serializer.data)
