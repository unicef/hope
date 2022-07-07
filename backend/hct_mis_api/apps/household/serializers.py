from rest_framework import serializers

from hct_mis_api.apps.household.models import Individual


class IndividualSerializer(serializers.ModelSerializer):
    class Meta:
        model = Individual
        fields = '__all__'  # TODO