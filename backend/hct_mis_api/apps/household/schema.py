import graphene
from django.db.models import Sum, Q
from django_filters import (
    FilterSet,
    OrderingFilter,
    CharFilter,
    ModelMultipleChoiceFilter,
)
from graphene import relay
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from core.filters import AgeRangeFilter, IntegerRangeFilter
from core.extended_connection import ExtendedConnection
from core.schema import ChoiceObject
from core.utils import to_choice_object
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
)


class HouseholdFilter(FilterSet):
    business_area = CharFilter(
        field_name="registration_data_import__business_area__slug"
    )
    size = IntegerRangeFilter(field_name="size")
    search = CharFilter(method="search_filter")

    class Meta:
        model = Household
        fields = {
            "business_area": ["exact", "icontains"],
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
            q_obj |= Q(id__icontains=value)
        return qs.filter(q_obj)


class IndividualFilter(FilterSet):
    business_area = CharFilter(field_name="household__business_area__slug",)
    age = AgeRangeFilter(field_name="birth_date")
    sex = ModelMultipleChoiceFilter(
        to_field_name="sex", queryset=Individual.objects.all(),
    )
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
        fields=(
            "id",
            "full_name",
            "household__id",
            "birth_date",
            "sex",
            "household__admin_area__title",
        )
    )

    def search_filter(self, qs, name, value):
        values = value.split(" ")
        q_obj = Q()
        for value in values:
            q_obj |= Q(household__admin_area__title__icontains=value)
            q_obj |= Q(id__icontains=value)
            q_obj |= Q(household__id__icontains=value)
            q_obj |= Q(full_name__icontains=value)
        return qs.filter(q_obj)


class DocumentTypeNode(DjangoObjectType):
    country = graphene.String(description="Country name")

    def resolve_country(parrent, info):
        return parrent.country.name

    class Meta:
        model = DocumentType


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

class HouseholdNode(DjangoObjectType):
    total_cash_received = graphene.Decimal()
    country_origin = graphene.String(description="Country origin name")
    country = graphene.String(description="Country name")
    flex_fields = FlexFieldsScalar()

    def resolve_country(parrent, info):
        return parrent.country.name

    def resolve_country_origin(parrent, info):
        return parrent.country_origin.name

    class Meta:
        model = Household
        filter_fields = []
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection




class IndividualNode(DjangoObjectType):
    estimated_birth_date = graphene.Boolean(required=False)
    role = graphene.String()
    flex_fields = FlexFieldsScalar()

    class Meta:
        model = Individual
        filter_fields = []
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class Query(graphene.ObjectType):
    household = relay.Node.Field(HouseholdNode)
    all_households = DjangoFilterConnectionField(
        HouseholdNode, filterset_class=HouseholdFilter,
    )
    individual = relay.Node.Field(IndividualNode)
    all_individuals = DjangoFilterConnectionField(
        IndividualNode, filterset_class=IndividualFilter,
    )
    residence_status_choices = graphene.List(ChoiceObject)
    sex_choices = graphene.List(ChoiceObject)
    marital_status_choices = graphene.List(ChoiceObject)
    relationship_choices = graphene.List(ChoiceObject)
    role_choices = graphene.List(ChoiceObject)

    def resolve_all_households(self, info, **kwargs):
        return Household.objects.annotate(
            total_cash=Sum("payment_records__entitlement__delivered_quantity")
        ).order_by("created_at")

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
