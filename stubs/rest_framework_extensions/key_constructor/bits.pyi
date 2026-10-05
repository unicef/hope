from typing import Any

from rest_framework.request import Request

class KeyBitBase:
    def get_data(
        self,
        params: Any,
        view_instance: Any,
        view_method: Any,
        request: Request,
        args: tuple,
        kwargs: dict,
    ) -> str: ...

class UniqueMethodIdKeyBit(KeyBitBase): ...
class QueryParamsKeyBit(KeyBitBase): ...
class KwargsKeyBit(KeyBitBase): ...
class PaginationKeyBit(KeyBitBase): ...
