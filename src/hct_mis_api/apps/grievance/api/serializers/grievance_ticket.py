from typing import Any, Dict, List, Optional

from rest_framework import serializers

from hct_mis_api.apps.account.api.serializers import PartnerSerializer, UserSerializer
from hct_mis_api.apps.account.models import Partner, User
from hct_mis_api.apps.accountability.models import Feedback
from hct_mis_api.apps.core.api.mixins import AdminUrlSerializerMixin
from hct_mis_api.apps.core.utils import to_choice_object
from hct_mis_api.apps.geo.api.serializers import AreaListSerializer
from hct_mis_api.apps.geo.models import Area
from hct_mis_api.apps.grievance.api.serializers.ticket_detail import (
    TICKET_DETAILS_SERIALIZER_MAPPING,
)
from hct_mis_api.apps.grievance.constants import PRIORITY_CHOICES, URGENCY_CHOICES
from hct_mis_api.apps.grievance.models import (
    GrievanceDocument,
    GrievanceTicket,
    TicketNote,
)
from hct_mis_api.apps.household.api.serializers.household import (
    HouseholdForTicketSerializer,
)
from hct_mis_api.apps.household.api.serializers.individual import (
    HouseholdSimpleSerializer,
    IndividualSimpleSerializer,
)
from hct_mis_api.apps.household.models import (
    BankAccountInfo,
    Document,
    DocumentType,
    Household,
    Individual,
    IndividualIdentity,
)
from hct_mis_api.apps.payment.api.serializers import PaymentSmallSerializer
from hct_mis_api.apps.payment.models import Payment
from hct_mis_api.apps.program.api.serializers import ProgramSmallSerializer
from hct_mis_api.apps.program.models import Program


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
    related_tickets = serializers.SerializerMethodField()
    total_days = serializers.SerializerMethodField()

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
        return ProgramSmallSerializer(obj.programs, many=True).data

    def get_related_tickets(self, obj: GrievanceTicket) -> Dict:
        return GrievanceTicketSimpleSerializer(obj._related_tickets.all(), many=True).data

    def get_total_days(self, obj: GrievanceTicket) -> Optional[int]:
        return getattr(obj, "total_days", None)


class GrievanceTicketDetailSerializer(AdminUrlSerializerMixin, GrievanceTicketListSerializer):
    partner = PartnerSerializer()
    postpone_deduplication = serializers.BooleanField(source="business_area.postpone_deduplication")
    individual = IndividualSimpleSerializer(source="ticket_details.individual", allow_null=True)
    payment_record = serializers.SerializerMethodField()
    linked_tickets = serializers.SerializerMethodField()
    existing_tickets = serializers.SerializerMethodField()
    documentation = serializers.SerializerMethodField()
    ticket_notes = TicketNoteSerializer(many=True)
    ticket_details = serializers.SerializerMethodField()
    household = HouseholdForTicketSerializer(source="ticket_details.household", allow_null=True)

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
            "ticket_details",
        )

    def get_payment_record(self, obj: GrievanceTicket) -> Optional[Dict]:
        payment_verification = getattr(obj.ticket_details, "payment_verification", None)
        if payment_verification:
            payment_record = getattr(payment_verification, "payment", None)
        else:
            payment_record = getattr(obj.ticket_details, "payment", None)
        return PaymentSmallSerializer(payment_record).data if payment_record else None

    def get_linked_tickets(self, obj: GrievanceTicket) -> Dict:
        return GrievanceTicketSimpleSerializer(obj._linked_tickets.order_by("created_at"), many=True).data

    def get_existing_tickets(self, obj: GrievanceTicket) -> Dict:
        return GrievanceTicketSimpleSerializer(obj._existing_tickets.order_by("created_at"), many=True).data

    def get_documentation(self, obj: GrievanceTicket) -> Dict:
        return GrievanceDocumentSerializer(obj.support_documents.order_by("created_at"), many=True).data

    def get_ticket_details(self, obj: GrievanceTicket) -> Optional[Dict]:
        ticket_details = obj.ticket_details
        serializer = TICKET_DETAILS_SERIALIZER_MAPPING.get(type(ticket_details))
        return serializer(ticket_details, context=self.context).data if serializer else None


