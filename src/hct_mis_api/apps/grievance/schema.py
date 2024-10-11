import datetime
import logging
from typing import Any, Dict, List, Optional, Tuple, Type

from django.core.files.storage import default_storage
from django.db.models import Case, DateField, F, Q, QuerySet, When
from django.utils import timezone

import graphene
from graphene import relay
from graphene_django import DjangoObjectType

from hct_mis_api.apps.account.models import Partner
from hct_mis_api.apps.account.permissions import (
    POPULATION_DETAILS,
    AdminUrlNodeMixin,
    BaseNodePermissionMixin,
    BasePermission,
    DjangoPermissionFilterConnectionField,
    DjangoPermissionFilterFastConnectionField,
    Permissions,
    hopeOneOfPermissionClass,
    hopePermissionClass,
)
from hct_mis_api.apps.account.schema import PartnerType
from hct_mis_api.apps.core.decorators import cached_in_django_cache
from hct_mis_api.apps.core.extended_connection import ExtendedConnection
from hct_mis_api.apps.core.field_attributes.core_fields_attributes import FieldFactory
from hct_mis_api.apps.core.field_attributes.fields_types import TYPE_IMAGE, Scope
from hct_mis_api.apps.core.models import BusinessArea, FlexibleAttribute
from hct_mis_api.apps.core.schema import (
    ChoiceObject,
    ChoiceObjectInt,
    FieldAttributeNode,
    sort_by_attr,
)
from hct_mis_api.apps.core.utils import (
    chart_filters_decoder,
    chart_get_filtered_qs,
    chart_permission_decorator,
    encode_ids,
    get_program_id_from_headers,
    to_choice_object,
)
from hct_mis_api.apps.geo.models import Area
from hct_mis_api.apps.geo.schema import AreaNode
from hct_mis_api.apps.grievance.constants import PRIORITY_CHOICES, URGENCY_CHOICES
from hct_mis_api.apps.grievance.filters import (
    ExistingGrievanceTicketFilter,
    GrievanceTicketFilter,
    TicketNoteFilter,
)
from hct_mis_api.apps.grievance.models import (
    GrievanceDocument,
    GrievanceTicket,
    TicketAddIndividualDetails,
    TicketComplaintDetails,
    TicketDeleteHouseholdDetails,
    TicketDeleteIndividualDetails,
    TicketHouseholdDataUpdateDetails,
    TicketIndividualDataUpdateDetails,
    TicketNeedsAdjudicationDetails,
    TicketNegativeFeedbackDetails,
    TicketNote,
    TicketPaymentVerificationDetails,
    TicketPositiveFeedbackDetails,
    TicketReferralDetails,
    TicketSensitiveDetails,
    TicketSystemFlaggingDetails,
)
from hct_mis_api.apps.grievance.utils import (
    filter_grievance_tickets_based_on_partner_areas_2,
)
from hct_mis_api.apps.household.schema import HouseholdNode, IndividualNode
from hct_mis_api.apps.payment.schema import PaymentRecordAndPaymentNode
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.program.schema import ProgramNode
from hct_mis_api.apps.registration_data.nodes import (
    DeduplicationEngineSimilarityPairNode,
    DeduplicationResultNode,
)
from hct_mis_api.apps.utils.exceptions import log_and_raise
from hct_mis_api.apps.utils.schema import Arg, ChartDatasetNode

logger = logging.getLogger(__name__)


class GrievanceDocumentNode(DjangoObjectType):
    file_path = graphene.String(source="file_path")
    file_name = graphene.String(source="file_name")

    class Meta:
        model = GrievanceDocument
        exclude = ("file",)
        interfaces = (relay.Node,)


