from hct_mis_api.api.utils import EncodedIdSerializerMixin
from hct_mis_api.apps.household.models import Individual


class IndividualSmallSerializer(EncodedIdSerializerMixin):
    class Meta:
        model = Individual
        fields = (
            "id",
            "unicef_id",
        )
