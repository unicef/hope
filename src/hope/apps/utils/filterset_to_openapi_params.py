from django_filters import (
    BooleanFilter,
    CharFilter,
    DateFilter,
    DateTimeFilter,
    NumberFilter,
    UUIDFilter,
)
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter

FILTER_TYPE_MAPPING = {
    CharFilter: OpenApiTypes.STR,
    NumberFilter: OpenApiTypes.FLOAT,
    BooleanFilter: OpenApiTypes.BOOL,
    UUIDFilter: OpenApiTypes.UUID,
    DateFilter: OpenApiTypes.DATE,
    DateTimeFilter: OpenApiTypes.DATETIME,
}


def filterset_to_openapi_params(filterset_class):
    params = []

    for name, filter_field in filterset_class.base_filters.items():
        openapi_type = OpenApiTypes.STR  # by default let's use string
        for filter_class, schema_type in FILTER_TYPE_MAPPING.items():  # pragma no cover
            if isinstance(filter_field, filter_class):
                openapi_type = schema_type
                break

        lookup = getattr(filter_field, "lookup_expr", "exact")

        description = f"Filter by {name.replace('_', ' ')}"
        if lookup != "exact":
            description += f" (lookup: {lookup})"

        params.append(
            OpenApiParameter(
                name=name,
                type=openapi_type,
                location=OpenApiParameter.QUERY,
                required=filter_field.extra.get("required", False),
                description=description,
            )
        )
    return params
