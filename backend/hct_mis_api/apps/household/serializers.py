from rest_framework import serializers

from hct_mis_api.apps.registration_datahub.models import ImportedIndividual
from hct_mis_api.apps.payment.models import PaymentRecord
from hct_mis_api.apps.household.models import Individual, Household


class IndividualStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Individual
        fields = ("status",)

    status = serializers.SerializerMethodField()

    def get_status(self, individual):
        if PaymentRecord.objects.filter(household__head_of_household=individual).exists():
            return "paid"

        if False:  # TODO
            return "sent to cash assist"

        if False:  # TODO
            return "targeted"

        if False:  # TODO
            return "merged to population"

        if ImportedIndividual.objects.filter(individual_id=individual.id).exists():
            return "imported"

        return "not imported"

class HouseholdStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Household
        fields = "__all__"  # TODO