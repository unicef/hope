from hct_mis_api.apps.registration_datahub.models import ImportedHousehold
from rest_framework import serializers
from django.utils import timezone

from hct_mis_api.apps.registration_datahub.models import ImportedIndividual
from hct_mis_api.apps.payment.models import PaymentRecord
from hct_mis_api.apps.household.models import Individual, Household


def get_household_status(household):
    payment_records = PaymentRecord.objects.filter(household=household)
    if payment_records.exists():
        return "paid", payment_records.first().updated_at

    if False:  # TODO
        return "sent to cash assist", timezone.now()

    if False:  # TODO
        return "targeted", timezone.now()

    if False:  # TODO
        return "merged to population", timezone.now()

    imported_households = ImportedHousehold.objects.filter(head_of_household__individual_id=household.head_of_household.id)
    if imported_households.exists():
        return "imported", imported_households.first().updated_at

    return "not imported", timezone.now()


def get_individual_info(individual, household, tax_id):
    # TODO
    role = "collector"
    relationship = "son"
    return {
        "role": role,
        "relationship": relationship,
        "tax_id": tax_id,
    }


def get_household_info(household, individual=None, tax_id=None):
    status, date = get_household_status(household)
    output = {
        "status": status,
        "date": date
    }
    if individual:
        output["individual"] = get_individual_info(individual, household, tax_id=tax_id)
    return output


class IndividualStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Individual
        fields = ("info",)

    info = serializers.SerializerMethodField()

    def get_info(self, individual):
        tax_id = self.context["tax_id"]
        return get_household_info(household=individual.household, individual=individual, tax_id=tax_id)


class HouseholdStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Household
        fields = ("info",)

    info = serializers.SerializerMethodField()

    def get_info(self, household):
        return get_household_info(household=household)