class GrievanceChoicesSerializer(serializers.Serializer):
    grievance_ticket_status_choices = serializers.SerializerMethodField()
    grievance_ticket_category_choices = serializers.SerializerMethodField()
    grievance_ticket_manual_category_choices = serializers.SerializerMethodField()
    grievance_ticket_system_category_choices = serializers.SerializerMethodField()
    grievance_ticket_priority_choices = serializers.SerializerMethodField()
    grievance_ticket_urgency_choices = serializers.SerializerMethodField()
    grievance_ticket_issue_type_choices = serializers.SerializerMethodField()
    document_type_choices = serializers.SerializerMethodField()

    def get_document_type_choices(self, *args: Any, **kwargs: Any) -> List[Dict[str, Any]]:
        return [{"name": x.label, "value": x.key} for x in DocumentType.objects.order_by("key")]

    def get_grievance_ticket_status_choices(self, *args: Any, **kwargs: Any) -> List[Dict[str, Any]]:
        return to_choice_object(GrievanceTicket.STATUS_CHOICES)

    def get_grievance_ticket_category_choices(self, info: Any, **kwargs: Any) -> List[Dict[str, Any]]:
        return to_choice_object(GrievanceTicket.CATEGORY_CHOICES)

    def get_grievance_ticket_manual_category_choices(self, info: Any, **kwargs: Any) -> List[Dict[str, Any]]:
        return to_choice_object(GrievanceTicket.CREATE_CATEGORY_CHOICES)

    def get_grievance_ticket_system_category_choices(self, info: Any, **kwargs: Any) -> List[Dict[str, Any]]:
        return to_choice_object(GrievanceTicket.SYSTEM_CATEGORIES)

    def get_grievance_ticket_priority_choices(self, info: Any, **kwargs: Any) -> List[Dict[str, Any]]:
        return to_choice_object(PRIORITY_CHOICES)

    def get_grievance_ticket_urgency_choices(self, info: Any, **kwargs: Any) -> List[Dict[str, Any]]:
        return to_choice_object(URGENCY_CHOICES)

    def get_grievance_ticket_issue_type_choices(self, info: Any, **kwargs: Any) -> List[Dict]:
        categories = dict(GrievanceTicket.CATEGORY_CHOICES)
        return [
            {"category": key, "label": categories[key], "sub_categories": value}
            for (key, value) in GrievanceTicket.ISSUE_TYPES_CHOICES.items()
        ]


class IndividualDocumentSerializer(serializers.Serializer):
    country = serializers.CharField(required=True)
    key = serializers.CharField(required=True)
    number = serializers.CharField(required=True)
    photo = serializers.FileField(use_url=False, required=False)
    photoraw = serializers.FileField(use_url=False, required=False)


class EditIndividualDocumentSerializer(serializers.Serializer):
    id = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(required=True, queryset=Document.objects.all()), required=False
    )
    country = serializers.CharField(required=True)
    key = serializers.CharField(required=True)
    number = serializers.CharField(required=True)
    photo = serializers.FileField(use_url=False, required=False)
    photoraw = serializers.FileField(use_url=False, required=False)


class IndividualIdentitySerializer(serializers.Serializer):
    country = serializers.CharField(required=True)
    partner = serializers.CharField(required=True)
    number = serializers.CharField(required=True)


class EditIndividualIdentitySerializer(serializers.Serializer):
    id = serializers.PrimaryKeyRelatedField(required=True, queryset=IndividualIdentity.objects.all())
    country = serializers.CharField(required=True)
    partner = serializers.CharField(required=True)
    number = serializers.CharField(required=True)


class BankTransferSerializer(serializers.Serializer):
    type = serializers.CharField(required=True)
    bank_name = serializers.CharField(required=True)
    bank_account_number = serializers.CharField(required=True)
    bank_branch_name = serializers.CharField(required=True)
    account_holder_name = serializers.CharField(required=True)


