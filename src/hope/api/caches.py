import functools
from typing import Any, Callable

from django.conf import settings
from django.core.cache import cache
from django.db.models import Count, Max, QuerySet
from rest_framework import status
from rest_framework.response import Response
from rest_framework_extensions.key_constructor import bits
from rest_framework_extensions.key_constructor.bits import KeyBitBase
from rest_framework_extensions.key_constructor.constructors import KeyConstructor


def _inm_matches(etag: str, inm_header: str | None) -> bool:
    if not inm_header:
        return False
    # If-None-Match can be a comma-separated list, possibly with W/ weak tags
    tokens = [t.strip() for t in inm_header.split(",") if t.strip()]
    if "*" in tokens:
        return True

    def norm(s: str) -> str:
        s = s.strip()
        if s.startswith("W/"):
            s = s[2:].strip()
        return s

    n_etag = norm(etag)
    return any(n_etag == norm(t) for t in tokens)


def etag_decorator(
    key_constructor_class: "KeyConstructor", compare_etags: bool = True, safe_only: bool = True
) -> Callable:
    """Decorate ViewSet methods.

    Computes ETag from a KeyConstructor and:
    - For GET/HEAD: returns 304 when If-None-Match matches (weak compare).
    - Otherwise: sets ETag header on the response.
    """

    def inner(function: Callable) -> Callable:
        @functools.wraps(function)
        def wrapper(*args: Any, **kwargs: Any) -> Response:
            view_instance, request = args[0], args[1]

            if safe_only and request.method not in ("GET", "HEAD"):
                return function(*args, **kwargs)

            etag = key_constructor_class()(
                view_instance=view_instance,
                view_method=function,
                request=request,
                args=args[2:],
                kwargs=kwargs,
            )

            if compare_etags and not settings.DEBUG and _inm_matches(etag, request.headers.get("If-None-Match")):
                return Response(
                    status=status.HTTP_304_NOT_MODIFIED,
                    headers={
                        "ETag": etag,
                        "Cache-Control": "private, no-cache",
                        "Vary": "Authorization, Cookie",
                    },
                )

            res = function(*args, **kwargs)
            res.headers["ETag"] = etag
            res.headers.setdefault("Cache-Control", "private, no-cache")
            res.headers.setdefault("Vary", "Authorization, Cookie")
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
        self,
        params: Any,
        view_instance: Any,
        view_method: Any,
        request: Any,
        args: tuple,
        kwargs: dict,
    ) -> str:
        business_area_slug = kwargs.get("business_area_slug")
        business_area_version = get_or_create_cache_key(f"{business_area_slug}:version", 1)
        return str(business_area_version)


class KeyConstructorMixin(KeyConstructor):
    business_area_version = BusinessAreaVersionKeyBit()
    unique_method_id = bits.UniqueMethodIdKeyBit()
    querystring = bits.QueryParamsKeyBit()
    params = bits.KwargsKeyBit()
    pagination = bits.PaginationKeyBit()


class BusinessAreaKeyBitMixin(KeyBitBase):
    specific_view_cache_key = ""

    def get_data(
        self,
        params: Any,
        view_instance: Any,
        view_method: Any,
        request: Any,
        args: tuple,
        kwargs: dict,
    ) -> str:
        business_area_slug = kwargs.get("business_area_slug")
        business_area_version = get_or_create_cache_key(f"{business_area_slug}:version", 1)

        version_key = f"{business_area_slug}:{business_area_version}:{self.specific_view_cache_key}"
        version = get_or_create_cache_key(version_key, 1)
        return str(version)


class BusinessAreaAndProgramKeyBitMixin(KeyBitBase):
    specific_view_cache_key = ""

    def get_data(
        self,
        params: Any,
        view_instance: Any,
        view_method: Any,
        request: Any,
        args: tuple,
        kwargs: dict,
    ) -> str:
        business_area_slug = kwargs.get("business_area_slug")
        business_area_version = get_or_create_cache_key(f"{business_area_slug}:version", 1)

        program_slug = kwargs.get("program_slug")

        version_key = f"{business_area_slug}:{business_area_version}:{program_slug}:{self.specific_view_cache_key}"
        version = get_or_create_cache_key(version_key, 1)
        return str(version)


class BusinessAreaAndProgramLastUpdatedKeyBit(KeyBitBase):
    """KeyBit that validates the cache based on the latest `updated_at` and the number of objects in the queryset.

    It eliminates the need to create and maintain cache versions at the cost of an additional query to fetch
    the latest `updated_at` value and object count.
    The cache is based also on the business area, program and their version.
    """

    specific_view_cache_key = ""

    def _get_queryset(
        self,
        business_area_slug: Any | None,
        program_slug: Any | None,
        view_instance: Any | None,
    ) -> QuerySet:
        return view_instance.get_queryset()

    def get_data(
        self,
        params: Any,
        view_instance: Any,
        view_method: Any,
        request: Any,
        args: tuple,
        kwargs: dict,
    ) -> str:
        business_area_slug = kwargs.get("business_area_slug")
        business_area_version = get_or_create_cache_key(f"{business_area_slug}:version", 1)
        program_slug = kwargs.get("program_slug")

        queryset = self._get_queryset(business_area_slug, program_slug, view_instance).aggregate(
            latest_updated_at=Max("updated_at"), obj_count=Count("id")
        )
        latest_updated_at = queryset["latest_updated_at"]
        obj_count = queryset["obj_count"]

        return (
            f"{business_area_slug}:{business_area_version}:{program_slug}:{self.specific_view_cache_key}"
            f":{latest_updated_at}:{obj_count}"
        )


class AreaLimitKeyBit(KeyBitBase):
    def get_data(
        self,
        params: Any,
        view_instance: Any,
        view_method: Any,
        request: Any,
        args: tuple,
        kwargs: dict,
    ) -> str:
        return ",".join(
            map(
                str,
                request.user.partner.get_area_limits_for_program(view_instance.program.id)
                .order_by("created_at")
                .values_list("id", flat=True),
            )
        )
