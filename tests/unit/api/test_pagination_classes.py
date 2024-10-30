from collections import OrderedDict

from rest_framework.response import Response

from hct_mis_api.api.pagination import LimitOffsetPaginationWithoutCount
from hct_mis_api.apps.core.base_test_case import APITestCase


class TestLimitOffsetPaginationWithoutCount(APITestCase):
    def test_get_paginated_response(self) -> None:
        obj = LimitOffsetPaginationWithoutCount()
        obj.offset = 0
        obj.limit = 10
        obj.count = 100
        obj.get_next_link = lambda: None
        obj.get_previous_link = lambda: None

        self.assertEqual(
            obj.get_paginated_response(data={}).data,
            Response(OrderedDict([("next", None), ("previous", None), ("results", {})])).data,
        )

    def test_get_paginated_response_schema(self) -> None:
        obj = LimitOffsetPaginationWithoutCount()
        obj.offset_query_param = "offset"
        obj.limit_query_param = "limit"
        expected_results = {
            "type": "object",
            "properties": {
                "next": {
                    "type": "string",
                    "nullable": True,
                    "format": "uri",
                    "example": "http://api.example.org/accounts/?{offset_param}=400&{limit_param}=100".format(
                        offset_param="offset", limit_param=obj.limit_query_param
                    ),
                },
                "previous": {
                    "type": "string",
                    "nullable": True,
                    "format": "uri",
                    "example": "http://api.example.org/accounts/?{offset_param}=200&{limit_param}=100".format(
                        offset_param="offset", limit_param=obj.limit_query_param
                    ),
                },
                "results": {},
            },
            "required": ["results"],
        }
        self.assertEqual(
            obj.get_paginated_response_schema({}),
            expected_results,
        )
