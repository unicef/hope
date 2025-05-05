from typing import Any, Dict

from rest_framework import serializers

from hct_mis_api.apps.account.api.serializers import UserSerializer, PartnerSerializer
from hct_mis_api.apps.core.api.mixins import AdminUrlSerializerMixin
from hct_mis_api.apps.geo.api.serializers import AreaListSerializer
from hct_mis_api.apps.grievance.models import GrievanceTicket, GrievanceDocument, TicketNote
from hct_mis_api.apps.household.api.serializers.individual import (
    HouseholdSimpleSerializer,
    LinkedGrievanceTicketSerializer, IndividualSimpleSerializer,
)
from hct_mis_api.apps.household.models import (
    Household,
    Individual,
)
from hct_mis_api.apps.program.api.serializers import ProgramSimpleSerializer


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
        model = Household
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
        return ProgramSimpleSerializer(obj.programs.order_by("created_at").all(), many=True).data

    def get_related_tickets(self, obj: GrievanceTicket) -> Dict:
        return GrievanceTicketSimpleSerializer(obj._related_tickets.order_by("created_at").all(), many=True).data

class GrievanceTicketDetailSerializer(AdminUrlSerializerMixin, GrievanceTicketListSerializer):
    partner = PartnerSerializer()
    postpone_deduplication = serializers.BooleanField(source="business_area.postpone_deduplication")
    individual = IndividualSimpleSerializer(source="ticket_details.individual", allow_null=True)
    payment_record = serializers.SerializerMethodField()  # TODO
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

    def get_linked_tickets(self, obj: GrievanceTicket) -> Dict:
        return GrievanceTicketSimpleSerializer(obj._linked_tickets.order_by("created_at").all(), many=True).data

    def get_existing_tickets(self, obj: GrievanceTicket) -> Dict:
        return GrievanceTicketSimpleSerializer(obj._existing_tickets.order_by("created_at").all(), many=True).data

    def get_documentation(self, obj: GrievanceTicket) -> Dict:
        return GrievanceDocumentSerializer(obj.support_documents.order_by("created_at").all(), many=True).data
