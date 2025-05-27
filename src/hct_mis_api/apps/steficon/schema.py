from typing import Any

import graphene
from django.db.models import QuerySet
from graphene import relay
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from hct_mis_api.apps.core.extended_connection import ExtendedConnection
from hct_mis_api.apps.steficon.filters import SteficonRuleFilter
from hct_mis_api.apps.steficon.models import Rule, RuleCommit


class SteficonRuleNode(DjangoObjectType):
    class Meta:
        model = Rule
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection
        exclude = ("version",)


class RuleCommitNode(DjangoObjectType):
    class Meta:
        model = RuleCommit
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection
        exclude = ("version",)


class Query(graphene.ObjectType):
    all_steficon_rules = DjangoFilterConnectionField(
        SteficonRuleNode,
        filterset_class=SteficonRuleFilter,
    )

    def resolve_all_steficon_rules(self, info: Any, **kwargs: Any) -> QuerySet:
        business_area_slug = info.context.headers.get("Business-Area")
        return (
            Rule.objects.filter(deprecated=False, enabled=True, history__is_release=True)
            .distinct()
            .allowed_to(business_area_slug)
        )
