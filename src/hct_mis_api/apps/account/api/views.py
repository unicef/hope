from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

from hct_mis_api.apps.account.api.serializers import ProfileSerializer


class UserProfileView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            raise PermissionDenied("Permission Denied: User is not authenticated.")

        serializer = ProfileSerializer(user)
        return Response(serializer.data)