class GrievanceTicketNode(BaseNodePermissionMixin, AdminUrlNodeMixin, DjangoObjectType):
    permission_classes: Tuple[Type[BasePermission], ...] = (
        hopePermissionClass(Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE),
        hopePermissionClass(Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE_AS_CREATOR),
        hopePermissionClass(Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE_AS_OWNER),
        hopePermissionClass(Permissions.GRIEVANCES_VIEW_DETAILS_SENSITIVE),
        hopePermissionClass(Permissions.GRIEVANCES_VIEW_DETAILS_SENSITIVE_AS_CREATOR),
        hopePermissionClass(Permissions.GRIEVANCES_VIEW_DETAILS_SENSITIVE_AS_OWNER),
    )
    household = graphene.Field(HouseholdNode)
    individual = graphene.Field(IndividualNode)
    payment_record = graphene.Field(PaymentRecordAndPaymentNode)
    admin = graphene.String()
    admin2 = graphene.Field(AreaNode)
    linked_tickets = graphene.List(lambda: GrievanceTicketNode)
    existing_tickets = graphene.List(lambda: GrievanceTicketNode)
    related_tickets = graphene.List(lambda: GrievanceTicketNode)
    priority = graphene.Int()
    urgency = graphene.Int()
    total_days = graphene.String()
    partner = graphene.Field(PartnerType)
    programs = graphene.List(ProgramNode)
    documentation = graphene.List(GrievanceDocumentNode)

    @classmethod
    def check_node_permission(cls, info: Any, object_instance: GrievanceTicket) -> None:
        super().check_node_permission(info, object_instance)
        business_area = object_instance.business_area
        user = info.context.user
        # when selected All programs in GPF program_id is None
        program_id: Optional[str] = get_program_id_from_headers(info.context.headers)

        if object_instance.category == GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE:
            perm = Permissions.GRIEVANCES_VIEW_DETAILS_SENSITIVE.value
            creator_perm = Permissions.GRIEVANCES_VIEW_DETAILS_SENSITIVE_AS_CREATOR.value
            owner_perm = Permissions.GRIEVANCES_VIEW_DETAILS_SENSITIVE_AS_OWNER.value
        else:
            perm = Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE.value
            creator_perm = Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE_AS_CREATOR.value
            owner_perm = Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE_AS_OWNER.value

        check_creator = object_instance.created_by == user and user.has_permission(
            creator_perm, business_area, program_id
        )
        check_assignee = object_instance.assigned_to == user and user.has_permission(
            owner_perm, business_area, program_id
        )
        partner = user.partner
        has_partner_area_access = partner.is_unicef
        ticket_program_id = str(object_instance.programs.first().id) if object_instance.programs.first() else None
        if not partner.is_unicef:
            if not object_instance.admin2 or not ticket_program_id:
                # admin2 is empty or non-program ticket -> no restrictions for admin area
                has_partner_area_access = True
            else:
                has_partner_area_access = partner.has_area_access(
                    area_id=object_instance.admin2.id, program_id=ticket_program_id
                )
        if (
            user.has_permission(perm, business_area, ticket_program_id) or check_creator or check_assignee
        ) and has_partner_area_access:
            return None

        log_and_raise(
            f"User is not active creator/assignee and does not have '{perm}' permission"
            f" or user does not have access to the ticket's program or its admin area"
        )

    class Meta:
        model = GrievanceTicket
        convert_choices_to_enum = False
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection

    @staticmethod
    def resolve_household(grievance_ticket: GrievanceTicket, info: Any) -> Optional[Any]:
        return getattr(grievance_ticket.ticket_details, "household", None)

    @staticmethod
    def resolve_individual(grievance_ticket: GrievanceTicket, info: Any) -> Optional[Any]:
        return getattr(grievance_ticket.ticket_details, "individual", None)

    @staticmethod
    def resolve_payment_record(grievance_ticket: GrievanceTicket, info: Any) -> Optional[Any]:
        payment_verification = getattr(grievance_ticket.ticket_details, "payment_verification", None)
        payment_obj = getattr(grievance_ticket.ticket_details, "payment_obj", None)
        return getattr(payment_verification, "payment_obj", None) if payment_verification else payment_obj

    @staticmethod
    def resolve_admin(grievance_ticket: GrievanceTicket, info: Any) -> Optional[str]:
        return getattr(grievance_ticket.admin2, "name", None)

    @staticmethod
    def resolve_admin2(grievance_ticket: GrievanceTicket, info: Any) -> Area:
        return grievance_ticket.admin2

    @staticmethod
    def resolve_linked_tickets(grievance_ticket: GrievanceTicket, info: Any) -> QuerySet:
        return grievance_ticket._linked_tickets

    @staticmethod
    def resolve_existing_tickets(grievance_ticket: GrievanceTicket, info: Any) -> QuerySet:
        return grievance_ticket._existing_tickets

    @staticmethod
    def resolve_related_tickets(grievance_ticket: GrievanceTicket, info: Any) -> QuerySet:
        return grievance_ticket._related_tickets

    @staticmethod
    def resolve_priority(grievance_ticket: GrievanceTicket, info: Any) -> int:
        return grievance_ticket.priority

    @staticmethod
    def resolve_urgency(grievance_ticket: GrievanceTicket, info: Any) -> int:
        return grievance_ticket.urgency

    @staticmethod
    def resolve_partner(grievance_ticket: GrievanceTicket, info: Any) -> Partner:
        return grievance_ticket.partner

    @staticmethod
    def resolve_programs(grievance_ticket: GrievanceTicket, info: Any) -> Program:
        return grievance_ticket.programs.all()

    @staticmethod
    def resolve_documentation(grievance_ticket: GrievanceTicket, info: Any) -> "QuerySet[GrievanceDocument]":
        return grievance_ticket.support_documents.order_by("-created_at")


