from typing import Any, Dict, Iterable, List, Optional, Tuple, Type

from django.core.exceptions import PermissionDenied
from django.db.models import (
    Case,
    F,
    Func,
    Model,
    OuterRef,
    Prefetch,
    Q,
    QuerySet,
    Subquery,
    Sum,
    Value,
    When,
)
from django.db.models.functions import Coalesce

import graphene
from graphene import Boolean, DateTime, Enum, Int, String, relay
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from hct_mis_api.apps.account.permissions import (
    ALL_GRIEVANCES_CREATE_MODIFY,
    AdminUrlNodeMixin,
    BaseNodePermissionMixin,
    BasePermission,
    DjangoPermissionFilterConnectionField,
    DjangoPermissionFilterFastConnectionField,
    Permissions,
    hopeOneOfPermissionClass,
    hopePermissionClass,
)
from hct_mis_api.apps.core.countries import Countries
from hct_mis_api.apps.core.decorators import cached_in_django_cache
from hct_mis_api.apps.core.extended_connection import ExtendedConnection
from hct_mis_api.apps.core.models import BusinessArea, FlexibleAttribute
from hct_mis_api.apps.core.schema import ChoiceObject, FieldAttributeNode
from hct_mis_api.apps.core.utils import (
    chart_filters_decoder,
    chart_permission_decorator,
    encode_ids,
    get_model_choices_fields,
    get_program_id_from_headers,
    resolve_flex_fields_choices_to_string,
    sum_lists_with_values,
    to_choice_object,
)
from hct_mis_api.apps.geo.schema import AreaNode
from hct_mis_api.apps.grievance.models import GrievanceTicket
from hct_mis_api.apps.household.filters import (
    HouseholdFilter,
    IndividualFilter,
    MergedHouseholdFilter,
    MergedIndividualFilter,
)
from hct_mis_api.apps.household.models import (
    AGENCY_TYPE_CHOICES,
    DUPLICATE,
    DUPLICATE_IN_BATCH,
    INDIVIDUAL_FLAGS_CHOICES,
    MARITAL_STATUS_CHOICE,
    NEEDS_ADJUDICATION,
    OBSERVED_DISABILITY_CHOICE,
    RELATIONSHIP_CHOICE,
    RESIDENCE_STATUS_CHOICE,
    ROLE_CHOICE,
    ROLE_NO_ROLE,
    SEVERITY_OF_DISABILITY_CHOICES,
    SEX_CHOICE,
    STATUS_ACTIVE,
    STATUS_INACTIVE,
    WORK_STATUS_CHOICE,
    BankAccountInfo,
    Document,
    DocumentType,
    Household,
    Individual,
    IndividualIdentity,
    IndividualRoleInHousehold,
)
from hct_mis_api.apps.household.services.household_programs_with_delivered_quantity import (
    delivered_quantity_service,
)
from hct_mis_api.apps.payment.models import Account
from hct_mis_api.apps.payment.utils import get_payment_items_for_dashboard
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.registration_data.nodes import (
    DeduplicationEngineSimilarityPairIndividualNode,
    DeduplicationResultNode,
)
from hct_mis_api.apps.utils.graphql import does_path_exist_in_query
from hct_mis_api.apps.utils.schema import (
    ChartDatasetNode,
    ChartDetailedDatasetsNode,
    FlexFieldsScalar,
    SectionTotalNode,
)

INDIVIDUALS_CHART_LABELS = [
    "Females 0-5",
    "Females 6-11",
    "Females 12-17",
    "Females 18-59",
    "Females 60+",
    "Males 0-5",
    "Males 6-11",
    "Males 12-17",
    "Males 18-59",
    "Males 60+",
]


class DocumentTypeNode(DjangoObjectType):
    class Meta:
        model = DocumentType


class IndividualIdentityNode(DjangoObjectType):
    partner = graphene.String(description="Partner")
    country = graphene.String(description="Individual Identity country")
    country_iso3 = graphene.String(description="Individual Identity country iso3")

    @staticmethod
    def resolve_partner(parent: IndividualIdentity, info: Any) -> str:
        return getattr(parent.partner, "name", "")

    @staticmethod
    def resolve_country(parent: IndividualIdentity, info: Any) -> str:
        return getattr(parent.country, "name", "")

    @staticmethod
    def resolve_country_iso3(parent: IndividualIdentity, info: Any) -> str:
        return getattr(parent.country, "iso_code3", "")

    class Meta:
        model = IndividualIdentity
        filter_fields = []
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class DocumentNode(DjangoObjectType):
    country = graphene.String(description="Document country")
    country_iso3 = graphene.String(description="Country ISO3")
    photo = graphene.String(description="Photo url")

    @staticmethod
    def resolve_country(parent: Document, info: Any) -> str:
        return getattr(parent.country, "name", "")

    @staticmethod
    def resolve_country_iso3(parent: Document, info: Any) -> str:
        return getattr(parent.country, "iso_code3", "")

    @staticmethod
    def resolve_photo(parent: Document, info: Any) -> Optional[String]:
        return parent.photo.url if parent.photo else None

    class Meta:
        model = Document
        filter_fields = []
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class ExtendedHouseHoldConnection(graphene.Connection):
    class Meta:
        abstract = True

    total_count = graphene.Int()
    individuals_count = graphene.Int()
    edge_count = graphene.Int()

    def resolve_total_count(root, info: Any, **kwargs: Any) -> int:
        return root.length

    def resolve_edge_count(root, info: Any, **kwargs: Any) -> int:
        return len(root.edges)

    def resolve_individuals_count(root, info: Any, **kwargs: Any) -> int:
        return root.iterable.aggregate(sum=Sum("size")).get("sum")


