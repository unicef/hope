from typing import Any

class KeyBitBase:
    def get_data(
        self,
        params: Any,
        view_instance: Any,
        view_method: Any,
        request: Any,
        args: tuple,
        kwargs: dict,
    ) -> str: ...

class UniqueMethodIdKeyBit(KeyBitBase): ...
class QueryParamsKeyBit(KeyBitBase): ...
class KwargsKeyBit(KeyBitBase): ...
class PaginationKeyBit(KeyBitBase): ...