class TicketNoteNode(DjangoObjectType):
    class Meta:
        model = TicketNote
        exclude = ("ticket",)
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class TicketComplaintDetailsNode(DjangoObjectType):
    payment_record = graphene.Field(PaymentRecordAndPaymentNode)

    class Meta:
        model = TicketComplaintDetails
        exclude = ("ticket",)
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection

    def resolve_payment_record(self, info: Any) -> Optional[Any]:
        return getattr(self, "payment_obj", None)


class TicketSensitiveDetailsNode(DjangoObjectType):
    payment_record = graphene.Field(PaymentRecordAndPaymentNode)

    class Meta:
        model = TicketSensitiveDetails
        exclude = ("ticket",)
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection

    def resolve_payment_record(self, info: Any) -> Optional[Any]:
        return getattr(self, "payment_obj", None)


class TicketIndividualDataUpdateDetailsNode(DjangoObjectType):
    individual_data = Arg()

    class Meta:
        model = TicketIndividualDataUpdateDetails
        exclude = ("ticket",)
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection

    def resolve_individual_data(self, info: Any) -> Dict:
        individual_data: Dict = self.individual_data  # type: ignore # mypy doesn't get that Arg() is a Dict
        flex_fields = individual_data.get("flex_fields")
        if flex_fields:
            images_flex_fields_names = FlexibleAttribute.objects.filter(type=TYPE_IMAGE).values_list("name", flat=True)
            for name, value in flex_fields.items():
                if value and name in images_flex_fields_names:
                    try:
                        previous_value = value.get("previous_value", "")
                        if previous_value:
                            previous_value = default_storage.url(previous_value)
                        flex_fields[name]["previous_value"] = previous_value

                        current_value = value.get("value", "")
                        if current_value:
                            current_value = default_storage.url(current_value)
                        flex_fields[name]["value"] = current_value
                    except Exception:
                        pass
            individual_data["flex_fields"] = flex_fields

        if documents_to_edit := individual_data.get("documents_to_edit"):
            for index, document in enumerate(documents_to_edit):
                previous_value = document.get("previous_value", {})
                if previous_value and previous_value.get("photo"):
                    previous_value["photoraw"] = previous_value["photo"]
                    previous_value["photo"] = default_storage.url(previous_value.get("photo"))
                    documents_to_edit[index]["previous_value"] = previous_value

                current_value = document.get("value", {})
                if current_value and current_value.get("photo"):
                    current_value["photoraw"] = current_value["photo"]
                    current_value["photo"] = default_storage.url(current_value.get("photo"))
                    documents_to_edit[index]["value"] = current_value
            individual_data["documents_to_edit"] = documents_to_edit

        if documents := individual_data.get("documents"):
            for index, document in enumerate(documents):
                current_value = document.get("value", {})
                if current_value and current_value.get("photo"):
                    current_value["photoraw"] = current_value["photo"]
                    current_value["photo"] = default_storage.url(current_value.get("photo"))
                    documents[index]["value"] = current_value
            individual_data["documents"] = documents

        return individual_data