class DeliveredQuantityNode(graphene.ObjectType):
    total_delivered_quantity = graphene.Decimal()
    currency = graphene.String()


class IndividualRoleInHouseholdNode(DjangoObjectType):
    class Meta:
        model = IndividualRoleInHousehold


class BankAccountInfoNode(DjangoObjectType):
    type = graphene.String(required=False)

    class Meta:
        model = BankAccountInfo
        exclude = ("debit_card_number",)
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class AccountsNode(BaseNodePermissionMixin, DjangoObjectType):
    permission_classes = (hopePermissionClass(Permissions.POPULATION_VIEW_INDIVIDUAL_DELIVERY_MECHANISMS_SECTION),)

    name = graphene.String(required=False)
    individual_tab_data = graphene.JSONString()

    def resolve_name(self, info: Any) -> str:
        return self.account_type.label

    def resolve_individual_tab_data(self, info: Any) -> dict:
        data = dict(sorted(self.data.items()))
        if self.number:
            data["number"] = self.number
        if self.financial_institution:
            data["financial_institution"] = self.financial_institution.code
        return data

    class Meta:
        model = Account
        exclude = ("unique_key", "signature_hash")
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class IndividualNode(BaseNodePermissionMixin, AdminUrlNodeMixin, DjangoObjectType):
    permission_classes: Tuple[Type[BasePermission], ...] = (
        hopePermissionClass(Permissions.POPULATION_VIEW_INDIVIDUALS_DETAILS),
        hopePermissionClass(Permissions.GRIEVANCES_VIEW_INDIVIDUALS_DETAILS),
        hopePermissionClass(Permissions.GRIEVANCES_VIEW_INDIVIDUALS_DETAILS_AS_CREATOR),
        hopePermissionClass(Permissions.GRIEVANCES_VIEW_INDIVIDUALS_DETAILS_AS_OWNER),
        hopePermissionClass(Permissions.RDI_VIEW_DETAILS),
    )
    status = graphene.String()
    estimated_birth_date = graphene.Boolean(required=False)
    role = graphene.String()
    flex_fields = FlexFieldsScalar()
    deduplication_golden_record_results = graphene.List(DeduplicationResultNode)
    deduplication_batch_results = graphene.List(DeduplicationResultNode)
    biometric_deduplication_golden_record_results = graphene.List(DeduplicationEngineSimilarityPairIndividualNode)
    biometric_deduplication_batch_results = graphene.List(DeduplicationEngineSimilarityPairIndividualNode)
    observed_disability = graphene.List(graphene.String)
    relationship = graphene.Enum(
        "IndividualRelationship",
        [(x[0], x[0]) for x in RELATIONSHIP_CHOICE],
    )
    photo = graphene.String()
    age = graphene.Int()
    bank_account_info = graphene.Field(BankAccountInfoNode, required=False)
    sanction_list_last_check = graphene.DateTime()
    phone_no_valid = graphene.Boolean()
    phone_no_alternative_valid = graphene.Boolean()
    payment_channels = graphene.List(BankAccountInfoNode)
    preferred_language = graphene.String()
    accounts = graphene.List(AccountsNode)
    email = graphene.String(source="email")
    import_id = graphene.String()

    documents = DjangoFilterConnectionField(
        DocumentNode,
    )
    identities = DjangoFilterConnectionField(
        IndividualIdentityNode,
    )

    @classmethod
    def get_node(cls, info: Any, object_id: str, **kwargs: Any) -> Optional[Model]:
        return super().get_node(info, object_id, get_object_queryset=Individual.all_merge_status_objects)

    @staticmethod
    def resolve_documents(parent: Individual, info: Any) -> QuerySet[Document]:
        return parent.documents(manager="all_merge_status_objects")

    @staticmethod
    def resolve_identities(parent: Individual, info: Any) -> QuerySet[IndividualIdentity]:
        return parent.identities(manager="all_merge_status_objects")

    @staticmethod
    def resolve_import_id(parent: Individual, info: Any) -> str:
        return f"{parent.unicef_id} (Detail ID {parent.detail_id})" if parent.detail_id else parent.unicef_id

    @staticmethod
    def resolve_preferred_language(parent: Individual, info: Any) -> Optional[str]:
        return parent.get_preferred_language_display()

    @staticmethod
    def resolve_payment_channels(parent: Individual, info: Any) -> QuerySet[BankAccountInfo]:
        return BankAccountInfo.all_merge_status_objects.filter(individual=parent).annotate(type=Value("BANK_TRANSFER"))

    def resolve_bank_account_info(parent, info: Any) -> Optional[BankAccountInfo]:
        bank_account_info = parent.bank_account_info(manager="all_merge_status_objects").first()  # type: ignore
        if bank_account_info:
            return bank_account_info
        return None

    def resolve_role(parent, info: Any) -> str:
        role = parent.households_and_roles(manager="all_merge_status_objects").first()
        if role is not None:
            return role.role
        return ROLE_NO_ROLE

    def resolve_deduplication_golden_record_results(parent, info: Any) -> List[Dict]:
        key = "duplicates" if parent.deduplication_golden_record_status == DUPLICATE else "possible_duplicates"
        results = parent.deduplication_golden_record_results.get(key, {})
        return encode_ids(results, "Individual", "hit_id")

    def resolve_deduplication_batch_results(parent, info: Any) -> List[Dict]:
        key = "duplicates" if parent.deduplication_batch_status == DUPLICATE_IN_BATCH else "possible_duplicates"
        results = parent.deduplication_batch_results.get(key, {})
        return encode_ids(results, "Individual", "hit_id")

    def resolve_relationship(parent, info: Any) -> Optional[Enum]:
        # custom resolver so when relationship value is empty string, query does not break (since empty string is not one of enum choices, we need to return None)
        if not parent.relationship:
            return None
        return parent.relationship

    def resolve_photo(parent, info: Any) -> Optional[str]:
        if parent.photo:
            return parent.photo.url
        return None

    def resolve_flex_fields(parent, info: Any) -> Dict:
        return resolve_flex_fields_choices_to_string(parent)

    def resolve_age(parent, info: Any) -> Int:
        return parent.age

    def resolve_sanction_list_last_check(parent, info: Any) -> DateTime:
        return parent.sanction_list_last_check

    def resolve_phone_no_valid(parent, info: Any) -> Boolean:
        return parent.phone_no_valid

    def resolve_phone_no_alternative_valid(parent, info: Any) -> Boolean:
        return parent.phone_no_alternative_valid

    def resolve_accounts(parent, info: Any) -> QuerySet[Account]:
        program_id = get_program_id_from_headers(info.context.headers)
        if not info.context.user.has_permission(
            Permissions.POPULATION_VIEW_INDIVIDUAL_DELIVERY_MECHANISMS_SECTION.value,
            parent.business_area,
            program_id,
        ):
            return parent.accounts.none()
        return parent.accounts(manager="all_objects").all()

    @classmethod
    def check_node_permission(cls, info: Any, object_instance: Individual) -> None:
        super().check_node_permission(info, object_instance)
        user = info.context.user
        program_id = get_program_id_from_headers(info.context.headers)

        if not user.partner.is_unicef:
            if program_id and str(object_instance.program_id) != program_id:
                raise PermissionDenied("Permission Denied")
            if not user.partner.has_program_access(object_instance.program_id):
                raise PermissionDenied("Permission Denied")
            if object_instance.household_id and object_instance.household.admin_area_id:
                areas_from_partner = user.partner.get_program_areas(object_instance.program_id)
                household = object_instance.household
                areas_from_household = [
                    household.admin1_id,
                    household.admin2_id,
                    household.admin3_id,
                ]
                if not areas_from_partner.filter(id__in=areas_from_household).exists():
                    raise PermissionDenied("Permission Denied")

        # if user can't simply view all individuals, we check if they can do it because of grievance or rdi details
        if not user.has_permission(
            Permissions.POPULATION_VIEW_INDIVIDUALS_DETAILS.value,
            object_instance.business_area,
            object_instance.program_id,
        ) and not user.has_permission(
            Permissions.RDI_VIEW_DETAILS.value,
            object_instance.business_area,
            object_instance.program_id,
        ):
            grievance_tickets = GrievanceTicket.objects.filter(
                complaint_ticket_details__in=object_instance.complaint_ticket_details.all()
            )
            cls.check_creator_or_owner_permission(
                info,
                object_instance,
                Permissions.GRIEVANCES_VIEW_INDIVIDUALS_DETAILS.value,
                any(user_ticket in user.created_tickets.all() for user_ticket in grievance_tickets),
                Permissions.GRIEVANCES_VIEW_INDIVIDUALS_DETAILS_AS_CREATOR.value,
                any(user_ticket in user.assigned_tickets.all() for user_ticket in grievance_tickets),
                Permissions.GRIEVANCES_VIEW_INDIVIDUALS_DETAILS_AS_OWNER.value,
            )

    class Meta:
        model = Individual
        exclude = ("vector_column",)
        filter_fields = []
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection
        convert_choices_to_enum = get_model_choices_fields(
            Individual,
            excluded=[
                "seeing_disability",
                "hearing_disability",
                "physical_disability",
                "memory_disability",
                "selfcare_disability",
                "comms_disability",
                "work_status",
            ],
        )


