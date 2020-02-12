import graphene
from django_filters import FilterSet, OrderingFilter, CharFilter, NumberFilter
from graphene import relay
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from core.schema import ExtendedConnection
from household.models import Household, RegistrationDataImport


class HouseholdFilter(FilterSet):
    business_area = CharFilter(field_name="location__business_area__slug")
    family_size_gte = NumberFilter(field_name="family_size__gte")
    family_size_lte = NumberFilter(field_name="family_size__lte")

    class Meta:
        model = Household

    order_by = OrderingFilter(
        fields=(
            "household_ca_id",
            "residence_status",
            "nationality",
            "family_size",
            "representative__full_name",
            "registration_data_import_id__name",
        )
    )


class HouseholdNode(DjangoObjectType):
    class Meta:
        model = Household
        filter_fields = []
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class RegistrationDataImportNode(DjangoObjectType):
    class Meta:
        model = RegistrationDataImport
        filter_fields = []
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class Query(graphene.ObjectType):
    household = relay.Node.Field(HouseholdNode)
    all_households = DjangoFilterConnectionField(
        HouseholdNode, filterset_class=HouseholdFilter
    )
    registration_data_import = relay.Node.Field(RegistrationDataImportNode)
    all_registration_data_imports = DjangoFilterConnectionField(
        RegistrationDataImportNode
    )
