from rest_framework import serializers

from hct_mis_api.apps.account.api.fields import Base64ModelField
from hct_mis_api.apps.household.models import Individual


class IndividualSmallSerializer(serializers.ModelSerializer):
    id = Base64ModelField(model_name="Individual")

    class Meta:
        model = Individual
        fields = (
            "id",
            "unicef_id",
        )