class TicketAddIndividualDetailsNode(DjangoObjectType):
    individual_data = Arg()

    class Meta:
        model = TicketAddIndividualDetails
        exclude = ("ticket",)
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection

    def resolve_individual_data(self, info: Any) -> Dict:
        individual_data: Dict = self.individual_data  # type: ignore # mypy doesn't get that Arg() is a Dict
        flex_fields = individual_data.get("flex_fields")
        if flex_fields:
            images_flex_fields_names = FlexibleAttribute.objects.filter(type=TYPE_IMAGE).values_list("name", flat=True)
            for name, value in flex_fields.items():
                if value and name in images_flex_fields_names:
                    try:
                        if value:
                            flex_fields[name] = default_storage.url(value)
                        else:
                            flex_fields[name] = ""
                    except Exception:
                        pass
            individual_data["flex_fields"] = flex_fields

        if documents := individual_data.get("documents"):
            for index, document in enumerate(documents):
                if document and document["photo"]:
                    document["photoraw"] = document["photo"]
                    document["photo"] = default_storage.url(document["photo"])
                    documents[index] = document
            individual_data["documents"] = documents
        return individual_data


class TicketDeleteIndividualDetailsNode(DjangoObjectType):
    individual_data = Arg()

    class Meta:
        model = TicketDeleteIndividualDetails
        exclude = ("ticket",)
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class TicketDeleteHouseholdDetailsNode(DjangoObjectType):
    household_data = Arg()

    class Meta:
        model = TicketDeleteHouseholdDetails
        exclude = ("ticket",)
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class TicketHouseholdDataUpdateDetailsNode(DjangoObjectType):
    household_data = Arg()

    class Meta:
        model = TicketHouseholdDataUpdateDetails
        exclude = ("ticket",)
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection

    @staticmethod
    def resolve_household_data(parent: TicketHouseholdDataUpdateDetails, info: Any) -> Dict:
        household_data = parent.household_data
        if admin_area_title := household_data.get("admin_area_title"):
            if value := admin_area_title.get("value"):
                area = Area.objects.get(p_code=value)
                admin_area_title["value"] = f"{area.name} - {area.p_code}"

            if previous_value := admin_area_title.get("previous_value"):
                area = Area.objects.get(p_code=previous_value)
                admin_area_title["previous_value"] = f"{area.name} - {area.p_code}"

            household_data["admin_area_title"] = admin_area_title
        return household_data


class TicketNeedsAdjudicationDetailsExtraDataNode(graphene.ObjectType):
    golden_records = graphene.List(DeduplicationResultNode)
    possible_duplicate = graphene.List(DeduplicationResultNode)
    dedup_engine_similarity_pair = graphene.Field(DeduplicationEngineSimilarityPairNode)

    def resolve_golden_records(self, info: Any) -> List[Dict]:
        return encode_ids(self.golden_records, "Individual", "hit_id")

    def resolve_possible_duplicate(self, info: Any) -> List[Dict]:
        return encode_ids(self.possible_duplicate, "Individual", "hit_id")


class TicketNeedsAdjudicationDetailsNode(DjangoObjectType):
    has_duplicated_document = graphene.Boolean()
    extra_data = graphene.Field(TicketNeedsAdjudicationDetailsExtraDataNode)
    possible_duplicates = graphene.List(IndividualNode)
    selected_duplicates = graphene.List(IndividualNode)
    selected_distinct = graphene.List(IndividualNode)

    class Meta:
        model = TicketNeedsAdjudicationDetails
        exclude = ("ticket",)
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection

    def resolve_extra_data(parent, info: Any) -> TicketNeedsAdjudicationDetailsExtraDataNode:
        golden_records = parent.extra_data.get("golden_records")
        possible_duplicate = parent.extra_data.get("possible_duplicate")
        dedup_engine_similarity_pair = parent.extra_data.get("dedup_engine_similarity_pair")
        return TicketNeedsAdjudicationDetailsExtraDataNode(
            golden_records, possible_duplicate, dedup_engine_similarity_pair
        )

    def resolve_possible_duplicates(self, info: Any) -> QuerySet:
        return self.possible_duplicates.all()

    def resolve_selected_duplicates(self, info: Any) -> QuerySet:
        return self.selected_individuals.all()

    def resolve_selected_distinct(self, info: Any) -> QuerySet:
        return self.selected_distinct.all()


