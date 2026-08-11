from collections.abc import Mapping
from copy import deepcopy
from datetime import date
from typing import Any

from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
from django.core.files.storage import default_storage
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from rest_framework.utils.serializer_helpers import ReturnDict

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
from hope.apps.grievance.services.needs_adjudication_ticket_services import (
    can_close_as_unique,
    find_open_unique_identifiers_ticket_for_individual,
)
from hope.apps.household.api.serializers.household import HouseholdForTicketSerializer
from hope.apps.household.api.serializers.individual import (
    AccountSerializer,
    HouseholdSimpleSerializer,
    IndividualForTicketSerializer,
    IndividualRoleInHouseholdSerializer,
)
from hope.apps.household.const import HEAD
from hope.apps.payment.api.serializers import PaymentVerificationSerializer
from hope.apps.sanction_list.api.serializers import SanctionListIndividualSerializer
from hope.models import BusinessArea, Household, Individual


class HouseholdDataUpdateTicketDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketHouseholdDataUpdateDetails
        fields = (
            "id",
            "household_data",
        )


class IndividualDataUpdateTicketDetailsSerializer(serializers.ModelSerializer):
    individual_data = serializers.SerializerMethodField()
    linked_needs_adjudication_ticket_id = serializers.SerializerMethodField()

    class Meta:
        model = TicketIndividualDataUpdateDetails
        fields = (
            "id",
            "individual_data",
            "role_reassign_data",
            "linked_needs_adjudication_ticket_id",
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

    def get_linked_needs_adjudication_ticket_id(self, obj: TicketIndividualDataUpdateDetails) -> str | None:
        linked = find_open_unique_identifiers_ticket_for_individual(obj.individual)
        return str(linked.ticket_id) if linked else None


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
        individual = Individual.all_objects.filter(id=obj.get("hit_id")).first()
        return str(individual.unicef_id) if individual else ""

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


def can_view_biometric_results(context: Mapping[str, Any]) -> bool:
    request = context["request"]
    business_area = BusinessArea.objects.filter(slug=request.parser_context["kwargs"]["business_area_slug"]).first()
    return request.user.has_perm(Permissions.GRIEVANCES_VIEW_BIOMETRIC_RESULTS.value, business_area)


def find_score(hits: list[dict] | None, individual_id: str) -> float | None:
    for hit in hits or []:
        if str(hit.get("hit_id") or "") == individual_id and hit.get("score") is not None:
            return float(hit["score"])
    return None


class TicketNeedsAdjudicationDetailsExtraDataSerializer(serializers.Serializer):
    golden_records = DeduplicationResultSerializer(many=True)
    possible_duplicate = DeduplicationResultSerializer(many=True)
    dedup_engine_similarity_pair = serializers.SerializerMethodField()

    def get_dedup_engine_similarity_pair(self, obj: Any) -> dict:
        if self.context["na_can_view_biometric_results"]:
            return DeduplicationEngineSimilarityPairSerializer(obj.get("dedup_engine_similarity_pair")).data
        return {}


class NaRoleHouseholdSerializer(serializers.ModelSerializer):
    active_individuals_count = serializers.IntegerField(source="active_individuals.count", read_only=True)

    class Meta:
        model = Household
        fields = ("id", "unicef_id", "withdrawn", "active_individuals_count")


class NaRoleInHouseholdSerializer(serializers.Serializer):
    role = serializers.CharField()
    household = NaRoleHouseholdSerializer()


class IndividualForNeedsAdjudicationSerializer(IndividualForTicketSerializer):
    household = HouseholdForTicketSerializer()  # type: ignore[assignment]
    role = serializers.SerializerMethodField()
    roles_in_households = IndividualRoleInHouseholdSerializer(source="households_and_roles", many=True)

    class Meta:
        model = Individual
        fields = (
            "id",
            "unicef_id",
            "household",
            "full_name",
            "birth_date",
            "last_registration_date",
            "sex",
            "deduplication_golden_record_results",
            "duplicate",
            "documents",
            "program_code",
            "role",
            "roles_in_households",
        )

    def get_role(self, obj: Individual) -> str | None:
        role = obj.households_and_roles.filter(household=obj.household).first()
        return role.role if role else None


class IndividualForNaComparisonSerializer(IndividualForTicketSerializer):
    roles_in_households = serializers.SerializerMethodField()
    accounts = serializers.SerializerMethodField()
    similarity_score = serializers.SerializerMethodField()

    class Meta:
        model = Individual
        fields = (
            "id",
            "unicef_id",
            "household",
            "full_name",
            "given_name",
            "family_name",
            "phone_no",
            "birth_date",
            "last_registration_date",
            "sex",
            "deduplication_golden_record_results",
            "duplicate",
            "documents",
            "accounts",
            "program",
            "program_code",
            "roles_in_households",
            "similarity_score",
        )

    @extend_schema_field(AccountSerializer(many=True))
    def get_accounts(self, obj: Individual) -> ReturnDict:
        if self.context["request"].user.has_perm(
            Permissions.POPULATION_VIEW_INDIVIDUAL_DELIVERY_MECHANISMS_SECTION.value,
            obj.program,
        ):
            queryset = obj.accounts(manager="all_objects").all()
        else:
            queryset = obj.accounts.none()
        return AccountSerializer(queryset, many=True).data

    @extend_schema_field(NaRoleInHouseholdSerializer(many=True))
    def get_roles_in_households(self, obj: Individual) -> list[dict]:
        roles = NaRoleInHouseholdSerializer(obj.households_and_roles.all(), many=True)
        data = list(roles.data)
        if obj.is_head():
            data.append({"role": HEAD, "household": NaRoleHouseholdSerializer(obj.household).data})
        return data

    def get_similarity_score(self, obj: Individual) -> float | None:
        """Score of this individual against the ticket's golden record; None on the golden record itself.

        Biometric tickets store one engine score for the pair; the other types store one hit per duplicate
        in the golden record's deduplication results.
        """
        ticket_details: TicketNeedsAdjudicationDetails | None = self.context.get("na_ticket_details")
        individual_id = str(obj.id)
        if ticket_details is None or individual_id == str(ticket_details.golden_records_individual_id):
            return None

        extra_data = ticket_details.extra_data or {}
        pair = extra_data.get("dedup_engine_similarity_pair") or {}
        if self.context.get("na_can_view_biometric_results") and pair.get("similarity_score") is not None:
            pair_ids = {str((pair.get(side) or {}).get("id") or "") for side in ("individual1", "individual2")}
            if individual_id in pair_ids:
                return float(pair["similarity_score"])

        return find_score(extra_data.get("golden_records"), individual_id)


class NeedsAdjudicationTicketDetailsSerializer(serializers.ModelSerializer):
    has_duplicated_document = serializers.BooleanField(read_only=True)
    can_close_as_unique = serializers.SerializerMethodField()
    golden_records_individual = IndividualForNaComparisonSerializer()
    extra_data = serializers.SerializerMethodField()
    possible_duplicate = IndividualForNaComparisonSerializer()
    possible_duplicates = IndividualForNaComparisonSerializer(many=True)
    selected_duplicates = IndividualForNeedsAdjudicationSerializer(source="selected_individuals", many=True)
    selected_individual = IndividualForTicketSerializer()
    selected_distinct = IndividualForTicketSerializer(many=True)

    class Meta:
        model = TicketNeedsAdjudicationDetails
        fields = (
            "id",
            "has_duplicated_document",
            "can_close_as_unique",
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

    def to_representation(self, instance: TicketNeedsAdjudicationDetails) -> dict:
        self._context = {
            **self.context,
            "na_ticket_details": instance,
            "na_can_view_biometric_results": can_view_biometric_results(self.context),
        }
        return super().to_representation(instance)

    def get_can_close_as_unique(self, obj: TicketNeedsAdjudicationDetails) -> bool:
        return can_close_as_unique(obj)

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
