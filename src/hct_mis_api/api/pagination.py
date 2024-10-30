from collections import OrderedDict
from typing import Any

from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response


class LimitOffsetPaginationWithoutCount(LimitOffsetPagination):
    def get_paginated_response(self, data: dict) -> Response:
        return Response(
            OrderedDict([("next", self.get_next_link()), ("previous", self.get_previous_link()), ("results", data)])
        )

    def get_paginated_response_schema(self, schema: Any) -> dict:
        response_schema = super().get_paginated_response_schema(schema)
        del response_schema["properties"]["count"]
        return response_schema
