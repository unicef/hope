from copy import deepcopy
from datetime import date
from typing import Any

from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
from django.core.files.storage import default_storage
from rest_framework import serializers

from hope.apps.account.permissions import Permissions
from hope.apps.grievance.models import (
    TicketAddIndividualDetails,
    TicketDeleteHouseholdDetails,
    TicketDeleteIndividualDetails,
    TicketHouseholdDataUpdateDetails,
    TicketIndividualDataUpdateDetails,
    TicketNeedsAdjudicationDetails,
    TicketPaymentVerificationDetails,
    TicketSystemFlaggingDetails,
)
from hope.apps.household.api.serializers.individual import (
    HouseholdSimpleSerializer,
    IndividualForTicketSerializer,
)
from hope.apps.payment.api.serializers import PaymentVerificationSerializer
from hope.apps.sanction_list.api.serializers import SanctionListIndividualSerializer
from hope.models import BusinessArea, Individual, Program


class HouseholdDataUpdateTicketDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketHouseholdDataUpdateDetails
        fields = (
            "id",
            "household_data",
        )


class IndividualDataUpdateTicketDetailsSerializer(serializers.ModelSerializer):
    individual_data = serializers.SerializerMethodField()

    class Meta:
        model = TicketIndividualDataUpdateDetails
        fields = (
            "id",
            "individual_data",
            "role_reassign_data",
        )

    def get_individual_data(self, obj: TicketIndividualDataUpdateDetails) -> dict | None:
        data = obj.individual_data
        if not data:
            return data
        data = deepcopy(data)
        photo_data = data.get("photo")
        if isinstance(photo_data, dict):
            if photo_data.get("value"):
                photo_data["value"] = default_storage.url(photo_data["value"])
            if photo_data.get("previous_value"):
                photo_data["previous_value"] = default_storage.url(photo_data["previous_value"])
        return data


class AddIndividualTicketDetailsSerializer(serializers.ModelSerializer):
    individual_data = serializers.SerializerMethodField()

    class Meta:
        model = TicketAddIndividualDetails
        fields = (
            "id",
            "approve_status",
            "individual_data",
        )

    def get_individual_data(self, obj: TicketAddIndividualDetails) -> dict | None:
        data = obj.individual_data
        if not data:
            return data
        data = deepcopy(data)
        if data.get("photo"):
            data["photo"] = default_storage.url(data["photo"])
        return data


class DeleteIndividualTicketDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketDeleteIndividualDetails
        fields = (
            "id",
            "approve_status",
            "role_reassign_data",
        )


class DeleteHouseholdTicketDetailsSerializer(serializers.ModelSerializer):
    reason_household = HouseholdSimpleSerializer()

    class Meta:
        model = TicketDeleteHouseholdDetails
        fields = (
            "id",
            "approve_status",
            "role_reassign_data",
            "reason_household",
        )


class SystemFlaggingTicketDetailsSerializer(serializers.ModelSerializer):
    golden_records_individual = IndividualForTicketSerializer()
    sanction_list_individual = SanctionListIndividualSerializer()

    class Meta:
        model = TicketSystemFlaggingDetails
        fields = (
            "id",
            "approve_status",
            "role_reassign_data",
            "golden_records_individual",
            "sanction_list_individual",
        )


class PaymentVerificationTicketDetailsSerializer(serializers.ModelSerializer):
    has_multiple_payment_verifications = serializers.SerializerMethodField()
    payment_verification = PaymentVerificationSerializer()

    class Meta:
        model = TicketPaymentVerificationDetails
        fields = (
            "id",
            "approve_status",
            "new_status",
            "old_received_amount",
            "new_received_amount",
            "payment_verification_status",
            "has_multiple_payment_verifications",
            "payment_verification",
        )

    def get_has_multiple_payment_verifications(self, obj: TicketPaymentVerificationDetails) -> bool:
        return obj.has_multiple_payment_verifications


class DeduplicationResultSerializer(serializers.Serializer):
    unicef_id = serializers.SerializerMethodField()
    full_name = serializers.CharField()
    hit_id = serializers.CharField()
    score = serializers.FloatField()
    proximity_to_score = serializers.FloatField()
    location = serializers.CharField(default="Not provided")
    age = serializers.SerializerMethodField()
    duplicate = serializers.BooleanField(default=False)
    distinct = serializers.BooleanField(default=False)

    def get_unicef_id(self, obj: Any) -> str:
        individual = Individual.all_objects.get(id=obj.get("hit_id"))
        return str(individual.unicef_id)

    def get_age(self, obj: Any) -> int | None:
        date_of_birth = obj.get("dob")
        if date_of_birth:
            today = date.today()
            return relativedelta(today, parse(date_of_birth)).years
        return None