class EditBankTransferSerializer(serializers.Serializer):
    id = serializers.PrimaryKeyRelatedField(required=True, queryset=BankAccountInfo.objects.all())
    type = serializers.CharField(required=True)
    bank_name = serializers.CharField(required=True)
    bank_account_number = serializers.CharField(required=True)
    bank_branch_name = serializers.CharField(required=False)
    account_holder_name = serializers.CharField(required=True)


class HouseholdUpdateDataSerializer(serializers.Serializer):
    admin_area_title = serializers.CharField(required=False)
    status = serializers.CharField(required=False)
    consent = serializers.BooleanField(required=False)
    consent_sharing = serializers.ListField(child=serializers.CharField(), required=False)
    residence_status = serializers.CharField(required=False)
    country_origin = serializers.CharField(required=False)
    country = serializers.CharField(required=False)
    size = serializers.IntegerField(required=False)
    address = serializers.CharField(required=False)
    female_age_group_0_5_count = serializers.IntegerField(required=False)
    female_age_group_6_11_count = serializers.IntegerField(required=False)
    female_age_group_12_17_count = serializers.IntegerField(required=False)
    female_age_group_18_59_count = serializers.IntegerField(required=False)
    female_age_group_60_count = serializers.IntegerField(required=False)
    pregnant_count = serializers.IntegerField(required=False)
    male_age_group_0_5_count = serializers.IntegerField(required=False)
    male_age_group_6_11_count = serializers.IntegerField(required=False)
    male_age_group_12_17_count = serializers.IntegerField(required=False)
    male_age_group_18_59_count = serializers.IntegerField(required=False)
    male_age_group_60_count = serializers.IntegerField(required=False)
    female_age_group_0_5_disabled_count = serializers.IntegerField(required=False)
    female_age_group_6_11_disabled_count = serializers.IntegerField(required=False)
    female_age_group_12_17_disabled_count = serializers.IntegerField(required=False)
    female_age_group_18_59_disabled_count = serializers.IntegerField(required=False)
    female_age_group_60_disabled_count = serializers.IntegerField(required=False)
    male_age_group_0_5_disabled_count = serializers.IntegerField(required=False)
    male_age_group_6_11_disabled_count = serializers.IntegerField(required=False)
    male_age_group_12_17_disabled_count = serializers.IntegerField(required=False)
    male_age_group_18_59_disabled_count = serializers.IntegerField(required=False)
    male_age_group_60_disabled_count = serializers.IntegerField(required=False)
    returnee = serializers.BooleanField(required=False)
    fchild_hoh = serializers.BooleanField(required=False)
    child_hoh = serializers.BooleanField(required=False)
    start = serializers.DateTimeField(required=False)
    end = serializers.DateTimeField(required=False)
    name_enumerator = serializers.CharField(required=False)
    org_enumerator = serializers.CharField(required=False)
    org_name_enumerator = serializers.CharField(required=False)
    village = serializers.CharField(required=False)
    registration_method = serializers.CharField(required=False)
    currency = serializers.CharField(required=False)
    unhcr_id = serializers.CharField(required=False)
    flex_fields = serializers.JSONField(required=False)


class AddIndividualDataSerializer(serializers.Serializer):
    full_name = serializers.CharField(required=True)
    given_name = serializers.CharField(required=False)
    middle_name = serializers.CharField(required=False)
    family_name = serializers.CharField(required=False)
    sex = serializers.CharField(required=True)
    birth_date = serializers.DateField(required=True)
    estimated_birth_date = serializers.BooleanField(required=True)
    marital_status = serializers.CharField(required=False)
    phone_no = serializers.CharField(required=False)
    phone_no_alternative = serializers.CharField(required=False)
    email = serializers.CharField(required=False)
    relationship = serializers.CharField(required=True)
    disability = serializers.CharField(required=False)
    work_status = serializers.CharField(required=False)
    enrolled_in_nutrition_programme = serializers.BooleanField(required=False)
    pregnant = serializers.BooleanField(required=False)
    observed_disability = serializers.ListField(child=serializers.CharField(), required=False)
    seeing_disability = serializers.CharField(required=False)
    hearing_disability = serializers.CharField(required=False)
    physical_disability = serializers.CharField(required=False)
    memory_disability = serializers.CharField(required=False)
    selfcare_disability = serializers.CharField(required=False)
    comms_disability = serializers.CharField(required=False)
    who_answers_phone = serializers.CharField(required=False)
    who_answers_alt_phone = serializers.CharField(required=False)
    role = serializers.CharField(required=True)
    business_area = serializers.CharField(required=False)
    documents = IndividualDocumentSerializer(many=True, required=False)
    identities = IndividualIdentitySerializer(many=True, required=False)
    payment_channels = BankTransferSerializer(many=True, required=False)
    preferred_language = serializers.CharField(required=False)
    flex_fields = serializers.JSONField(required=False)
    payment_delivery_phone_no = serializers.CharField(required=False)
    blockchain_name = serializers.CharField(required=False)
    wallet_address = serializers.CharField(required=False)
    wallet_name = serializers.CharField(required=False)


