import django_filters
from django_filters import FilterSet
from drf_spectacular.types import OpenApiTypes

from hope.apps.utils.filterset_to_openapi_params import filterset_to_openapi_params


def test_filterset_to_openapi_params_default_string():
    class DummyFilterSet(FilterSet):
        name = django_filters.CharFilter()

    params = filterset_to_openapi_params(DummyFilterSet)
    assert len(params) == 1
    assert params[0].name == "name"
    assert params[0].type == OpenApiTypes.STR
    assert "lookup" not in params[0].description
    assert params[0].required is False


def test_filterset_to_openapi_params_number_type():
    class DummyNumberFilterSet(FilterSet):
        age = django_filters.NumberFilter()

    params = filterset_to_openapi_params(DummyNumberFilterSet)
    assert params[0].type == OpenApiTypes.FLOAT


def test_filterset_lookup_description():
    class DummyLookupFilterSet(FilterSet):
        name = django_filters.CharFilter(lookup_expr="icontains")

    params = filterset_to_openapi_params(DummyLookupFilterSet)
    assert "(lookup: icontains)" in params[0].description


def test_filterset_required_flag():
    class DummyRequiredFilterSet(FilterSet):
        name = django_filters.CharFilter(required=True)

    params = filterset_to_openapi_params(DummyRequiredFilterSet)
    assert params[0].required is True