class DeduplicationEngineSimilarityPairIndividualSerializer(serializers.Serializer):
    id = serializers.CharField()
    photo = serializers.SerializerMethodField()
    full_name = serializers.CharField()
    unicef_id = serializers.CharField()

    def get_photo(self, obj: Any) -> str | None:
        if not (ind_id := obj.get("id")):
            return ""
        individual = Individual.all_objects.filter(id=ind_id).first()
        return individual.photo.url if individual and individual.photo else ""


class DeduplicationEngineSimilarityPairSerializer(serializers.Serializer):
    individual1 = DeduplicationEngineSimilarityPairIndividualSerializer()
    individual2 = DeduplicationEngineSimilarityPairIndividualSerializer()
    similarity_score = serializers.CharField()
    status_code = serializers.CharField()


class TicketNeedsAdjudicationDetailsExtraDataSerializer(serializers.Serializer):
    golden_records = DeduplicationResultSerializer(many=True)
    possible_duplicate = DeduplicationResultSerializer(many=True)
    dedup_engine_similarity_pair = serializers.SerializerMethodField()

    def get_dedup_engine_similarity_pair(self, obj: Any) -> dict:
        business_area_slug = self.context["request"].parser_context["kwargs"]["business_area_slug"]
        if program_slug := self.context["request"].parser_context["kwargs"].get("program_slug"):
            scope = Program.objects.filter(slug=program_slug, business_area__slug=business_area_slug).first()
        else:
            scope = BusinessArea.objects.filter(slug=business_area_slug).first()
        if self.context["request"].user.has_perm(Permissions.GRIEVANCES_VIEW_BIOMETRIC_RESULTS.value, scope):
            return DeduplicationEngineSimilarityPairSerializer(obj.get("dedup_engine_similarity_pair")).data
        return {}


class NeedsAdjudicationTicketDetailsSerializer(serializers.ModelSerializer):
    has_duplicated_document = serializers.SerializerMethodField()
    golden_records_individual = IndividualForTicketSerializer()
    extra_data = serializers.SerializerMethodField()
    possible_duplicate = IndividualForTicketSerializer()
    possible_duplicates = IndividualForTicketSerializer(many=True)
    selected_duplicates = IndividualForTicketSerializer(source="selected_individuals", many=True)
    selected_individual = IndividualForTicketSerializer()
    selected_distinct = IndividualForTicketSerializer(many=True)

    class Meta:
        model = TicketNeedsAdjudicationDetails
        fields = (
            "id",
            "has_duplicated_document",
            "is_multiple_duplicates_version",
            "golden_records_individual",
            "possible_duplicate",
            "possible_duplicates",
            "selected_duplicates",
            "selected_individual",
            "selected_distinct",
            "extra_data",
            "role_reassign_data",
        )

    def get_has_duplicated_document(self, obj: TicketNeedsAdjudicationDetails) -> bool:
        return obj.has_duplicated_document

    def get_extra_data(self, obj: TicketSystemFlaggingDetails) -> dict:
        return TicketNeedsAdjudicationDetailsExtraDataSerializer(
            {
                "golden_records": obj.extra_data.get("golden_records"),
                "possible_duplicate": obj.extra_data.get("possible_duplicate"),
                "dedup_engine_similarity_pair": obj.extra_data.get("dedup_engine_similarity_pair"),
            },
            context=self.context,
        ).data


TICKET_DETAILS_SERIALIZER_MAPPING = {
    TicketHouseholdDataUpdateDetails: HouseholdDataUpdateTicketDetailsSerializer,
    TicketIndividualDataUpdateDetails: IndividualDataUpdateTicketDetailsSerializer,
    TicketAddIndividualDetails: AddIndividualTicketDetailsSerializer,
    TicketDeleteIndividualDetails: DeleteIndividualTicketDetailsSerializer,
    TicketDeleteHouseholdDetails: DeleteHouseholdTicketDetailsSerializer,
    TicketSystemFlaggingDetails: SystemFlaggingTicketDetailsSerializer,
    TicketPaymentVerificationDetails: PaymentVerificationTicketDetailsSerializer,
    TicketNeedsAdjudicationDetails: NeedsAdjudicationTicketDetailsSerializer,
}