class IndividualUpdateDataSerializer(serializers.Serializer):
    status = serializers.CharField(required=False)
    full_name = serializers.CharField(required=False)
    given_name = serializers.CharField(required=False)
    middle_name = serializers.CharField(required=False)
    family_name = serializers.CharField(required=False)
    sex = serializers.CharField(required=False)
    birth_date = serializers.DateField(required=False)
    estimated_birth_date = serializers.BooleanField(required=False)
    marital_status = serializers.CharField(required=False)
    phone_no = serializers.CharField(required=False)
    phone_no_alternative = serializers.CharField(required=False)
    email = serializers.CharField(required=False)
    relationship = serializers.CharField(required=False)
    disability = serializers.CharField(required=False)
    work_status = serializers.CharField(required=False)
    enrolled_in_nutrition_programme = serializers.BooleanField(required=False)
    pregnant = serializers.BooleanField(required=False)
    observed_disability = serializers.ListField(child=serializers.CharField(), required=False)
    seeing_disability = serializers.CharField(required=False)
    hearing_disability = serializers.CharField(required=False)
    physical_disability = serializers.CharField(required=False)
    memory_disability = serializers.CharField(required=False)
    selfcare_disability = serializers.CharField(required=False)
    comms_disability = serializers.CharField(required=False)
    who_answers_phone = serializers.CharField(required=False)
    who_answers_alt_phone = serializers.CharField(required=False)
    role = serializers.CharField(required=False)
    documents = IndividualDocumentSerializer(many=True, required=False)
    documents_to_remove = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(required=True, queryset=Document.objects.all()), required=False
    )
    documents_to_edit = EditIndividualDocumentSerializer(many=True, required=False)
    identities = IndividualIdentitySerializer(many=True, required=False)
    identities_to_remove = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(required=True, queryset=IndividualIdentity.objects.all()),
        required=False,
    )
    identities_to_edit = EditIndividualIdentitySerializer(many=True, required=False)
    payment_channels = BankTransferSerializer(many=True, required=False)
    payment_channels_to_edit = EditBankTransferSerializer(many=True, required=False)
    payment_channels_to_remove = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(required=True, queryset=BankAccountInfo.objects.all()), required=False
    )
    preferred_language = serializers.CharField(required=False)
    flex_fields = serializers.JSONField(required=False)
    payment_delivery_phone_no = serializers.CharField(required=False)
    blockchain_name = serializers.CharField(required=False)
    wallet_address = serializers.CharField(required=False)
    wallet_name = serializers.CharField(required=False)
    # people fields
    consent = serializers.CharField(required=False, help_text="People update")
    residence_status = serializers.CharField(required=False, help_text="People update")
    country_origin = serializers.CharField(required=False, help_text="People update")
    country = serializers.CharField(required=False, help_text="People update")
    address = serializers.CharField(required=False, help_text="People update")
    village = serializers.CharField(required=False, help_text="People update")
    currency = serializers.CharField(required=False, help_text="People update")
    unhcr_id = serializers.CharField(required=False, help_text="People update")
    name_enumerator = serializers.CharField(required=False, help_text="People update")
    org_enumerator = serializers.CharField(required=False, help_text="People update")
    org_name_enumerator = serializers.CharField(required=False, help_text="People update")
    registration_method = serializers.CharField(required=False, help_text="People update")
    admin_area_title = serializers.CharField(required=False, help_text="People update")


