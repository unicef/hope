import functools
from typing import Any, Callable, ParamSpec

from constance import config
from django.conf import settings
from django.core.cache import cache
from rest_framework import status
from rest_framework.response import Response
from rest_framework_extensions.cache.decorators import CacheResponse
from rest_framework_extensions.key_constructor import bits
from rest_framework_extensions.key_constructor.bits import KeyBitBase
from rest_framework_extensions.key_constructor.constructors import KeyConstructor


class _ConstanceTTLCacheResponse(CacheResponse):
    # Reads REST_API_TTL from constance per request instead of at decoration time.
    # Why: with the database constance backend, evaluating config.REST_API_TTL at
    # import time hits the constance table before migrations can be applied,
    # breaking bootstrap (URL resolver runs during `manage.py check`).
    def __init__(
        self,
        key_func: Any = None,
        cache: str | None = None,
        cache_errors: bool | None = None,
    ) -> None:
        super().__init__(timeout=0, key_func=key_func, cache=cache, cache_errors=cache_errors)

    def calculate_timeout(self, view_instance: Any, **_: Any) -> int:
        return config.REST_API_TTL


cached_response = _ConstanceTTLCacheResponse


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


P = ParamSpec("P")


def etag_decorator(
    key_constructor_class: "type[KeyConstructor] | type", compare_etags: bool = True, safe_only: bool = True
) -> Callable[[Callable[P, Response]], Callable[P, Response]]:
    """Decorate ViewSet methods.

    Computes ETag from a KeyConstructor and:
    - For GET/HEAD: returns 304 when If-None-Match matches (weak compare).
    - Otherwise: sets ETag header on the response.
    """

    def inner(function: Callable[P, Response]) -> Callable[P, Response]:
        @functools.wraps(function)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> Response:
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


def get_or_create_cache_key(key: str, default: Any = 1) -> Any:
    """Get value from cache by key or create it with default value."""
    return cache.get_or_set(key, default, timeout=config.REST_API_TTL)


def increment_cache_key(key: str) -> int:
    """Increment a numeric cache key, creating it if it doesn't exist."""
    try:
        val = cache.incr(key)
        cache.expire(key, timeout=config.REST_API_TTL)
        return val
    except ValueError:
        cache.set(key, 1, timeout=config.REST_API_TTL)
        return 1


def business_area_and_program_version_key(
    business_area_slug: Any, program_code: Any, specific_view_cache_key: str
) -> str:
    """Build the version key read by `BusinessAreaAndProgramKeyBitMixin`."""
    business_area_version = get_or_create_cache_key(f"{business_area_slug}:version", 1)
    return f"{business_area_slug}:{business_area_version}:{program_code}:{specific_view_cache_key}"


def increment_business_area_and_program_version(
    business_area_slug: Any, program_code: Any, specific_view_cache_key: str
) -> None:
    """Invalidate a business-area+program scoped list cache."""
    version_key = business_area_and_program_version_key(business_area_slug, program_code, specific_view_cache_key)
    increment_cache_key(version_key)


class BusinessAreaVersionKeyBit(KeyBitBase):
    def get_data(  # noqa: PLR0913 – override of base method signature
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


class RendererKeyBit(KeyBitBase):
    """Key bit that includes renderer class information in cache keys."""

    def get_data(  # noqa: PLR0913 – override of base method signature
        self,
        params: Any,
        view_instance: Any,
        view_method: Any,
        request: Any,
        args: tuple,
        kwargs: dict,
    ) -> str:
        if hasattr(request, "accepted_renderer") and request.accepted_renderer:
            return request.accepted_renderer.__class__.__name__

        return "JSONRenderer"  # pragma: no cover


class KeyConstructorMixin(KeyConstructor):
    business_area_version = BusinessAreaVersionKeyBit()
    unique_method_id = bits.UniqueMethodIdKeyBit()
    querystring = bits.QueryParamsKeyBit()
    params = bits.KwargsKeyBit()
    pagination = bits.PaginationKeyBit()
    renderer = RendererKeyBit()


class BusinessAreaKeyBitMixin(KeyBitBase):
    specific_view_cache_key = ""

    def get_data(  # noqa: PLR0913 – override of base method signature
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

    def get_data(  # noqa: PLR0913 – override of base method signature
        self,
        params: Any,
        view_instance: Any,
        view_method: Any,
        request: Any,
        args: tuple,
        kwargs: dict,
    ) -> str:
        version_key = business_area_and_program_version_key(
            kwargs.get("business_area_slug"), kwargs.get("program_code"), self.specific_view_cache_key
        )
        version = get_or_create_cache_key(version_key, 1)
        return str(version)


class AreaLimitKeyBit(KeyBitBase):
    def get_data(  # noqa: PLR0913 – override of base method signature
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
