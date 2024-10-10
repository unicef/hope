from typing import TYPE_CHECKING, Any

from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from hct_mis_api.api.endpoints.base import HOPEAPIView
from hct_mis_api.api.endpoints.program.filters import ProgramFilter
from hct_mis_api.api.endpoints.program.serializers import ProgramGlobalSerializer
from hct_mis_api.apps.program.models import Program

if TYPE_CHECKING:
    from rest_framework.request import Request


class ProgramGlobalListView(HOPEAPIView, ListAPIView):
    serializer_class = ProgramGlobalSerializer
    queryset = Program.objects.all()

    def list(self, request: "Request", *args: Any, **kwargs: Any) -> Response:
        queryset = self.queryset
        filterset = ProgramFilter(request.GET, queryset=queryset)
        if filterset.is_valid():
            queryset = filterset.qs

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)
