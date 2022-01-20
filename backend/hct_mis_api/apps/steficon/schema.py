import graphene
from django_filters import FilterSet
from graphene import relay
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from hct_mis_api.apps.core.extended_connection import ExtendedConnection
from hct_mis_api.apps.steficon.models import Rule, RuleCommit


class SteficonRuleFilter(FilterSet):
    class Meta:
        fields = ("enabled", "deprecated")
        model = Rule


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

    def resolve_all_steficon_rules(self, info, **kwargs):
        return Rule.objects.filter(deprecated=False, enabled=True, history__is_release=True)
