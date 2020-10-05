import graphene
from django.db.models import Sum, Q, Prefetch
from django_filters import (
    FilterSet,
    OrderingFilter,
    CharFilter,
    MultipleChoiceFilter,
)
from graphene import relay
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from core.extended_connection import ExtendedConnection
from core.filters import AgeRangeFilter, IntegerRangeFilter
from core.schema import ChoiceObject
from core.utils import to_choice_object, encode_ids
from household.models import (
    Household,
    Individual,
    Document,
    DocumentType,
    RESIDENCE_STATUS_CHOICE,
    RELATIONSHIP_CHOICE,
    ROLE_CHOICE,
    MARITAL_STATUS_CHOICE,
    SEX_CHOICE,
    IndividualRoleInHousehold,
    ROLE_NO_ROLE,
    IndividualIdentity,
    DUPLICATE,
    DUPLICATE_IN_BATCH,
)
from registration_datahub.schema import DeduplicationResultNode
from targeting.models import HouseholdSelection


class HouseholdFilter(FilterSet):
    business_area = CharFilter(field_name="business_area__slug")
    size = IntegerRangeFilter(field_name="size")
    search = CharFilter(method="search_filter")

    class Meta:
        model = Household
        fields = {
            "business_area": ["exact"],
            "country_origin": ["exact", "icontains"],
            "address": ["exact", "icontains"],
            "head_of_household__full_name": ["exact", "icontains"],
            "size": ["range", "lte", "gte"],
            "admin_area": ["exact"],
            "target_populations": ["exact"],
            "programs": ["exact"],
            "residence_status": ["exact"],
        }

    order_by = OrderingFilter(
        fields=(
            "age",
            "sex",
            "household__id",
            "id",
            "unicef_id",
            "household_ca_id",
            "size",
            "head_of_household__full_name",
            "admin_area__title",
            "residence_status",
            "registration_data_import__name",
            "total_cash",
            "registration_date",
        )
    )

    def search_filter(self, qs, name, value):
        values = value.split(" ")
        q_obj = Q()
        for value in values:
            q_obj |= Q(head_of_household__given_name__icontains=value)
            q_obj |= Q(head_of_household__family_name__icontains=value)
            q_obj |= Q(unicef_id__icontains=value)
        return qs.filter(q_obj)


class IndividualFilter(FilterSet):
    business_area = CharFilter(field_name="household__business_area__slug",)
    age = AgeRangeFilter(field_name="birth_date")
    sex = MultipleChoiceFilter(field_name="sex", choices=SEX_CHOICE)
    programme = CharFilter(field_name="household__programs__name")
    search = CharFilter(method="search_filter")

    class Meta:
        model = Individual
        fields = {
            "programme": ["exact", "icontains"],
            "business_area": ["exact"],
            "full_name": ["exact", "icontains"],
            "age": ["range", "lte", "gte"],
            "sex": ["exact"],
        }

    order_by = OrderingFilter(
        fields=("id", "unicef_id", "full_name", "household__id", "birth_date",
                "sex", "relationship", "household__admin_area__title",)
    )

    def search_filter(self, qs, name, value):
        values = value.split(" ")
        q_obj = Q()
        for value in values:
            q_obj |= Q(household__admin_area__title__icontains=value)
            q_obj |= Q(unicef_id__icontains=value)
            q_obj |= Q(household__id__icontains=value)
            q_obj |= Q(full_name__icontains=value)
        return qs.filter(q_obj)


class DocumentTypeNode(DjangoObjectType):
    country = graphene.String(description="Country name")

    def resolve_country(parent, info):
        return parent.country.name

    class Meta:
        model = DocumentType


class IndividualIdentityNode(DjangoObjectType):
    type = graphene.String(description="Agency type")

    def resolve_type(parent, info):
        return parent.agency.type

    class Meta:
        model = IndividualIdentity


class DocumentNode(DjangoObjectType):
    class Meta:
        model = Document
        filter_fields = []
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class FlexFieldsScalar(graphene.Scalar):
    """
    Allows use of a JSON String for input / output from the GraphQL schema.

    Use of this type is *not recommended* as you lose the benefits of having a defined, static
    schema (one of the key benefits of GraphQL).
    """

    @staticmethod
    def serialize(dt):
        return dt

    @staticmethod
    def parse_literal(node):
        return node

    @staticmethod
    def parse_value(value):
        return value