class PositiveFeedbackTicketExtras(serializers.Serializer):
    household = serializers.PrimaryKeyRelatedField(required=False, queryset=Household.objects.all())
    individual = serializers.PrimaryKeyRelatedField(required=False, queryset=Individual.objects.all())


class NegativeFeedbackTicketExtras(serializers.Serializer):
    household = serializers.PrimaryKeyRelatedField(required=False, queryset=Household.objects.all())
    individual = serializers.PrimaryKeyRelatedField(required=False, queryset=Individual.objects.all())


class GrievanceComplaintTicketExtras(serializers.Serializer):
    household = serializers.PrimaryKeyRelatedField(required=False, queryset=Household.objects.all())
    individual = serializers.PrimaryKeyRelatedField(required=False, queryset=Individual.objects.all())
    payment_record = serializers.ListField(child=serializers.PrimaryKeyRelatedField(queryset=Payment.objects.all()))


class PaymentVerificationTicketExtras(serializers.Serializer):
    pass


class ReferralTicketExtras(serializers.Serializer):
    household = serializers.PrimaryKeyRelatedField(required=False, queryset=Household.objects.all())
    individual = serializers.PrimaryKeyRelatedField(required=False, queryset=Individual.objects.all())


class SensitiveGrievanceTicketExtras(serializers.Serializer):
    household = serializers.PrimaryKeyRelatedField(required=False, queryset=Household.objects.all())
    individual = serializers.PrimaryKeyRelatedField(required=False, queryset=Individual.objects.all())
    payment_record = serializers.ListField(child=serializers.PrimaryKeyRelatedField(queryset=Payment.objects.all()))


class AddIndividualIssueTypeExtras(serializers.Serializer):
    household = serializers.PrimaryKeyRelatedField(required=True, queryset=Household.objects.all())
    individual_data = AddIndividualDataSerializer(required=True)


class UpdateAddIndividualIssueTypeExtras(serializers.Serializer):
    individual_data = AddIndividualDataSerializer(required=True)


class HouseholdDeleteIssueTypeExtras(serializers.Serializer):
    household = serializers.PrimaryKeyRelatedField(required=True, queryset=Household.objects.all())


class IndividualDeleteIssueTypeExtras(serializers.Serializer):
    individual = serializers.PrimaryKeyRelatedField(required=True, queryset=Individual.objects.all())


class HouseholdDataUpdateIssueTypeExtras(serializers.Serializer):
    household = serializers.PrimaryKeyRelatedField(required=True, queryset=Household.objects.all())
    household_data = HouseholdUpdateDataSerializer(required=True)


class UpdateHouseholdDataUpdateIssueTypeExtras(serializers.Serializer):
    household_data = HouseholdUpdateDataSerializer(required=True)


class IndividualDataUpdateIssueTypeExtras(serializers.Serializer):
    individual = serializers.PrimaryKeyRelatedField(required=False, queryset=Individual.objects.all())
    individual_data = IndividualUpdateDataSerializer(required=True)


class UpdateIndividualDataUpdateIssueTypeExtras(serializers.Serializer):
    individual_data = IndividualUpdateDataSerializer(required=True)


class IssueTypeExtrasSerializer(serializers.Serializer):
    household_data_update_issue_type_extras = HouseholdDataUpdateIssueTypeExtras(required=False)
    individual_data_update_issue_type_extras = IndividualDataUpdateIssueTypeExtras(required=False)
    individual_delete_issue_type_extras = IndividualDeleteIssueTypeExtras(required=False)
    household_delete_issue_type_extras = HouseholdDeleteIssueTypeExtras(required=False)
    add_individual_issue_type_extras = AddIndividualIssueTypeExtras(required=False)


class CategoryExtrasSerializer(serializers.Serializer):
    sensitive_grievance_ticket_extras = SensitiveGrievanceTicketExtras(required=False)
    grievance_complaint_ticket_extras = GrievanceComplaintTicketExtras(required=False)
    positive_feedback_ticket_extras = PositiveFeedbackTicketExtras(required=False)
    negative_feedback_ticket_extras = NegativeFeedbackTicketExtras(required=False)
    referral_ticket_extras = ReferralTicketExtras(required=False)


