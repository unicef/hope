import graphene
from graphene import relay
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from core.schema import ExtendedConnection
from household.models import Household, RegistrationDataImport


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
    all_households = DjangoFilterConnectionField(HouseholdNode)
    registration_data_import = relay.Node.Field(RegistrationDataImportNode)
    all_registration_data_imports = DjangoFilterConnectionField(
        RegistrationDataImportNode
    )