class HouseholdNode(BaseNodePermissionMixin, AdminUrlNodeMixin, DjangoObjectType):
    permission_classes = (
        hopePermissionClass(Permissions.POPULATION_VIEW_HOUSEHOLDS_DETAILS),
        hopePermissionClass(Permissions.GRIEVANCES_VIEW_HOUSEHOLD_DETAILS),
        hopePermissionClass(Permissions.GRIEVANCES_VIEW_HOUSEHOLD_DETAILS_AS_CREATOR),
        hopePermissionClass(Permissions.GRIEVANCES_VIEW_HOUSEHOLD_DETAILS_AS_OWNER),
        hopePermissionClass(Permissions.RDI_VIEW_DETAILS),
    )
    total_cash_received = graphene.Decimal()
    total_cash_received_usd = graphene.Decimal()
    country_origin = graphene.String(description="Country origin name")
    country = graphene.String(description="Country name")
    currency = graphene.String()
    flex_fields = FlexFieldsScalar()
    sanction_list_possible_match = graphene.Boolean()
    sanction_list_confirmed_match = graphene.Boolean()
    has_duplicates = graphene.Boolean(description="Mark household if any of individuals has Duplicate status")
    has_duplicates_for_rdi = graphene.Boolean(
        description="Mark household if any of individuals has Duplicate or Duplicate In Batch or Needs Adjudication"
    )
    consent_sharing = graphene.List(graphene.String)
    admin_area = graphene.Field(AreaNode)
    admin_area_title = graphene.String(description="Admin area title")
    admin1 = graphene.Field(AreaNode)
    admin2 = graphene.Field(AreaNode)
    status = graphene.String()
    delivered_quantities = graphene.List(DeliveredQuantityNode)
    active_individuals_count = graphene.Int()
    individuals = DjangoFilterConnectionField(
        IndividualNode,
        filterset_class=IndividualFilter,
    )
    residence_status = graphene.String()
    program_registration_id = graphene.String()
    import_id = graphene.String()
    geopoint = graphene.String()

    @staticmethod
    def resolve_sanction_list_possible_match(parent: Household, info: Any) -> bool:
        if hasattr(parent, "sanction_list_possible_match_annotated"):
            return parent.sanction_list_possible_match_annotated
        return parent.sanction_list_possible_match

    @staticmethod
    def resolve_sanction_list_confirmed_match(parent: Household, info: Any) -> bool:
        if hasattr(parent, "sanction_list_confirmed_match_annotated"):
            return parent.sanction_list_confirmed_match_annotated
        return parent.sanction_list_confirmed_match

    @staticmethod
    def resolve_admin_area_title(parent: Household, info: Any) -> str:
        if parent.admin_area:
            return f"{parent.admin_area.name} - {parent.admin_area.p_code}"
        return ""

    @staticmethod
    def resolve_delivered_quantities(parent: Household, info: Any) -> List[Dict[str, Any]]:
        return delivered_quantity_service(parent)

    @staticmethod
    def resolve_country(parent: Household, info: Any) -> str:
        return getattr(parent.country, "name", "")

    @staticmethod
    def resolve_country_origin(parent: Household, info: Any) -> str:
        return getattr(parent.country_origin, "name", "")

    @staticmethod
    def resolve_individuals(parent: Household, info: Any, *arg: Any, **kwargs: Any) -> QuerySet:
        individuals_ids = list(parent.individuals(manager="all_merge_status_objects").values_list("id", flat=True))

        collectors_ids = list(parent.representatives(manager="all_merge_status_objects").values_list("id", flat=True))
        ids = list(set(individuals_ids + collectors_ids))
        return Individual.all_merge_status_objects.filter(id__in=ids).prefetch_related(
            Prefetch(
                "households_and_roles",
                queryset=IndividualRoleInHousehold.all_merge_status_objects.filter(household=parent.id),
            )
        )

    @staticmethod
    def resolve_has_duplicates(parent: Household, info: Any) -> bool:
        if hasattr(parent, "has_duplicates_annotated"):
            return parent.has_duplicates_annotated
        return parent.individuals.filter(deduplication_golden_record_status=DUPLICATE).exists()

    @staticmethod
    def resolve_has_duplicates_for_rdi(parent: Household, info: Any) -> bool:
        return parent.individuals.filter(
            Q(deduplication_batch_status=DUPLICATE_IN_BATCH)
            | Q(deduplication_golden_record_status__in=(DUPLICATE, NEEDS_ADJUDICATION))
        ).exists()

    @staticmethod
    def resolve_flex_fields(parent: Household, info: Any) -> Dict:
        return resolve_flex_fields_choices_to_string(parent)

    @staticmethod
    def resolve_active_individuals_count(parent: Household, info: Any) -> int:
        return parent.active_individuals.count()

    @staticmethod
    def resolve_program_registration_id(parent: Household, info: Any) -> Optional[str]:
        if not parent.program_registration_id:
            return None
        return parent.program_registration_id.split("#")[0]

    @classmethod
    def check_node_permission(cls, info: Any, object_instance: Household) -> None:
        super().check_node_permission(info, object_instance)
        user = info.context.user
        program_id = get_program_id_from_headers(info.context.headers)

        if not user.partner.is_unicef:
            if program_id and str(object_instance.program_id) != program_id:
                raise PermissionDenied("Permission Denied")
            if not user.partner.has_program_access(object_instance.program_id):
                raise PermissionDenied("Permission Denied")
            if object_instance.admin_area_id:
                areas_from_partner = user.partner.get_program_areas(object_instance.program_id)
                areas_from_household = [object_instance.admin1_id, object_instance.admin2_id, object_instance.admin3_id]
                if not areas_from_partner.filter(id__in=areas_from_household).exists():
                    raise PermissionDenied("Permission Denied")

        # if user doesn't have permission to view all households or RDI details, we check based on their grievance tickets
        if not user.has_permission(
            Permissions.POPULATION_VIEW_HOUSEHOLDS_DETAILS.value,
            object_instance.business_area,
            object_instance.program_id,
        ) and not user.has_permission(
            Permissions.RDI_VIEW_DETAILS.value,
            object_instance.business_area,
            object_instance.program_id,
        ):
            grievance_tickets = GrievanceTicket.objects.filter(
                complaint_ticket_details__in=object_instance.complaint_ticket_details.all()
            )
            cls.check_creator_or_owner_permission(
                info,
                object_instance,
                Permissions.GRIEVANCES_VIEW_HOUSEHOLD_DETAILS.value,
                any(user_ticket in user.created_tickets.all() for user_ticket in grievance_tickets),
                Permissions.GRIEVANCES_VIEW_HOUSEHOLD_DETAILS_AS_CREATOR.value,
                any(user_ticket in user.assigned_tickets.all() for user_ticket in grievance_tickets),
                Permissions.GRIEVANCES_VIEW_HOUSEHOLD_DETAILS_AS_OWNER.value,
            )

    @staticmethod
    def resolve_import_id(parent: Household, info: Any) -> str:
        if parent.detail_id:
            return f"{parent.unicef_id} (Detail id {parent.detail_id})"
        if parent.enumerator_rec_id:
            return f"{parent.unicef_id} (Enumerator ID {parent.enumerator_rec_id})"

        return parent.unicef_id

    @classmethod
    def get_queryset(cls, queryset: QuerySet[Household], info: Any) -> QuerySet[Household]:
        queryset = queryset.annotate(
            status_label=Case(
                When(withdrawn=True, then=Value(STATUS_INACTIVE)),
                default=Value(STATUS_ACTIVE),
            )
        )
        qs = super().get_queryset(queryset, info)
        return qs

    @classmethod
    def get_node(cls, info: Any, object_id: str, **kwargs: Any) -> Optional[Model]:
        return super().get_node(info, object_id, get_object_queryset=Household.all_merge_status_objects)

    class Meta:
        model = Household
        filter_fields = []
        interfaces = (relay.Node,)
        connection_class = ExtendedHouseHoldConnection