class CreateGrievanceTicketExtrasSerializer(serializers.Serializer):
    category = CategoryExtrasSerializer(required=False)
    issue_type = IssueTypeExtrasSerializer(required=False)


class GrievanceDocumentCreateSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)
    file = serializers.FileField(use_url=False, required=True)


class TicketPaymentVerificationDetailsExtras(serializers.Serializer):
    new_received_amount = serializers.FloatField()
    new_status = serializers.CharField()


class CreateGrievanceTicketSerializer(serializers.Serializer):
    description = serializers.CharField(required=True)
    assigned_to = serializers.PrimaryKeyRelatedField(required=False, queryset=User.objects.all())
    category = serializers.IntegerField(required=True)
    issue_type = serializers.IntegerField(required=False)
    admin = serializers.PrimaryKeyRelatedField(required=False, queryset=Area.objects.all())
    area = serializers.CharField(required=False)
    language = serializers.CharField(required=True)
    consent = serializers.BooleanField(required=True)
    linked_tickets = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(queryset=GrievanceTicket.objects.all()),
        required=False,
    )
    extras = CreateGrievanceTicketExtrasSerializer()
    priority = serializers.IntegerField(required=False)
    urgency = serializers.IntegerField(required=False)
    partner = serializers.PrimaryKeyRelatedField(queryset=Partner.objects.all(), required=False)
    program = serializers.PrimaryKeyRelatedField(queryset=Program.objects.all(), required=False)
    comments = serializers.CharField(required=False)
    linked_feedback_id = serializers.PrimaryKeyRelatedField(queryset=Feedback.objects.all(), required=False)
    documentation = GrievanceDocumentCreateSerializer(many=True, required=False)


class UpdateGrievanceTicketExtrasSerializer(serializers.Serializer):
    household_data_update_issue_type_extras = UpdateHouseholdDataUpdateIssueTypeExtras(required=False)
    individual_data_update_issue_type_extras = UpdateIndividualDataUpdateIssueTypeExtras(required=False)
    add_individual_issue_type_extras = UpdateAddIndividualIssueTypeExtras(required=False)
    category = CategoryExtrasSerializer(required=False)
    ticket_payment_verification_details_extras = TicketPaymentVerificationDetailsExtras(required=False)


class CreateGrievanceDocumentSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)
    file = serializers.FileField(use_url=False, required=True)


class UpdateGrievanceDocumentSerializer(serializers.Serializer):
    id = serializers.UUIDField(required=True)
    name = serializers.CharField(required=True)
    file = serializers.FileField(use_url=False, required=True)


class UpdateGrievanceTicketSerializer(serializers.Serializer):
    version = serializers.IntegerField(required=False)
    description = serializers.CharField(required=False)
    assigned_to = serializers.PrimaryKeyRelatedField(required=False, queryset=User.objects.all())
    admin = serializers.PrimaryKeyRelatedField(required=False, queryset=Area.objects.all())
    area = serializers.CharField(required=False)
    language = serializers.CharField(required=False)
    linked_tickets = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(queryset=GrievanceTicket.objects.all()),
        required=False,
    )
    household = serializers.PrimaryKeyRelatedField(queryset=Household.objects.all(), required=False)
    individual = serializers.PrimaryKeyRelatedField(queryset=Individual.objects.all(), required=False)
    payment_record = serializers.PrimaryKeyRelatedField(queryset=Payment.objects.all(), required=False)
    extras = UpdateGrievanceTicketExtrasSerializer(required=False)
    priority = serializers.IntegerField(required=False)
    urgency = serializers.IntegerField(required=False)
    partner = serializers.PrimaryKeyRelatedField(queryset=Partner.objects.all(), required=False)
    program = serializers.PrimaryKeyRelatedField(queryset=Program.objects.all(), required=False)
    comments = serializers.CharField(required=False)
    documentation = CreateGrievanceDocumentSerializer(many=True, required=False)
    documentation_to_update = UpdateGrievanceDocumentSerializer(many=True, required=False)
    documentation_to_delete = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
    )


