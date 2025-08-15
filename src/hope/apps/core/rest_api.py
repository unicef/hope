import logging
from typing import TYPE_CHECKING

from django.core.cache import cache

from rest_framework.decorators import api_view
from rest_framework.response import Response

from hope.apps.core.api.serializers import FieldAttributeSerializer
from hope.apps.core.utils import get_fields_attr_generators, sort_by_attr

if TYPE_CHECKING:
    from rest_framework.request import Request


logger = logging.getLogger(__name__)


# Not used in the app
@api_view()
def all_fields_attributes(request: "Request") -> "Response":
    """Return the list of FieldAttribute."""
    business_area_slug = request.data.get("business_area_slug")

    records = cache.get(business_area_slug)
    if records:
        return Response(records)

    records = sort_by_attr(get_fields_attr_generators(True, business_area_slug), "label.English(EN)")
    serializer = FieldAttributeSerializer(records, many=True)
    data = serializer.data

    cache.set(business_area_slug, data)
    return Response(data)
