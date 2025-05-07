from typing import Any, Dict, Optional

from rest_framework import serializers
from datetime import date

from hct_mis_api.apps.account.api.serializers import UserSerializer, PartnerSerializer
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.api.mixins import AdminUrlSerializerMixin
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.geo.api.serializers import AreaListSerializer
from hct_mis_api.apps.grievance.models import GrievanceTicket, GrievanceDocument, TicketNote, \
    TicketHouseholdDataUpdateDetails, TicketIndividualDataUpdateDetails, TicketAddIndividualDetails, \
    TicketDeleteIndividualDetails, TicketDeleteHouseholdDetails, TicketSystemFlaggingDetails, \
    TicketPaymentVerificationDetails, TicketNeedsAdjudicationDetails
from hct_mis_api.apps.household.api.serializers.individual import (
    HouseholdSimpleSerializer,
    LinkedGrievanceTicketSerializer, IndividualSimpleSerializer, IndividualForTicketSerializer,
)
from hct_mis_api.apps.household.models import (
    Household,
    Individual,
)
from hct_mis_api.apps.payment.api.serializers import PaymentVerificationSerializer
from hct_mis_api.apps.payment.services.payment_gateway import PaymentSerializer
from hct_mis_api.apps.program.api.serializers import ProgramSmallSerializer
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.registration_data.nodes import DeduplicationEngineSimilarityPairNode
from hct_mis_api.apps.sanction_list.api.serializers import SanctionListIndividualSerializer
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta

class GrievanceTicketSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = GrievanceTicket
        fields = (
            "id",
            "unicef_id",
        )

class GrievanceDocumentSerializer(serializers.ModelSerializer):
    file_name = serializers.SerializerMethodField()
    file_path = serializers.SerializerMethodField()
    created_by = UserSerializer()

    class Meta:
        model = GrievanceDocument
        fields = (
            "id",
            "name",
            "created_by",
            "created_at",
            "updated_at",
            "file_size",
            "content_type",
            "file_path",
            "file_name",
        )

    def get_file_name(self, obj: GrievanceDocument) -> str:
        return obj.file_name

    def get_file_path(self, obj: GrievanceDocument) -> str:
        return obj.file_path

class TicketNoteSerializer(serializers.ModelSerializer):
    created_by = UserSerializer()

    class Meta:
        model = TicketNote
        fields = (
            "id",
            "description",
            "created_by",
            "created_at",
            "updated_at",
        )

class GrievanceTicketListSerializer(serializers.ModelSerializer):
    programs = serializers.SerializerMethodField()
    household = HouseholdSimpleSerializer(source="ticket_details.household", allow_null=True)
    admin = serializers.CharField(source="admin2.name", default="")
    admin2 = AreaListSerializer()
    assigned_to = UserSerializer()
    created_by = UserSerializer()
    user_modified = UserSerializer()
    related_tickets = serializers.SerializerMethodField()

    class Meta:
        model = GrievanceTicket
        fields = (
            "id",
            "unicef_id",
            "status",
            "programs",
            "household",
            "admin",
            "admin2",
            "assigned_to",
            "created_by",
            "user_modified",
            "category",
            "issue_type",
            "priority",
            "urgency",
            "created_at",
            "updated_at",
            "total_days",
            "target_id",
            "related_tickets",
        )

    def get_programs(self, obj: GrievanceTicket) -> Dict:
        return ProgramSmallSerializer(obj.programs.order_by("created_at").all(), many=True).data

    def get_related_tickets(self, obj: GrievanceTicket) -> Dict:
        return GrievanceTicketSimpleSerializer(obj._related_tickets.order_by("created_at").all(), many=True).data


class HouseholdDataUpdateTicketDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketHouseholdDataUpdateDetails
        fields = (
            "id",
            "household_data",
        )


class IndividualDataUpdateTicketDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketIndividualDataUpdateDetails
        fields = (
            "id",
            "individual_data",
            "role_reassign_data",
        )


class AddIndividualTicketDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketAddIndividualDetails
        fields = (
            "id",
            "approve_status"
            "individual_data",
        )


class TicketDeleteIndividualDetails(serializers.ModelSerializer):
    class Meta:
        model = TicketDeleteIndividualDetails
        fields = (
            "id",
            "approve_status"
            "role_reassign_data",
        )


class DeleteHouseholdTicketDetailSerializer(serializers.ModelSerializer):
    reason_household = HouseholdSimpleSerializer()
    class Meta:
        model = TicketDeleteHouseholdDetails
        fields = (
            "id",
            "approve_status"
            "role_reassign_data",
            "reason_household",
        )

class SystemFlaggingTicketDetailSerializer(serializers.ModelSerializer):
    golden_records_individual = IndividualForTicketSerializer()
    sanction_list_individual = SanctionListIndividualSerializer()
    class Meta:
        model = TicketSystemFlaggingDetails
        fields = (
            "id",
            "approve_status"
            "role_reassign_data",
            "golden_records_individual",
            "sanction_list_individual",
        )

