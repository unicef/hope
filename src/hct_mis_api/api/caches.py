import functools
from typing import Any, Callable

from django.core.cache import cache

from rest_framework import status
from rest_framework.response import Response
from rest_framework_extensions.key_constructor import bits
from rest_framework_extensions.key_constructor.bits import KeyBitBase
from rest_framework_extensions.key_constructor.constructors import KeyConstructor

from hct_mis_api.apps.core.utils import decode_id_string


def etag_decorator(key_constructor_class: "KeyConstructor", compare_etags: bool = True) -> Callable:
    """Decorator operating on ViewSet methods.
    It expects for the first argument to be a view instance and for the second to be a request like:
        def view_function(self, request, *args, **kwargs)
    It calculates etag based on the KeyConstructor (key_constructor_class) and adds it to the response.
    If compare_etags is True it compares calculated etag with If-None_match header from the request.
    If they are the same, it returns 304 status code without any data.
    """

    def inner(function: Callable) -> Callable:
        @functools.wraps(function)
        def wrapper(*args: dict, **kwargs: dict) -> Response:
            # in view methods first argument is always self, second is request
            request = args[1]
            etag = key_constructor_class()(
                view_instance=args[0],
                view_method=function,
                request=request,
                args=args[2:],
                kwargs=kwargs,
            )

            # If etag from header and calculated are the same,
            # return 304 status code as request consists of the same data already (cached on client side)
            if compare_etags and request.headers.get("If-None-Match") == etag:
                return Response(status=status.HTTP_304_NOT_MODIFIED, headers={"ETAG": etag})
            res = function(*args, **kwargs)
            res.headers["ETAG"] = etag
            return res

        return wrapper

    return inner


def get_or_create_cache_key(key: str, default: Any) -> Any:
    """Get value from cache by key or create it with default value."""
    value = cache.get(key)
    if value is None:
        cache.set(key, default, timeout=None)
        return default
    return value


class BusinessAreaVersionKeyBit(KeyBitBase):
    def get_data(
        self, params: Any, view_instance: Any, view_method: Any, request: Any, args: tuple, kwargs: dict
    ) -> str:
        business_area_slug = kwargs.get("business_area")
        business_area_version = get_or_create_cache_key(f"{business_area_slug}:version", 1)
        return str(business_area_version)


class KeyConstructorMixin(KeyConstructor):
    business_area_version = BusinessAreaVersionKeyBit()
    unique_method_id = bits.UniqueMethodIdKeyBit()
    querystring = bits.QueryParamsKeyBit()
    params = bits.KwargsKeyBit()
    pagination = bits.PaginationKeyBit()


class BusinessAreaKeyBit(KeyBitBase):
    specific_view_cache_key = ""

    def get_data(
        self, params: Any, view_instance: Any, view_method: Any, request: Any, args: tuple, kwargs: dict
    ) -> str:
        business_area_slug = kwargs.get("business_area")
        business_area_version = get_or_create_cache_key(f"{business_area_slug}:version", 1)

        version_key = f"{business_area_slug}:{business_area_version}:{self.specific_view_cache_key}"
        version = get_or_create_cache_key(version_key, 1)
        return str(version)


class BusinessAreaAndProgramKeyBit(KeyBitBase):
    specific_view_cache_key = ""

    def get_data(
        self, params: Any, view_instance: Any, view_method: Any, request: Any, args: tuple, kwargs: dict
    ) -> str:
        business_area_slug = kwargs.get("business_area")
        business_area_version = get_or_create_cache_key(f"{business_area_slug}:version", 1)

        program_id = decode_id_string(kwargs.get("program_id"))

        version_key = f"{business_area_slug}:{business_area_version}:{program_id}:{self.specific_view_cache_key}"
        version = get_or_create_cache_key(version_key, 1)
        return str(version)


class ProgramKeyBit(KeyBitBase):
    def get_data(
        self, params: Any, view_instance: Any, view_method: Any, request: Any, args: tuple, kwargs: dict
    ) -> str:
        program_id = decode_id_string(kwargs.get("program_id"))
        version = get_or_create_cache_key(f"{program_id}:version", 1)
        return str(version)
