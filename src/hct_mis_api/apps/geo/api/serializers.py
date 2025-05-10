from hct_mis_api.api.utils import EncodedIdSerializerMixin
from hct_mis_api.apps.geo.models import Area


class AreaListSerializer(EncodedIdSerializerMixin):
    class Meta:
        model = Area
        fields = ("id", "name", "p_code", "area_type")
