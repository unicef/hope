import graphene
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django_filters import FilterSet, OrderingFilter, CharFilter, MultipleChoiceFilter
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from account.models import USER_PARTNER_CHOICES, USER_STATUS_CHOICES, Role
from core.extended_connection import ExtendedConnection
from core.models import BusinessArea


class UsersFilter(FilterSet):
    business_area = CharFilter(required=True, method="business_area_filter")
    search = CharFilter(method="search_filter")
    status = MultipleChoiceFilter(field_name="status", choices=USER_STATUS_CHOICES)
    partner = MultipleChoiceFilter(field_name="partner", choices=USER_PARTNER_CHOICES)
    roles = MultipleChoiceFilter(choices=Role.get_roles_as_choices(), method="roles_filter")

    class Meta:
        model = get_user_model()
        fields = {
            "search": ["exact", "icontains"],
            "status": ["exact"],
            "partner": ["exact"],
            "roles": ["exact"],
        }

    order_by = OrderingFilter(fields=("first_name", "last_name", "last_login", "status", "partner", "email"))

    def search_filter(self, qs, name, value):
        values = value.split(" ")
        q_obj = Q()
        for value in values:
            q_obj |= Q(first_name__icontains=value)
            q_obj |= Q(last_name__icontains=value)
            q_obj |= Q(email__icontains=value)
        return qs.filter(q_obj)

    def business_area_filter(self, qs, name, value):
        return qs

    def roles_filter(self, qs, name, values):
        business_area_slug = self.data.get("business_area")
        q_obj = Q()
        for value in values:
            q_obj |= Q(user_roles__role__name=value, user_roles__business_area__slug=business_area_slug)
        return qs.filter(q_obj)


class BusinessAreaForUserNode(DjangoObjectType):
    class Meta:
        model = BusinessArea
        filter_fields = ["id"]
        interfaces = (graphene.relay.Node,)
        connection_class = ExtendedConnection


class UserObjectType(DjangoObjectType):
    business_areas = DjangoFilterConnectionField(BusinessAreaForUserNode)

    def resolve_business_areas(self, info):
        return BusinessArea.objects.filter(user_roles__user=self).distinct()

    class Meta:
        model = get_user_model()
        exclude = ("password",)


class UserNode(DjangoObjectType):
    business_areas = DjangoFilterConnectionField(BusinessAreaForUserNode)

    def resolve_business_areas(self, info):
        return BusinessArea.objects.filter(user_roles__user=self).distinct()

    class Meta:
        model = get_user_model()
        exclude = ("password",)
        filter_fields = []
        interfaces = (graphene.relay.Node,)
        connection_class = ExtendedConnection


class Query(graphene.ObjectType):
    me = graphene.Field(UserObjectType)
    all_users = DjangoFilterConnectionField(UserNode, filterset_class=UsersFilter)

    def resolve_me(self, info, **kwargs):
        if not info.context.user.is_authenticated:
            raise PermissionDenied("Permission Denied: User is not authenticated.")
        return info.context.user