class ExtendedHouseHoldConnection(graphene.Connection):
    class Meta:
        abstract = True

    total_count = graphene.Int()
    individuals_count = graphene.Int()
    edge_count = graphene.Int()

    def resolve_total_count(root, info, **kwargs):
        return root.length

    def resolve_edge_count(root, info, **kwargs):
        return len(root.edges)

    def resolve_individuals_count(root, info, **kwargs):
        return root.iterable.aggregate(sum=Sum("size")).get("sum")


class HouseholdSelection(DjangoObjectType):
    class Meta:
        model = HouseholdSelection


class HouseholdNode(DjangoObjectType):
    total_cash_received = graphene.Decimal()
    country_origin = graphene.String(description="Country origin name")
    country = graphene.String(description="Country name")
    flex_fields = FlexFieldsScalar()
    selection = graphene.Field(HouseholdSelection)
    sanction_list_possible_match = graphene.Boolean()
    has_duplicates = graphene.Boolean(description="Mark household if any of individuals has Duplicate status")

    def resolve_country(parent, info):
        return parent.country.name

    def resolve_country_origin(parent, info):
        return parent.country_origin.name

    def resolve_selection(parent, info):
        selection = parent.selections.first()
        return selection

    def resolve_individuals(parent, info):
        individuals_ids = list(parent.individuals.values_list("id", flat=True))
        collectors_ids = list(parent.representatives.values_list("id", flat=True))
        ids = list(set(individuals_ids + collectors_ids))
        return Individual.objects.filter(id__in=ids).prefetch_related(
            Prefetch("households_and_roles", queryset=IndividualRoleInHousehold.objects.filter(household=parent.id),)
        )

    def resolve_has_duplicates(parent, info):
        return parent.individuals.filter(deduplication_golden_record_status=DUPLICATE).exists()

    class Meta:
        model = Household
        filter_fields = []
        interfaces = (relay.Node,)
        connection_class = ExtendedHouseHoldConnection


class IndividualRoleInHouseholdNode(DjangoObjectType):
    class Meta:
        model = IndividualRoleInHousehold


class IndividualNode(DjangoObjectType):
    estimated_birth_date = graphene.Boolean(required=False)
    role = graphene.String()
    flex_fields = FlexFieldsScalar()
    deduplication_golden_record_results = graphene.List(DeduplicationResultNode)
    deduplication_batch_results = graphene.List(DeduplicationResultNode)

    def resolve_role(parent, info):
        role = parent.households_and_roles.first()
        if role is not None:
            return role.role
        return ROLE_NO_ROLE

    def resolve_deduplication_golden_record_results(parent, info):
        key = "duplicates" if parent.deduplication_golden_record_status == DUPLICATE else "possible_duplicates"
        results = parent.deduplication_golden_record_results.get(key, {})
        return encode_ids(results, "Individual", "hit_id")

    def resolve_deduplication_batch_results(parent, info):
        key = "duplicates" if parent.deduplication_batch_status == DUPLICATE_IN_BATCH else "possible_duplicates"
        results = parent.deduplication_batch_results.get(key, {})
        return encode_ids(results, "ImportedIndividual", "hit_id")

    class Meta:
        model = Individual
        filter_fields = []
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class Query(graphene.ObjectType):
    household = relay.Node.Field(HouseholdNode)
    all_households = DjangoFilterConnectionField(HouseholdNode, filterset_class=HouseholdFilter,)
    individual = relay.Node.Field(IndividualNode)
    all_individuals = DjangoFilterConnectionField(IndividualNode, filterset_class=IndividualFilter,)
    residence_status_choices = graphene.List(ChoiceObject)
    sex_choices = graphene.List(ChoiceObject)
    marital_status_choices = graphene.List(ChoiceObject)
    relationship_choices = graphene.List(ChoiceObject)
    role_choices = graphene.List(ChoiceObject)

    def resolve_all_households(self, info, **kwargs):
        return Household.objects.annotate(total_cash=Sum("payment_records__delivered_quantity")).order_by("created_at")

    def resolve_residence_status_choices(self, info, **kwargs):
        return to_choice_object(RESIDENCE_STATUS_CHOICE)

    def resolve_sex_choices(self, info, **kwargs):
        return to_choice_object(SEX_CHOICE)

    def resolve_marital_status_choices(self, info, **kwargs):
        return to_choice_object(MARITAL_STATUS_CHOICE)

    def resolve_relationship_choices(self, info, **kwargs):
        return to_choice_object(RELATIONSHIP_CHOICE)

    def resolve_role_choices(self, info, **kwargs):
        return to_choice_object(ROLE_CHOICE)
