from rest_framework import serializers

from hct_mis_api.apps.household.models import Individual, Household


class IndividualStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Individual
        fields = ("status",)

    status = serializers.SerializerMethodField()

    def get_status(self, obj):
        return "hello"


class HouseholdStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Household
        fields = "__all__"  # TODO