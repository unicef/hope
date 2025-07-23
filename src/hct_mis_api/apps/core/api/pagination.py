from collections import OrderedDict
from typing import Any

from rest_framework.pagination import (
    LimitOffsetPagination,
    _divide_with_ceil,
    _get_displayed_page_numbers,
    _get_page_links,
)
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.utils.urls import remove_query_param, replace_query_param


class NoCountLimitOffsetPagination(LimitOffsetPagination):
    """
    Override LimitOffsetPagination to remove count query from response.
    """

    def paginate_queryset(self, queryset: Any, request: Request, view: Any = None) -> list[Any] | None:
        self.limit = self.get_limit(request)
        if self.limit is None:
            return None

        self.offset = self.get_offset(request)
        self.request = request
        self.display_page_controls = self.template is not None
        return list(queryset[self.offset : self.offset + self.limit])

    def get_paginated_response(self, data: list[Any]) -> Response:
        return Response(
            OrderedDict([("next", self.get_next_link()), ("previous", self.get_previous_link()), ("results", data)])
        )

    def get_paginated_response_schema(self, schema: dict[str, Any]) -> dict[str, Any]:
        paginated_schema = super().get_paginated_response_schema(schema)
        paginated_schema["properties"].pop("count", None)
        return paginated_schema

    def get_next_link(self) -> str | None:
        url = self.request.build_absolute_uri()
        url = replace_query_param(url, self.limit_query_param, self.limit)

        offset = self.offset + self.limit  # type: ignore
        return replace_query_param(url, self.offset_query_param, offset)

    def get_html_context(self) -> Any:
        base_url = self.request.build_absolute_uri()

        if self.limit:
            current = _divide_with_ceil(self.offset, self.limit) + 1  # type: ignore

            final = current + 1
        else:
            current = 1
            final = 1

        if current > final:
            current = final

        def page_number_to_url(page_number: int) -> str:
            if page_number == 1:
                return remove_query_param(base_url, self.offset_query_param)
            offset = self.offset + ((page_number - current) * self.limit)  # type: ignore
            return replace_query_param(base_url, self.offset_query_param, offset)

        page_numbers = _get_displayed_page_numbers(current, final)
        page_links = _get_page_links(page_numbers, current, page_number_to_url)

        return {"previous_url": self.get_previous_link(), "next_url": self.get_next_link(), "page_links": page_links}

    def get_count(self, queryset: Any) -> int:
        return 0
