from typing import Any

import graphene
from graphene import relay
from graphene_django import DjangoObjectType

from hct_mis_api.apps.account.permissions import DjangoPermissionFilterConnectionField
from hct_mis_api.apps.core.extended_connection import ExtendedConnection
from hct_mis_api.apps.sanction_list.filters import SanctionListIndividualFilter
from hct_mis_api.apps.sanction_list.models import (
    SanctionListIndividual,
    SanctionListIndividualAliasName,
    SanctionListIndividualCountries,
    SanctionListIndividualNationalities,
)


class SanctionListIndividualNode(DjangoObjectType):
    country_of_birth = graphene.String(description="Country of birth")

    class Meta:
        model = SanctionListIndividual
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection

    def resolve_country_of_birth(parent, info: Any) -> str:
        return parent.country_of_birth.name


class SanctionListIndividualNationalitiesNode(DjangoObjectType):
    nationality = graphene.String()

    class Meta:
        model = SanctionListIndividualNationalities
        exclude = ("individual",)
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection

    def resolve_nationality(parent, info: Any) -> str:
        return parent.nationality.name


class SanctionListIndividualCountriesNode(DjangoObjectType):
    country = graphene.String()

    class Meta:
        model = SanctionListIndividualCountries
        exclude = ("individual",)
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection

    def resolve_country(parent, info: Any) -> str:
        return parent.country.name


class SanctionListIndividualAliasNameNode(DjangoObjectType):
    class Meta:
        model = SanctionListIndividualAliasName
        exclude = ("individual",)
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class Query(graphene.ObjectType):
    sanction_list_individual = relay.Node.Field(SanctionListIndividualNode)
    all_sanction_list_individuals = DjangoPermissionFilterConnectionField(
        SanctionListIndividualNode,
        filterset_class=SanctionListIndividualFilter,
    )