class TicketSystemFlaggingDetailsNode(DjangoObjectType):
    class Meta:
        model = TicketSystemFlaggingDetails
        exclude = ("ticket",)
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class TicketPaymentVerificationDetailsNode(DjangoObjectType):
    has_multiple_payment_verifications = graphene.Boolean(source="has_multiple_payment_verifications")

    class Meta:
        model = TicketPaymentVerificationDetails
        exclude = ("ticket",)
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class TicketPositiveFeedbackDetailsNode(DjangoObjectType):
    class Meta:
        model = TicketPositiveFeedbackDetails
        exclude = ("ticket",)
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class TicketNegativeFeedbackDetailsNode(DjangoObjectType):
    class Meta:
        model = TicketNegativeFeedbackDetails
        exclude = ("ticket",)
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class TicketReferralDetailsNode(DjangoObjectType):
    class Meta:
        model = TicketReferralDetails
        exclude = ("ticket",)
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class IssueTypesObject(graphene.ObjectType):
    category = graphene.String()
    label = graphene.String()
    sub_categories = graphene.List(ChoiceObject)

    def resolve_sub_categories(self, info: Any) -> List[Dict[str, str]]:
        return [{"name": value, "value": key} for key, value in self.get("sub_categories").items()]


class AddIndividualFiledObjectType(graphene.ObjectType):
    name = graphene.String()
    label = graphene.String()
    required = graphene.Boolean()
    type = graphene.String()
    flex_field = graphene.Boolean()


class ChartGrievanceTicketsNode(ChartDatasetNode):
    total_number_of_grievances = graphene.Int()
    total_number_of_feedback = graphene.Int()
    total_number_of_open_sensitive = graphene.Int()


