import graphene
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django_filters import FilterSet, OrderingFilter, CharFilter
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from core.extended_connection import ExtendedConnection


class UsersFilter(FilterSet):
    full_name = CharFilter(field_name="full_name", method="filter_by_full_name")

    class Meta:
        model = get_user_model()
        fields = {
            "full_name": ["exact", "icontains"],
        }

    order_by = OrderingFilter(fields=("full_name", "first_name", "last_name",))

    def filter_by_full_name(self, qs, name, value):
        for term in value.split():
            qs = qs.filter(
                Q(first_name__icontains=term) | Q(last_name__icontains=term)
            )
        return qs


class UserObjectType(DjangoObjectType):
    class Meta:
        model = get_user_model()
        exclude = ("password",)


class UserNode(DjangoObjectType):
    class Meta:
        model = get_user_model()
        exclude = ("password",)
        filter_fields = []
        interfaces = (graphene.relay.Node,)
        connection_class = ExtendedConnection


class Query(graphene.ObjectType):
    me = graphene.Field(UserObjectType)
    all_users = DjangoFilterConnectionField(
        UserNode, filterset_class=UsersFilter,
    )

    def resolve_me(self, info, **kwargs):
        if not info.context.user.is_authenticated:
            raise PermissionDenied(
                "Permission Denied: User is not authenticated."
            )
        return info.context.user
