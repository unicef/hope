from typing import TYPE_CHECKING, Any

from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from hct_mis_api.api.endpoints.base import HOPEAPIView
from hct_mis_api.api.endpoints.core.filters import BusinessAreaFilter
from hct_mis_api.api.endpoints.core.serializers import BusinessAreaSerializer
from hct_mis_api.apps.core.models import BusinessArea

if TYPE_CHECKING:
    from rest_framework.request import Request


class BusinessAreaListView(HOPEAPIView, ListAPIView):
    serializer_class = BusinessAreaSerializer
    queryset = BusinessArea.objects.all()

    def list(self, request: "Request", *args: Any, **kwargs: Any) -> Response:
        queryset = self.queryset

        filterset = BusinessAreaFilter(request.GET, queryset=queryset)
        if filterset.is_valid():
            queryset = filterset.qs

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
