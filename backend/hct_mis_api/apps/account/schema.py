import json

import graphene
from auditlog.models import LogEntry
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Q
from django.utils.encoding import force_text
from django.utils.functional import Promise
from django_filters import FilterSet, OrderingFilter, CharFilter, MultipleChoiceFilter
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from account.models import USER_PARTNER_CHOICES, USER_STATUS_CHOICES, Role, UserRole
from core.extended_connection import ExtendedConnection
from core.models import BusinessArea
from core.schema import ChoiceObject, BusinessAreaNode
from core.utils import to_choice_object


def permissions_resolver(user_roles):
    all_user_roles = user_roles
    permissions_set = set()
    for user_role in all_user_roles:
        permissions_set.update(user_role.role.permissions)
    return permissions_set


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


class UserRoleNode(DjangoObjectType):
    class Meta:
        model = UserRole
        exclude = ("id", "user")


class RoleNode(DjangoObjectType):
    class Meta:
        model = Role
        exclude = ("id",)


class UserObjectType(DjangoObjectType):
    business_areas = DjangoFilterConnectionField(BusinessAreaNode)
    permissions = graphene.List(graphene.String)

    def resolve_business_areas(self, info):
        return BusinessArea.objects.all()[:2]

    def resolve_permissions(self, info):
        return permissions_resolver(self.user_roles.all())

    class Meta:
        model = get_user_model()
        exclude = ("password",)


class UserNode(DjangoObjectType):
    business_areas = DjangoFilterConnectionField(BusinessAreaNode)
    permissions = graphene.List(graphene.String)

    def resolve_business_areas(self, info):
        return BusinessArea.objects.all()[:2]

    def resolve_permissions(self, info):
        return permissions_resolver(self.user_roles.all())

    class Meta:
        model = get_user_model()
        exclude = ("password",)
        filter_fields = []
        interfaces = (graphene.relay.Node,)
        connection_class = ExtendedConnection


class LazyEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, Promise):
            return force_text(obj)
        return super(LazyEncoder, self).default(obj)


class JSONLazyString(graphene.Scalar):
    """
    Allows use of a JSON String for input / output from the GraphQL schema.

    Use of this type is *not recommended* as you lose the benefits of having a defined, static
    schema (one of the key benefits of GraphQL).
    """

    @staticmethod
    def serialize(dt):
        return json.dumps(dt, cls=LazyEncoder)

    @staticmethod
    def parse_literal(node):
        if isinstance(node, graphene.String):
            return json.loads(node.value)

    @staticmethod
    def parse_value(value):
        return json.loads(value)


class LogEntryObject(DjangoObjectType):
    timestamp = graphene.DateTime()
    changes_display_dict = JSONLazyString()
    actor = UserObjectType()

    class Meta:
        model = LogEntry
        exclude_fields = ("additional_data",)


class LogEntryObjectConnection(graphene.Connection):
    total_count = graphene.Int()

    def resolve_total_count(self, info, **kwargs):
        return self.iterable.count()

    class Meta:
        node = LogEntryObject


class Query(graphene.ObjectType):
    me = graphene.Field(UserObjectType)
    all_users = DjangoFilterConnectionField(UserNode, filterset_class=UsersFilter)
    all_log_entries = graphene.ConnectionField(LogEntryObjectConnection, object_id=graphene.String(required=True))
    user_roles_choices = graphene.List(ChoiceObject)
    user_status_choices = graphene.List(ChoiceObject)
    user_partner_choices = graphene.List(ChoiceObject)

    def resolve_me(self, info, **kwargs):
        if not info.context.user.is_authenticated:
            raise PermissionDenied("Permission Denied: User is not authenticated.")
        return info.context.user

    def resolve_user_roles_choices(self, info, **kwargs):
        return to_choice_object(USER_STATUS_CHOICES)

    def resolve_user_status_choices(self, info, **kwargs):
        return to_choice_object(Role.get_roles_as_choices())

    def resolve_user_partner_choices(self, info, **kwargs):
        return to_choice_object(USER_PARTNER_CHOICES)