class Query(graphene.ObjectType):
    grievance_ticket = relay.Node.Field(GrievanceTicketNode)
    all_grievance_ticket = DjangoPermissionFilterFastConnectionField(
        GrievanceTicketNode,
        filterset_class=GrievanceTicketFilter,
        permission_classes=(
            hopePermissionClass(Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE),
            hopePermissionClass(Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE_AS_CREATOR),
            hopePermissionClass(Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE_AS_OWNER),
            hopePermissionClass(Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE),
            hopePermissionClass(Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE_AS_CREATOR),
            hopePermissionClass(Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE_AS_OWNER),
            hopeOneOfPermissionClass(*POPULATION_DETAILS),
        ),
    )
    cross_area_filter_available = graphene.Boolean()
    existing_grievance_tickets = DjangoPermissionFilterFastConnectionField(
        GrievanceTicketNode,
        filterset_class=ExistingGrievanceTicketFilter,
        permission_classes=(
            hopePermissionClass(Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE),
            hopePermissionClass(Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE_AS_CREATOR),
            hopePermissionClass(Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE_AS_OWNER),
            hopePermissionClass(Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE),
            hopePermissionClass(Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE_AS_CREATOR),
            hopePermissionClass(Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE_AS_OWNER),
        ),
    )
    all_ticket_notes = DjangoPermissionFilterConnectionField(
        TicketNoteNode,
        filterset_class=TicketNoteFilter,
    )
    chart_grievances = graphene.Field(
        ChartGrievanceTicketsNode,
        business_area_slug=graphene.String(required=True),
        year=graphene.Int(required=True),
        administrative_area=graphene.String(required=False),
    )
    all_add_individuals_fields_attributes = graphene.List(FieldAttributeNode, description="All field datatype meta.")
    all_edit_household_fields_attributes = graphene.List(FieldAttributeNode, description="All field datatype meta.")
    grievance_ticket_status_choices = graphene.List(ChoiceObject)
    grievance_ticket_category_choices = graphene.List(ChoiceObject)
    grievance_ticket_manual_category_choices = graphene.List(ChoiceObject)
    grievance_ticket_system_category_choices = graphene.List(ChoiceObject)
    grievance_ticket_issue_type_choices = graphene.List(IssueTypesObject)
    grievance_ticket_priority_choices = graphene.List(ChoiceObjectInt)
    grievance_ticket_urgency_choices = graphene.List(ChoiceObjectInt)

    def resolve_all_grievance_ticket(self, info: Any, **kwargs: Any) -> QuerySet:
        user = info.context.user
        program_id = get_program_id_from_headers(info.context.headers)
        business_area_slug = info.context.headers.get("Business-Area")
        business_area_id = BusinessArea.objects.get(slug=business_area_slug).id

        queryset = GrievanceTicket.objects.filter(ignored=False).select_related("admin2", "assigned_to", "created_by")
        to_prefetch = []
        for key, value in GrievanceTicket.SEARCH_TICKET_TYPES_LOOKUPS.items():
            to_prefetch.append(key)
            if "household" in value:
                to_prefetch.append(f"{key}__{value['household']}")
            if "golden_records_individual" in value:
                to_prefetch.append(f"{key}__{value['golden_records_individual']}__household")

        queryset = queryset.prefetch_related(*to_prefetch)

        # Full access to all AdminAreas if is_unicef
        # and ignore filtering for Cross Area tickets
        if not user.partner.is_unicef and not (
            kwargs.get("is_cross_area", False)
            and program_id
            and user.partner.has_full_area_access_in_program(program_id)
        ):
            queryset = filter_grievance_tickets_based_on_partner_areas_2(
                queryset, user.partner, business_area_id, program_id
            )

        if program_id is None:
            queryset = queryset | (
                GrievanceTicket.objects.select_related("admin2", "assigned_to", "created_by")
                .prefetch_related(*to_prefetch)
                .filter(business_area_id=business_area_id, programs=None)
            )
        else:
            queryset = queryset.filter(programs__id=program_id)

        return queryset.annotate(
            total=Case(
                When(
                    status=GrievanceTicket.STATUS_CLOSED,
                    then=F("updated_at") - F("created_at"),
                ),
                default=timezone.now() - F("created_at"),  # type: ignore
                output_field=DateField(),
            )
        ).annotate(total_days=F("total__day"))

    def resolve_cross_area_filter_available(self, info: Any, **kwargs: Any) -> bool:
        user = info.context.user
        if not user.is_authenticated:
            return False
        business_area = BusinessArea.objects.get(slug=info.context.headers.get("Business-Area"))
        program_id = get_program_id_from_headers(info.context.headers)

        perm = Permissions.GRIEVANCES_CROSS_AREA_FILTER.value

        return user.has_permission(perm, business_area, program_id) and user.partner.has_full_area_access_in_program(
            program_id
        )

    def resolve_grievance_ticket_status_choices(self, info: Any, **kwargs: Any) -> List[Dict[str, Any]]:
        return to_choice_object(GrievanceTicket.STATUS_CHOICES)

    def resolve_grievance_ticket_category_choices(self, info: Any, **kwargs: Any) -> List[Dict[str, Any]]:
        return to_choice_object(GrievanceTicket.CATEGORY_CHOICES)

    def resolve_grievance_ticket_manual_category_choices(self, info: Any, **kwargs: Any) -> List[Dict[str, Any]]:
        return to_choice_object(GrievanceTicket.CREATE_CATEGORY_CHOICES)

    def resolve_grievance_ticket_system_category_choices(self, info: Any, **kwargs: Any) -> List[Dict[str, Any]]:
        return to_choice_object(GrievanceTicket.SYSTEM_CATEGORIES)

    def resolve_grievance_ticket_issue_type_choices(self, info: Any, **kwargs: Any) -> List[Dict]:
        categories = dict(GrievanceTicket.CATEGORY_CHOICES)
        return [
            {"category": key, "label": categories[key], "sub_categories": value}
            for (key, value) in GrievanceTicket.ISSUE_TYPES_CHOICES.items()
        ]

    def resolve_grievance_ticket_priority_choices(self, info: Any, **kwargs: Any) -> List[Dict[str, Any]]:
        return to_choice_object(PRIORITY_CHOICES)

    def resolve_grievance_ticket_urgency_choices(self, info: Any, **kwargs: Any) -> List[Dict[str, Any]]:
        return to_choice_object(URGENCY_CHOICES)

    def resolve_all_add_individuals_fields_attributes(self, info: Any, **kwargs: Any) -> List:
        business_area_slug = info.context.headers.get("Business-Area")
        fields = (
            FieldFactory.from_scope(Scope.INDIVIDUAL_UPDATE)
            .associated_with_individual()
            .apply_business_area(business_area_slug)
        )
        all_options = list(fields) + list(
            FlexibleAttribute.objects.filter(associated_with=FlexibleAttribute.ASSOCIATED_WITH_INDIVIDUAL)
            .exclude(type=FlexibleAttribute.PDU)
            .prefetch_related("choices")
        )
        return sort_by_attr(all_options, "label.English(EN)")

    def resolve_all_edit_household_fields_attributes(self, info: Any, **kwargs: Any) -> List:
        business_area_slug = info.context.headers.get("Business-Area")
        fields = (
            FieldFactory.from_scope(Scope.HOUSEHOLD_UPDATE)
            .associated_with_household()
            .apply_business_area(business_area_slug)
        )
        all_options = list(fields) + list(
            FlexibleAttribute.objects.filter(
                associated_with=FlexibleAttribute.ASSOCIATED_WITH_HOUSEHOLD
            ).prefetch_related("choices")
        )
        return sort_by_attr(all_options, "label.English(EN)")

    @chart_permission_decorator(permissions=[Permissions.DASHBOARD_VIEW_COUNTRY])
    @cached_in_django_cache(24)
    def resolve_chart_grievances(
        self, info: Any, business_area_slug: str, year: int, **kwargs: Any
    ) -> Dict[str, object]:
        grievance_tickets = chart_get_filtered_qs(
            GrievanceTicket.objects,
            year,
            business_area_slug_filter={"business_area__slug": business_area_slug},
        )

        filters = chart_filters_decoder(kwargs)
        if filters.get("administrative_area") is not None:
            try:
                grievance_tickets = grievance_tickets.filter(
                    admin2=Area.objects.get(id=filters.get("administrative_area"))
                )
            except Area.DoesNotExist:
                pass

        grievance_status_labels = [
            "Resolved",
            "Unresolved",
            "Unresolved for longer than 30 days",
            "Unresolved for longer than 60 days",
        ]

        days_30_from_now = datetime.date.today() - datetime.timedelta(days=30)
        days_60_from_now = datetime.date.today() - datetime.timedelta(days=60)

        feedback_categories = [
            GrievanceTicket.CATEGORY_POSITIVE_FEEDBACK,
            GrievanceTicket.CATEGORY_NEGATIVE_FEEDBACK,
        ]
        all_open_tickets = grievance_tickets.filter(~Q(status=GrievanceTicket.STATUS_CLOSED))
        all_closed_tickets = grievance_tickets.filter(status=GrievanceTicket.STATUS_CLOSED)

        datasets = [
            {
                "data": [
                    all_closed_tickets.count(),  # Resolved
                    all_open_tickets.filter(
                        created_at__gte=days_30_from_now,
                    ).count(),  # Unresolved less than 30 days
                    all_open_tickets.filter(
                        created_at__lt=days_30_from_now,
                        created_at__gte=days_60_from_now,
                    ).count(),  # Unresolved for longer than 30 days
                    all_open_tickets.filter(
                        created_at__lt=days_60_from_now
                    ).count(),  # Unresolved for longer than 60 days
                ]
            },
        ]
        return {
            "labels": grievance_status_labels,
            "datasets": datasets,
            "total_number_of_grievances": grievance_tickets.exclude(category__in=feedback_categories).count(),
            "total_number_of_feedback": grievance_tickets.filter(category__in=feedback_categories).count(),
            "total_number_of_open_sensitive": all_open_tickets.filter(
                category=GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE,
            ).count(),
        }