class GrievanceStatusChangeSerializer(serializers.Serializer):
    status = serializers.IntegerField(required=True)
    version = serializers.IntegerField(required=False)


class GrievanceCreateNoteSerializer(serializers.Serializer):
    description = serializers.CharField(required=True)
    version = serializers.IntegerField(required=False)


class GrievanceIndividualDataChangeApproveSerializer(serializers.Serializer):
    individual_approve_data = serializers.JSONField(required=True)
    approved_documents_to_create = serializers.ListField(child=serializers.IntegerField(), required=False)
    approved_documents_to_edit = serializers.ListField(child=serializers.IntegerField(), required=False)
    approved_documents_to_remove = serializers.ListField(child=serializers.IntegerField(), required=False)
    approved_identities_to_create = serializers.ListField(child=serializers.IntegerField(), required=False)
    approved_identities_to_edit = serializers.ListField(child=serializers.IntegerField(), required=False)
    approved_identities_to_remove = serializers.ListField(child=serializers.IntegerField(), required=False)
    approved_payment_channels_to_create = serializers.ListField(child=serializers.IntegerField(), required=False)
    approved_payment_channels_to_edit = serializers.ListField(child=serializers.IntegerField(), required=False)
    approved_payment_channels_to_remove = serializers.ListField(child=serializers.IntegerField(), required=False)
    flex_fields_approve_data = serializers.JSONField(required=False)
    version = serializers.IntegerField(required=False)


class GrievanceHouseholdDataChangeApproveSerializer(serializers.Serializer):
    household_approve_data = serializers.JSONField(required=True)
    flex_fields_approve_data = serializers.JSONField(required=False)
    version = serializers.IntegerField(required=False)


class GrievanceUpdateApproveStatusSerializer(serializers.Serializer):
    approve_status = serializers.BooleanField(required=True)
    version = serializers.IntegerField(required=False)


class GrievanceDeleteHouseholdApproveStatusSerializer(serializers.Serializer):
    approve_status = serializers.BooleanField(required=True)
    reason_hh_id = serializers.CharField(required=False, allow_blank=True)
    version = serializers.IntegerField(required=False)


class GrievanceNeedsAdjudicationApproveSerializer(serializers.Serializer):
    selected_individual_id = serializers.PrimaryKeyRelatedField(queryset=Individual.objects.all(), required=False)
    duplicate_individual_ids = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(queryset=Individual.objects.all()), required=False
    )
    distinct_individual_ids = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(queryset=Individual.objects.all()), required=False
    )
    clear_individual_ids = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(queryset=Individual.objects.all()), required=False
    )
    version = serializers.IntegerField(required=False)


class GrievanceReassignRoleSerializer(serializers.Serializer):
    household_id = serializers.PrimaryKeyRelatedField(queryset=Household.objects.all(), required=True)
    household_version = serializers.IntegerField(required=False)
    individual_id = serializers.PrimaryKeyRelatedField(queryset=Individual.objects.all(), required=True)
    individual_version = serializers.IntegerField(required=False)
    new_individual_id = serializers.PrimaryKeyRelatedField(queryset=Individual.objects.all(), required=False)
    role = serializers.CharField(required=True)
    version = serializers.IntegerField(required=False)


class BulkUpdateGrievanceTicketsAssigneesSerializer(serializers.Serializer):
    grievance_ticket_ids = serializers.ListField(child=serializers.UUIDField(), required=True)
    assigned_to = serializers.UUIDField(required=True)


class BulkUpdateGrievanceTicketsPrioritySerializer(serializers.Serializer):
    grievance_ticket_ids = serializers.ListField(child=serializers.UUIDField(), required=True)
    priority = serializers.IntegerField(required=True)


class BulkUpdateGrievanceTicketsUrgencySerializer(serializers.Serializer):
    grievance_ticket_ids = serializers.ListField(child=serializers.UUIDField(), required=True)
    urgency = serializers.IntegerField(required=True)


class BulkGrievanceTicketsAddNoteSerializer(serializers.Serializer):
    grievance_ticket_ids = serializers.ListField(child=serializers.UUIDField(), required=True)
    note = serializers.CharField(required=True)
