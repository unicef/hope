from hct_mis_api.api.utils import EncodedIdSerializerMixin
from hct_mis_api.apps.steficon.models import Rule


class RuleSerializer(EncodedIdSerializerMixin):
    class Meta:
        model = Rule
        fields = (
            "id",
            "name",
            "description",
            "type",
        )
