import datetime
import logging

from django.core.files.storage import default_storage
from django.db.models import Q

import graphene
from graphene import relay
from graphene_django import DjangoObjectType
from graphql import GraphQLError

from hct_mis_api.apps.account.permissions import (
    BaseNodePermissionMixin,
    DjangoPermissionFilterConnectionField,
    Permissions,
    hopePermissionClass,
)
from hct_mis_api.apps.core.core_fields_attributes import (
    _HOUSEHOLD,
    _INDIVIDUAL,
    CORE_FIELDS_ATTRIBUTES,
    HOUSEHOLD_EDIT_ONLY_FIELDS,
    KOBO_ONLY_INDIVIDUAL_FIELDS,
    TYPE_IMAGE,
)
from hct_mis_api.apps.core.extended_connection import ExtendedConnection
from hct_mis_api.apps.core.models import FlexibleAttribute
from hct_mis_api.apps.core.schema import (
    ChoiceObject,
    FieldAttributeNode,
    sort_by_attr,
)
from hct_mis_api.apps.core.utils import (
    chart_filters_decoder,
    chart_get_filtered_qs,
    chart_permission_decorator,
    choices_to_dict,
    encode_ids,
    nested_getattr,
    to_choice_object,
)
from hct_mis_api.apps.geo.models import Area
from hct_mis_api.apps.geo.schema import AreaNode
from hct_mis_api.apps.grievance.models import (
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
from hct_mis_api.apps.household.schema import HouseholdNode, IndividualNode
from hct_mis_api.apps.payment.schema import PaymentRecordNode
from hct_mis_api.apps.grievance.filters import ExistingGrievanceTicketFilter, GrievanceTicketFilter, TicketNoteFilter
from hct_mis_api.apps.registration_datahub.schema import DeduplicationResultNode
from hct_mis_api.apps.utils.schema import Arg, ChartDatasetNode

logger = logging.getLogger(__name__)


class GrievanceTicketNode(BaseNodePermissionMixin, DjangoObjectType):
    permission_classes = (
        hopePermissionClass(Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE),
        hopePermissionClass(Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE_AS_CREATOR),
        hopePermissionClass(Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE_AS_OWNER),
        hopePermissionClass(Permissions.GRIEVANCES_VIEW_DETAILS_SENSITIVE),
        hopePermissionClass(Permissions.GRIEVANCES_VIEW_DETAILS_SENSITIVE_AS_CREATOR),
        hopePermissionClass(Permissions.GRIEVANCES_VIEW_DETAILS_SENSITIVE_AS_OWNER),
    )
    household = graphene.Field(HouseholdNode)
    individual = graphene.Field(IndividualNode)
    payment_record = graphene.Field(PaymentRecordNode)
    related_tickets = graphene.List(lambda: GrievanceTicketNode)
    admin = graphene.String()
    admin2 = graphene.Field(AreaNode)

    @staticmethod
    def _search_for_lookup(grievance_ticket_obj, lookup_name):
        for field, lookups in GrievanceTicket.FIELD_TICKET_TYPES_LOOKUPS.items():
            extras_field = getattr(grievance_ticket_obj, field, None)
            if extras_field is None:
                continue
            real_lookup = lookup_name
            for lookup in lookups:
                if isinstance(lookup, dict):
                    tmp_lookup = lookup.get(lookup_name)
                    if tmp_lookup is not None:
                        real_lookup = tmp_lookup
                        break
            obj = nested_getattr(extras_field, real_lookup, None)
            if obj is not None:
                return obj

    @classmethod
    def check_node_permission(cls, info, object_instance):
        super().check_node_permission(info, object_instance)
        business_area = object_instance.business_area
        user = info.context.user

        if object_instance.category == GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE:
            perm = Permissions.GRIEVANCES_VIEW_DETAILS_SENSITIVE.value
            creator_perm = Permissions.GRIEVANCES_VIEW_DETAILS_SENSITIVE_AS_CREATOR.value
            owner_perm = Permissions.GRIEVANCES_VIEW_DETAILS_SENSITIVE_AS_OWNER.value
        else:
            perm = Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE.value
            creator_perm = Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE_AS_CREATOR.value
            owner_perm = Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE_AS_OWNER.value

        check_creator = object_instance.created_by == user and user.has_permission(creator_perm, business_area)
        check_assignee = object_instance.assigned_to == user and user.has_permission(owner_perm, business_area)
        if user.has_permission(perm, business_area) or check_creator or check_assignee:
            return True

        msg = "User is not active creator/assignee and does not have '{perm}' permission"
        logger.error(msg)
        raise GraphQLError(msg)

    class Meta:
        model = GrievanceTicket
        convert_choices_to_enum = False
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection

    def resolve_related_tickets(grievance_ticket, info):
        return grievance_ticket.related_tickets

    def resolve_household(grievance_ticket, info):
        return GrievanceTicketNode._search_for_lookup(grievance_ticket, "household")

    def resolve_individual(grievance_ticket, info):
        return GrievanceTicketNode._search_for_lookup(grievance_ticket, "individual")

    def resolve_payment_record(grievance_ticket, info):
        return GrievanceTicketNode._search_for_lookup(grievance_ticket, "payment_record")

    def resolve_admin(grievance_ticket, info):
        if grievance_ticket.admin2_new:
            return grievance_ticket.admin2_new.name
        return None

    def resolve_admin2(grievance_ticket, info):
        return grievance_ticket.admin2_new


class TicketNoteNode(DjangoObjectType):
    class Meta:
        model = TicketNote
        exclude = ("ticket",)
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class TicketComplaintDetailsNode(DjangoObjectType):
    class Meta:
        model = TicketComplaintDetails
        exclude = ("ticket",)
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class TicketSensitiveDetailsNode(DjangoObjectType):
    class Meta:
        model = TicketSensitiveDetails
        exclude = ("ticket",)
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class TicketIndividualDataUpdateDetailsNode(DjangoObjectType):
    individual_data = Arg()

    class Meta:
        model = TicketIndividualDataUpdateDetails
        exclude = ("ticket",)
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection

    def resolve_individual_data(self, info):
        individual_data = self.individual_data
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

        documents_to_edit = individual_data.get("documents_to_edit")
        if documents_to_edit:
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

        documents = individual_data.get("documents")
        if documents:
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

    def resolve_individual_data(self, info):
        individual_data = self.individual_data
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

        documents = individual_data.get("documents")
        if documents:
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


class TicketNeedsAdjudicationDetailsExtraDataNode(graphene.ObjectType):
    golden_records = graphene.List(DeduplicationResultNode)
    possible_duplicate = graphene.List(DeduplicationResultNode)

    def resolve_golden_records(self, info):
        return encode_ids(self.golden_records, "Individual", "hit_id")

    def resolve_possible_duplicate(self, info):
        return encode_ids(self.possible_duplicate, "Individual", "hit_id")


class TicketNeedsAdjudicationDetailsNode(DjangoObjectType):
    has_duplicated_document = graphene.Boolean()
    extra_data = graphene.Field(TicketNeedsAdjudicationDetailsExtraDataNode)

    class Meta:
        model = TicketNeedsAdjudicationDetails
        exclude = ("ticket",)
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection

    def resolve_extra_data(parent, info):
        golden_records = parent.extra_data.get("golden_records")
        possible_duplicate = parent.extra_data.get("possible_duplicate")
        return TicketNeedsAdjudicationDetailsExtraDataNode(golden_records, possible_duplicate)


class TicketSystemFlaggingDetailsNode(DjangoObjectType):
    class Meta:
        model = TicketSystemFlaggingDetails
        exclude = ("ticket",)
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class TicketPaymentVerificationDetailsNode(DjangoObjectType):
    has_multiple_payment_verifications = graphene.Boolean(source='has_multiple_payment_verifications')

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

    def resolve_sub_categories(self, info):
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
    all_grievance_ticket = DjangoPermissionFilterConnectionField(
        GrievanceTicketNode,
        filterset_class=GrievanceTicketFilter,
        permission_classes=(
            hopePermissionClass(Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE),
            hopePermissionClass(Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE_AS_CREATOR),
            hopePermissionClass(Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE_AS_OWNER),
            hopePermissionClass(Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE),
            hopePermissionClass(Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE_AS_CREATOR),
            hopePermissionClass(Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE_AS_OWNER),
        ),
    )
    existing_grievance_tickets = DjangoPermissionFilterConnectionField(
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
    grievance_ticket_issue_type_choices = graphene.List(IssueTypesObject)

    def resolve_all_grievance_ticket(self, info, **kwargs):
        return GrievanceTicket.objects.select_related("assigned_to", "created_by")

    def resolve_grievance_ticket_status_choices(self, info, **kwargs):
        return to_choice_object(GrievanceTicket.STATUS_CHOICES)

    def resolve_grievance_ticket_category_choices(self, info, **kwargs):
        return to_choice_object(GrievanceTicket.CATEGORY_CHOICES)

    def resolve_grievance_ticket_manual_category_choices(self, info, **kwargs):
        return [
            {"name": name, "value": value}
            for value, name in GrievanceTicket.CATEGORY_CHOICES
            if value in GrievanceTicket.MANUAL_CATEGORIES
        ]

    def resolve_grievance_ticket_all_category_choices(self, info, **kwargs):
        return [{"name": name, "value": value} for value, name in GrievanceTicket.CATEGORY_CHOICES]

    def resolve_grievance_ticket_issue_type_choices(self, info, **kwargs):
        categories = choices_to_dict(GrievanceTicket.CATEGORY_CHOICES)
        return [
            {"category": key, "label": categories[key], "sub_categories": value}
            for (key, value) in GrievanceTicket.ISSUE_TYPES_CHOICES.items()
        ]

    def resolve_all_add_individuals_fields_attributes(self, info, **kwargs):
        ACCEPTABLE_FIELDS = [
            "full_name",
            "given_name",
            "middle_name",
            "family_name",
            "sex",
            "birth_date",
            "estimated_birth_date",
            "marital_status",
            "phone_no",
            "phone_no_alternative",
            "relationship",
            "disability",
            "work_status",
            "enrolled_in_nutrition_programme",
            "administration_of_rutf",
            "pregnant",
            "observed_disability",
            "seeing_disability",
            "hearing_disability",
            "physical_disability",
            "memory_disability",
            "selfcare_disability",
            "comms_disability",
            "who_answers_phone",
            "who_answers_alt_phone",
        ]

        all_options = (
            [
                x
                for x in CORE_FIELDS_ATTRIBUTES
                if x.get("associated_with") == _INDIVIDUAL and x.get("name") in ACCEPTABLE_FIELDS
            ]
            + list(KOBO_ONLY_INDIVIDUAL_FIELDS.values())
            + list(FlexibleAttribute.objects.filter(associated_with=FlexibleAttribute.ASSOCIATED_WITH_INDIVIDUAL))
        )

        return sort_by_attr(all_options, "label.English(EN)")

    def resolve_all_edit_household_fields_attributes(self, info, **kwargs):
        ACCEPTABLE_FIELDS = [
            "status",
            "consent",
            "consent_sharing",
            "residence_status",
            "country_origin",
            "country",
            "size",
            "address",
            "admin_area_title",
            "female_age_group_0_5_count",
            "female_age_group_6_11_count",
            "female_age_group_12_17_count",
            "female_age_group_18_59_count",
            "female_age_group_60_count",
            "pregnant_count",
            "male_age_group_0_5_count",
            "male_age_group_6_11_count",
            "male_age_group_12_17_count",
            "male_age_group_18_59_count",
            "male_age_group_60_count",
            "female_age_group_0_5_disabled_count",
            "female_age_group_6_11_disabled_count",
            "female_age_group_12_17_disabled_count",
            "female_age_group_18_59_disabled_count",
            "female_age_group_60_disabled_count",
            "male_age_group_0_5_disabled_count",
            "male_age_group_6_11_disabled_count",
            "male_age_group_12_17_disabled_count",
            "male_age_group_18_59_disabled_count",
            "male_age_group_60_disabled_count",
            "returnee",
            "fchild_hoh",
            "child_hoh",
            "start",
            "end",
            "name_enumerator",
            "org_enumerator",
            "org_name_enumerator",
            "village",
            "registration_method",
            "collect_individual_data",
            "currency",
            "unhcr_id",
        ]

        # yield from FlexibleAttribute.objects.order_by("name").all()
        all_options = [
            x
            for x in HOUSEHOLD_EDIT_ONLY_FIELDS + CORE_FIELDS_ATTRIBUTES
            if x.get("associated_with") == _HOUSEHOLD and x.get("name") in ACCEPTABLE_FIELDS
        ] + list(FlexibleAttribute.objects.filter(associated_with=FlexibleAttribute.ASSOCIATED_WITH_HOUSEHOLD))

        return sort_by_attr(all_options, "label.English(EN)")

    @chart_permission_decorator(permissions=[Permissions.DASHBOARD_VIEW_COUNTRY])
    def resolve_chart_grievances(self, info, business_area_slug, year, **kwargs):
        grievance_tickets = chart_get_filtered_qs(
            GrievanceTicket,
            year,
            business_area_slug_filter={"business_area__slug": business_area_slug},
        )

        filters = chart_filters_decoder(kwargs)
        if filters.get("administrative_area") is not None:
            try:
                grievance_tickets = grievance_tickets.filter(
                    admin2_new=Area.objects.get(id=filters.get("administrative_area")).name
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