class PaymentVerificationTicketDetailSerializer(serializers.ModelSerializer):
    has_multiple_payment_verifications = serializers.SerializerMethodField()
    payment_verification = PaymentVerificationSerializer()
    class Meta:
        model = TicketPaymentVerificationDetails
        fields = (
            "id",
            "approve_status"
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

    def get_age(self, obj: Any) -> Optional[int]:
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
    similarity_score = serializers.FloatField()
    age = serializers.IntegerField()
    location = serializers.CharField()

    def get_photo(self, obj: Any) -> Optional[str]:
        individual = Individual.all_objects.filter(id=obj.get("id")).first()
        return individual.photo.url if individual and individual.photo else None


class DeduplicationEngineSimilarityPairSerializer(serializers.Serializer):
    individual1 = DeduplicationEngineSimilarityPairIndividualSerializer()
    individual2 = DeduplicationEngineSimilarityPairIndividualSerializer()
    similarity_score = serializers.CharField()
    status_code = serializers.CharField()

class TicketNeedsAdjudicationDetailsExtraDataSerializer(serializers.Serializer):
    golden_records = DeduplicationResultSerializer(many=True)
    possible_duplicate = DeduplicationResultSerializer(many=True)
    dedup_engine_similarity_pair = serializers.SerializerMethodField()

    def get_dedup_engine_similarity_pair(self, obj: Any) -> Dict:
        business_area_slug = self.context["request"].parser_context["kwargs"]["business_area_slug"]
        if program_slug := self.context["request"].parser_context["kwargs"].get("program_slug"):
            scope = Program.objects.filter(slug=program_slug, business_area__slug=business_area_slug).first()
        else:
            scope = BusinessArea.objects.filter(slug=business_area_slug).first()
        if self.context["request"].user.has_perm(
            Permissions.GRIEVANCES_VIEW_BIOMETRIC_RESULTS.value, scope
        ):
            return DeduplicationEngineSimilarityPairSerializer(obj.get("dedup_engine_similarity_pair")).data
        return {}

class NeedsAdjudicationTicketDetailSerializer(serializers.ModelSerializer):
    has_duplicated_document = serializers.SerializerMethodField()
    golden_records_individual = IndividualForTicketSerializer()
    extra_data = serializers.SerializerMethodField()
    possible_duplicates = IndividualForTicketSerializer(many=True)
    selected_duplicates = IndividualForTicketSerializer(source="selected_individuals", many=True)
    selected_distinct = IndividualForTicketSerializer(many=True)

    class Meta:
        model = TicketNeedsAdjudicationDetails
        fields = (
            "id",
            "has_duplicated_document"
            "golden_records_individual",
            "extra_data",
            "possible_duplicates",
            "selected_duplicates",
            "selected_distinct",
            "is_multiple_duplicates_version",
            "role_reassign_data",
        )

    def get_has_duplicated_document(self, obj: TicketNeedsAdjudicationDetails) -> bool:
        return obj.has_duplicated_document

    def get_extra_data(self, obj: TicketSystemFlaggingDetails) -> Dict:
        return TicketNeedsAdjudicationDetailsExtraDataSerializer(
            {
                "golden_records": obj.extra_data.get("golden_records"),
                "possible_duplicate": obj.extra_data.get("possible_duplicate"),
                "dedup_engine_similarity_pair": obj.extra_data.get("dedup_engine_similarity_pair"),
            }
        ).data


class GrievanceTicketDetailSerializer(AdminUrlSerializerMixin, GrievanceTicketListSerializer):
    partner = PartnerSerializer()
    postpone_deduplication = serializers.BooleanField(source="business_area.postpone_deduplication")
    individual = IndividualSimpleSerializer(source="ticket_details.individual", allow_null=True)
    payment_record = serializers.SerializerMethodField()
    # TODO: all the ticket_detail types
    linked_tickets = serializers.SerializerMethodField()
    existing_tickets = serializers.SerializerMethodField()
    documentation = serializers.SerializerMethodField()
    ticket_notes = TicketNoteSerializer(many=True)

    class Meta(GrievanceTicketListSerializer.Meta):
        fields = GrievanceTicketListSerializer.Meta.fields + (  # type: ignore
            "admin_url",
            "consent",
            "partner",
            "postpone_deduplication",
            "description",
            "language",
            "area",
            "individual",
            "payment_record",
            "linked_tickets",
            "existing_tickets",
            "comments",
            "documentation",
            "ticket_notes",
        )

    def get_payment_record(self, obj: GrievanceTicket) -> Dict:
        payment_verification = getattr(obj.ticket_details, "payment_verification", None)
        if payment_verification:
            payment_record = getattr(payment_verification, "payment", None)
        else:
            payment_record = getattr(obj.ticket_details, "payment", None)
        return PaymentSerializer(payment_record).data

    def get_linked_tickets(self, obj: GrievanceTicket) -> Dict:
        return GrievanceTicketSimpleSerializer(obj._linked_tickets.order_by("created_at").all(), many=True).data

    def get_existing_tickets(self, obj: GrievanceTicket) -> Dict:
        return GrievanceTicketSimpleSerializer(obj._existing_tickets.order_by("created_at").all(), many=True).data

    def get_documentation(self, obj: GrievanceTicket) -> Dict:
        return GrievanceDocumentSerializer(obj.support_documents.order_by("created_at").all(), many=True).data