class Query(graphene.ObjectType):
    household = relay.Node.Field(HouseholdNode)
    all_households = DjangoPermissionFilterConnectionField(
        HouseholdNode,
        filterset_class=HouseholdFilter,
        permission_classes=(
            hopeOneOfPermissionClass(
                Permissions.RDI_VIEW_DETAILS, Permissions.POPULATION_VIEW_HOUSEHOLDS_LIST, *ALL_GRIEVANCES_CREATE_MODIFY
            ),
        ),
    )
    individual = relay.Node.Field(IndividualNode)
    all_individuals = DjangoPermissionFilterConnectionField(
        IndividualNode,
        filterset_class=IndividualFilter,
        permission_classes=(
            hopeOneOfPermissionClass(
                Permissions.RDI_VIEW_DETAILS,
                Permissions.POPULATION_VIEW_INDIVIDUALS_LIST,
                *ALL_GRIEVANCES_CREATE_MODIFY,
            ),
        ),
    )

    # Emulation of imported_households query to switch links when RDI merged
    all_merged_households = DjangoPermissionFilterFastConnectionField(
        HouseholdNode,
        filterset_class=MergedHouseholdFilter,
        permission_classes=(hopeOneOfPermissionClass(Permissions.RDI_VIEW_DETAILS),),
    )

    # Emulation of imported_households query to switch links when RDI merged
    all_merged_individuals = DjangoPermissionFilterFastConnectionField(
        IndividualNode,
        filterset_class=MergedIndividualFilter,
        permission_classes=(hopeOneOfPermissionClass(Permissions.RDI_VIEW_DETAILS),),
    )

    section_households_reached = graphene.Field(
        SectionTotalNode,
        business_area_slug=graphene.String(required=True),
        year=graphene.Int(required=True),
        program=graphene.String(required=False),
        administrative_area=graphene.String(required=False),
    )
    section_individuals_reached = graphene.Field(
        SectionTotalNode,
        business_area_slug=graphene.String(required=True),
        year=graphene.Int(required=True),
        program=graphene.String(required=False),
        administrative_area=graphene.String(required=False),
    )
    section_people_reached = graphene.Field(
        SectionTotalNode,
        business_area_slug=graphene.String(required=True),
        year=graphene.Int(required=True),
        program=graphene.String(required=False),
        administrative_area=graphene.String(required=False),
    )
    section_child_reached = graphene.Field(
        SectionTotalNode,
        business_area_slug=graphene.String(required=True),
        year=graphene.Int(required=True),
        program=graphene.String(required=False),
        administrative_area=graphene.String(required=False),
    )
    chart_individuals_reached_by_age_and_gender = graphene.Field(
        ChartDatasetNode,
        business_area_slug=graphene.String(required=True),
        year=graphene.Int(required=True),
        program=graphene.String(required=False),
        administrative_area=graphene.String(required=False),
    )
    chart_people_reached_by_age_and_gender = graphene.Field(
        ChartDatasetNode,
        business_area_slug=graphene.String(required=True),
        year=graphene.Int(required=True),
        program=graphene.String(required=False),
        administrative_area=graphene.String(required=False),
    )
    chart_individuals_with_disability_reached_by_age = graphene.Field(
        ChartDetailedDatasetsNode,
        business_area_slug=graphene.String(required=True),
        year=graphene.Int(required=True),
        program=graphene.String(required=False),
        administrative_area=graphene.String(required=False),
    )
    chart_people_with_disability_reached_by_age = graphene.Field(
        ChartDetailedDatasetsNode,
        business_area_slug=graphene.String(required=True),
        year=graphene.Int(required=True),
        program=graphene.String(required=False),
        administrative_area=graphene.String(required=False),
    )

    residence_status_choices = graphene.List(ChoiceObject)
    sex_choices = graphene.List(ChoiceObject)
    marital_status_choices = graphene.List(ChoiceObject)
    work_status_choices = graphene.List(ChoiceObject)
    relationship_choices = graphene.List(ChoiceObject)
    role_choices = graphene.List(ChoiceObject)
    document_type_choices = graphene.List(ChoiceObject)
    identity_type_choices = graphene.List(ChoiceObject)
    countries_choices = graphene.List(ChoiceObject)
    observed_disability_choices = graphene.List(ChoiceObject)
    severity_of_disability_choices = graphene.List(ChoiceObject)
    flag_choices = graphene.List(ChoiceObject)

    all_households_flex_fields_attributes = graphene.List(FieldAttributeNode)
    all_individuals_flex_fields_attributes = graphene.List(FieldAttributeNode)

    def resolve_all_individuals(self, info: Any, **kwargs: Any) -> QuerySet[Individual]:
        user = info.context.user
        program_id = get_program_id_from_headers(info.context.headers)
        business_area_slug = info.context.headers.get("Business-Area")

        if program_id:
            program = Program.objects.filter(id=program_id).first()
            if program and program.status == Program.DRAFT:
                return Individual.objects.none()

        queryset = Individual.all_merge_status_objects.all()
        if does_path_exist_in_query("edges.node.household", info):
            queryset = queryset.select_related("household")
        if does_path_exist_in_query("edges.node.household.admin2", info):
            queryset = queryset.select_related("household__admin2")
            queryset = queryset.select_related("household__admin2__area_type")
        if does_path_exist_in_query("edges.node.program", info):
            queryset = queryset.select_related("program")

        if not user.partner.is_unicef:  # Unicef partner has full access to all AdminAreas
            business_area_id = BusinessArea.objects.get(slug=business_area_slug).id
            programs_for_business_area = []

            if program_id and user.partner.has_program_access(program_id):
                programs_for_business_area = [program_id]
            elif not program_id:
                programs_for_business_area = user.partner.get_program_ids_for_business_area(business_area_id)
            if not programs_for_business_area:
                return Individual.objects.none()
            programs_permissions = [
                (program_id, user.partner.get_program_areas(program_id)) for program_id in programs_for_business_area
            ]

            filter_q = Q()
            for program_id, areas_ids in programs_permissions:
                areas_query = Q(
                    Q(household__admin1__in=areas_ids)
                    | Q(household__admin2__in=areas_ids)
                    | Q(household__admin3__in=areas_ids)
                    | Q(household__admin_area__isnull=True)
                )
                filter_q |= Q(Q(program_id=program_id) & areas_query)

            queryset = queryset.filter(filter_q)
        return queryset

    def resolve_all_households_flex_fields_attributes(self, info: Any, **kwargs: Any) -> Iterable:
        yield from FlexibleAttribute.objects.filter(
            associated_with=FlexibleAttribute.ASSOCIATED_WITH_HOUSEHOLD
        ).prefetch_related("choices").order_by("created_at")

    def resolve_all_individuals_flex_fields_attributes(self, info: Any, **kwargs: Any) -> Iterable:
        yield from FlexibleAttribute.objects.filter(
            associated_with=FlexibleAttribute.ASSOCIATED_WITH_INDIVIDUAL
        ).exclude(type=FlexibleAttribute.PDU).prefetch_related("choices").order_by("created_at")

    def resolve_all_households(self, info: Any, **kwargs: Any) -> QuerySet:
        user = info.context.user
        program_id = get_program_id_from_headers(info.context.headers)
        business_area_slug = info.context.headers.get("Business-Area")

        if program_id:
            program = Program.objects.filter(id=program_id).first()
            if program and program.status == Program.DRAFT:
                return Household.objects.none()

        queryset = Household.all_merge_status_objects.all()

        if not user.partner.is_unicef:  # Unicef partner has full access to all AdminAreas
            business_area_id = BusinessArea.objects.get(slug=business_area_slug).id
            programs_for_business_area = []

            if program_id and user.partner.has_program_access(program_id):
                programs_for_business_area = [program_id]
            elif not program_id:
                programs_for_business_area = user.partner.get_program_ids_for_business_area(business_area_id)
            if not programs_for_business_area:
                return Household.objects.none()
            programs_permissions = [
                (program_id, user.partner.get_program_areas(program_id)) for program_id in programs_for_business_area
            ]

            filter_q = Q()
            for program_id, areas_ids in programs_permissions:
                areas_query = Q(
                    Q(admin1__in=areas_ids)
                    | Q(admin2__in=areas_ids)
                    | Q(admin3__in=areas_ids)
                    | Q(admin_area__isnull=True)
                )
                filter_q |= Q(Q(program_id=program_id) & areas_query)

            queryset = queryset.filter(filter_q)

        if does_path_exist_in_query("edges.node.admin2", info):
            queryset = queryset.select_related("admin_area")
            queryset = queryset.select_related("admin_area__area_type")

        if does_path_exist_in_query("edges.node.headOfHousehold", info):
            queryset = queryset.select_related("head_of_household")
        if does_path_exist_in_query("edges.node.program", info):
            queryset = queryset.select_related("program")
        if does_path_exist_in_query("edges.node.hasDuplicates", info):
            subquery = Subquery(
                Individual.objects.filter(household_id=OuterRef("pk"), deduplication_golden_record_status="DUPLICATE")
                .annotate(count=Func(F("id"), function="Count"))
                .values("count")
            )
            queryset = queryset.annotate(has_duplicates_annotated=subquery)

        if does_path_exist_in_query("edges.node.sanctionListPossibleMatch", info):
            subquery = Subquery(
                Individual.objects.filter(household_id=OuterRef("pk"), sanction_list_possible_match=True)
                .annotate(count=Func(F("id"), function="Count"))
                .values("count")
            )
            queryset = queryset.annotate(sanction_list_possible_match_annotated=subquery)
        if does_path_exist_in_query("edges.node.sanctionListConfirmedMatch", info):
            subquery = Subquery(
                Individual.objects.filter(household_id=OuterRef("pk"), sanction_list_confirmed_match=True)
                .annotate(count=Func(F("id"), function="Count"))
                .values("count")
            )
            queryset = queryset.annotate(sanction_list_confirmed_match_annotated=subquery)
        return queryset

    def resolve_residence_status_choices(self, info: Any, **kwargs: Any) -> List[Dict[str, Any]]:
        return to_choice_object(RESIDENCE_STATUS_CHOICE)

    def resolve_sex_choices(self, info: Any, **kwargs: Any) -> List[Dict[str, Any]]:
        return to_choice_object(SEX_CHOICE)

    def resolve_marital_status_choices(self, info: Any, **kwargs: Any) -> List[Dict[str, Any]]:
        return to_choice_object(MARITAL_STATUS_CHOICE)

    def resolve_relationship_choices(self, info: Any, **kwargs: Any) -> List[Dict[str, Any]]:
        return to_choice_object(RELATIONSHIP_CHOICE)

    def resolve_role_choices(self, info: Any, **kwargs: Any) -> List[Dict[str, Any]]:
        return to_choice_object(ROLE_CHOICE)

    def resolve_document_type_choices(self, info: Any, **kwargs: Any) -> List[Dict[str, Any]]:
        return [{"name": x.label, "value": x.key} for x in DocumentType.objects.all()]

    def resolve_identity_type_choices(self, info: Any, **kwargs: Any) -> List[Dict[str, Any]]:
        return to_choice_object(AGENCY_TYPE_CHOICES)

    def resolve_countries_choices(self, info: Any, **kwargs: Any) -> List[Dict[str, Any]]:
        return to_choice_object([(alpha3, label) for (label, alpha2, alpha3) in Countries.get_countries()])

    def resolve_severity_of_disability_choices(self, info: Any, **kwargs: Any) -> List[Dict[str, Any]]:
        return to_choice_object(SEVERITY_OF_DISABILITY_CHOICES)

    def resolve_observed_disability_choices(self, info: Any, **kwargs: Any) -> List[Dict[str, Any]]:
        return to_choice_object(OBSERVED_DISABILITY_CHOICE)

    def resolve_flag_choices(self, info: Any, **kwargs: Any) -> List[Dict[str, Any]]:
        return to_choice_object(INDIVIDUAL_FLAGS_CHOICES)

    def resolve_work_status_choices(self, info: Any, **kwargs: Any) -> List[Dict[str, Any]]:
        return to_choice_object(WORK_STATUS_CHOICE)

    def resolve_deduplication_status_choices(self, info: Any, **kwargs: Any) -> List[Dict[str, Any]]:
        return to_choice_object(WORK_STATUS_CHOICE)

    @chart_permission_decorator(permissions=[Permissions.DASHBOARD_VIEW_COUNTRY])
    @cached_in_django_cache(24)
    def resolve_section_households_reached(
        self, info: Any, business_area_slug: str, year: int, **kwargs: Any
    ) -> Dict[str, int]:
        payment_items_qs: "QuerySet" = get_payment_items_for_dashboard(
            year, business_area_slug, chart_filters_decoder(kwargs), True
        ).filter(household__collect_type=Household.CollectType.STANDARD.value)
        return {"total": payment_items_qs.values_list("household", flat=True).distinct().count()}

    @chart_permission_decorator(permissions=[Permissions.DASHBOARD_VIEW_COUNTRY])
    @cached_in_django_cache(24)
    def resolve_section_individuals_reached(
        self, info: Any, business_area_slug: str, year: int, **kwargs: Any
    ) -> Dict[str, int]:
        payment_items_qs: "QuerySet" = get_payment_items_for_dashboard(
            year, business_area_slug, chart_filters_decoder(kwargs), True
        ).filter(household__collect_type=Household.CollectType.STANDARD.value)
        households_ids = payment_items_qs.values_list("household", flat=True).distinct()
        return Household.objects.filter(pk__in=households_ids).aggregate(total=Sum(Coalesce("size", 0)))

    @chart_permission_decorator(permissions=[Permissions.DASHBOARD_VIEW_COUNTRY])
    @cached_in_django_cache(24)
    def resolve_section_people_reached(
        self, info: Any, business_area_slug: str, year: int, **kwargs: Any
    ) -> Dict[str, int]:
        payment_items_qs: "QuerySet" = get_payment_items_for_dashboard(
            year, business_area_slug, chart_filters_decoder(kwargs), True
        ).filter(household__collect_type=Household.CollectType.SINGLE.value)
        people_count = payment_items_qs.values("household").distinct().count()
        return {"total": people_count}

    @chart_permission_decorator(permissions=[Permissions.DASHBOARD_VIEW_COUNTRY])
    @cached_in_django_cache(24)
    def resolve_section_child_reached(
        self, info: Any, business_area_slug: str, year: int, **kwargs: Any
    ) -> Dict[str, int]:
        households_child_params = [
            "female_age_group_0_5_count",
            "female_age_group_6_11_count",
            "female_age_group_12_17_count",
            "male_age_group_0_5_count",
            "male_age_group_6_11_count",
            "male_age_group_12_17_count",
        ]
        payment_items_qs: "QuerySet" = get_payment_items_for_dashboard(
            year, business_area_slug, chart_filters_decoder(kwargs), True
        )
        households_ids = payment_items_qs.values_list("household", flat=True).distinct()
        household_child_counts = Household.objects.filter(pk__in=households_ids).values_list(*households_child_params)
        return {"total": sum(sum_lists_with_values(household_child_counts, len(households_child_params)))}

    @chart_permission_decorator(permissions=[Permissions.DASHBOARD_VIEW_COUNTRY])
    @cached_in_django_cache(24)
    def resolve_chart_individuals_reached_by_age_and_gender(
        self, info: Any, business_area_slug: str, year: int, **kwargs: Any
    ) -> Dict:
        households_params = [
            "female_age_group_0_5_count",
            "female_age_group_6_11_count",
            "female_age_group_12_17_count",
            "female_age_group_18_59_count",
            "female_age_group_60_count",
            "male_age_group_0_5_count",
            "male_age_group_6_11_count",
            "male_age_group_12_17_count",
            "male_age_group_18_59_count",
            "male_age_group_60_count",
        ]
        payment_items_qs: "QuerySet" = get_payment_items_for_dashboard(
            year, business_area_slug, chart_filters_decoder(kwargs), True
        ).filter(household__collect_type=Household.CollectType.STANDARD.value)
        households_ids = payment_items_qs.values_list("household", flat=True).distinct()
        household_child_counts = Household.objects.filter(pk__in=households_ids).values_list(*households_params)

        return {
            "labels": INDIVIDUALS_CHART_LABELS,
            "datasets": [{"data": sum_lists_with_values(household_child_counts, len(households_params))}],
        }

    @chart_permission_decorator(permissions=[Permissions.DASHBOARD_VIEW_COUNTRY])
    @cached_in_django_cache(24)
    def resolve_chart_people_reached_by_age_and_gender(
        self, info: Any, business_area_slug: str, year: int, **kwargs: Any
    ) -> Dict:
        households_params = [
            "female_age_group_0_5_count",
            "female_age_group_6_11_count",
            "female_age_group_12_17_count",
            "female_age_group_18_59_count",
            "female_age_group_60_count",
            "male_age_group_0_5_count",
            "male_age_group_6_11_count",
            "male_age_group_12_17_count",
            "male_age_group_18_59_count",
            "male_age_group_60_count",
        ]
        payment_items_qs: "QuerySet" = get_payment_items_for_dashboard(
            year, business_area_slug, chart_filters_decoder(kwargs), True
        ).filter(household__collect_type=Household.CollectType.SINGLE.value)
        households_ids = payment_items_qs.values_list("household", flat=True).distinct()
        household_child_counts = Household.objects.filter(pk__in=households_ids).values_list(*households_params)

        return {
            "labels": INDIVIDUALS_CHART_LABELS,
            "datasets": [{"data": sum_lists_with_values(household_child_counts, len(households_params))}],
        }

    @chart_permission_decorator(permissions=[Permissions.DASHBOARD_VIEW_COUNTRY])
    @cached_in_django_cache(24)
    def resolve_chart_individuals_with_disability_reached_by_age(
        self, info: Any, business_area_slug: str, year: int, **kwargs: Any
    ) -> Dict:
        households_params_with_disability = [
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
        ]
        households_params_total = [
            "female_age_group_0_5_count",
            "female_age_group_6_11_count",
            "female_age_group_12_17_count",
            "female_age_group_18_59_count",
            "female_age_group_60_count",
            "male_age_group_0_5_count",
            "male_age_group_6_11_count",
            "male_age_group_12_17_count",
            "male_age_group_18_59_count",
            "male_age_group_60_count",
        ]

        payment_items_qs: "QuerySet" = get_payment_items_for_dashboard(
            year, business_area_slug, chart_filters_decoder(kwargs), True
        ).filter(household__collect_type=Household.CollectType.STANDARD.value)
        households_ids = payment_items_qs.values_list("household", flat=True).distinct()

        households_with_disability_counts = Household.objects.filter(pk__in=households_ids).values_list(
            *households_params_with_disability
        )
        sum_of_with_disability = sum_lists_with_values(
            households_with_disability_counts, len(households_params_with_disability)
        )

        households_totals_counts = Household.objects.filter(pk__in=households_ids).values_list(*households_params_total)
        sum_of_totals = sum_lists_with_values(households_totals_counts, len(households_params_total))

        sum_of_without_disability = []

        for i, total in enumerate(sum_of_totals):
            if not total:
                sum_of_without_disability.append(0)
            elif not sum_of_with_disability[i]:
                sum_of_without_disability.append(total)
            else:
                sum_of_without_disability.append(total - sum_of_with_disability[i])

        datasets = [
            {"label": "with disability", "data": sum_of_with_disability},
            {"label": "without disability", "data": sum_of_without_disability},
            {"label": "total", "data": sum_of_totals},
        ]
        return {"labels": INDIVIDUALS_CHART_LABELS, "datasets": datasets}

    @chart_permission_decorator(permissions=[Permissions.DASHBOARD_VIEW_COUNTRY])
    @cached_in_django_cache(24)
    def resolve_chart_people_with_disability_reached_by_age(
        self, info: Any, business_area_slug: str, year: int, **kwargs: Any
    ) -> Dict:
        households_params_with_disability = [
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
        ]
        households_params_total = [
            "female_age_group_0_5_count",
            "female_age_group_6_11_count",
            "female_age_group_12_17_count",
            "female_age_group_18_59_count",
            "female_age_group_60_count",
            "male_age_group_0_5_count",
            "male_age_group_6_11_count",
            "male_age_group_12_17_count",
            "male_age_group_18_59_count",
            "male_age_group_60_count",
        ]

        payment_items_qs: "QuerySet" = get_payment_items_for_dashboard(
            year, business_area_slug, chart_filters_decoder(kwargs), True
        ).filter(household__collect_type=Household.CollectType.SINGLE.value)
        households_ids = payment_items_qs.values_list("household", flat=True).distinct()

        households_with_disability_counts = Household.objects.filter(pk__in=households_ids).values_list(
            *households_params_with_disability
        )
        sum_of_with_disability = sum_lists_with_values(
            households_with_disability_counts, len(households_params_with_disability)
        )

        households_totals_counts = Household.objects.filter(pk__in=households_ids).values_list(*households_params_total)
        sum_of_totals = sum_lists_with_values(households_totals_counts, len(households_params_total))

        sum_of_without_disability = []

        for i, total in enumerate(sum_of_totals):
            if not total:
                sum_of_without_disability.append(0)
            elif not sum_of_with_disability[i]:
                sum_of_without_disability.append(total)
            else:
                sum_of_without_disability.append(total - sum_of_with_disability[i])

        datasets = [
            {"label": "with disability", "data": sum_of_with_disability},
            {"label": "without disability", "data": sum_of_without_disability},
            {"label": "total", "data": sum_of_totals},
        ]
        return {"labels": INDIVIDUALS_CHART_LABELS, "datasets": datasets}
