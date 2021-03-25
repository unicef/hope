import json
import logging

import graphene
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Q
from django.db.models.functions import Lower
from django.utils.encoding import force_text
from django.utils.functional import Promise
from django_filters import FilterSet, CharFilter, MultipleChoiceFilter
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from hct_mis_api.apps.account.models import USER_PARTNER_CHOICES, USER_STATUS_CHOICES, Role, UserRole, User
from hct_mis_api.apps.account.permissions import DjangoPermissionFilterConnectionField, Permissions, hopePermissionClass
from hct_mis_api.apps.core.extended_connection import ExtendedConnection
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.schema import ChoiceObject
from hct_mis_api.apps.core.utils import to_choice_object, CustomOrderingFilter

logger = logging.getLogger(__name__)


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
            "search": ["exact", "startswith"],
            "status": ["exact"],
            "partner": ["exact"],
            "roles": ["exact"],
        }

    order_by = CustomOrderingFilter(
        fields=(Lower("first_name"), Lower("last_name"), "last_login", "status", "partner", "email")
    )

    def search_filter(self, qs, name, value):
        values = value.split(" ")
        q_obj = Q()
        for value in values:
            q_obj |= Q(first_name__startswith=value)
            q_obj |= Q(last_name__startswith=value)
            q_obj |= Q(email__startswith=value)
        return qs.filter(q_obj)

    def business_area_filter(self, qs, name, value):
        return qs.filter(user_roles__business_area__slug=value)

    def roles_filter(self, qs, name, values):
        business_area_slug = self.data.get("business_area")
        q_obj = Q()
        for value in values:
            q_obj |= Q(user_roles__role__id=value, user_roles__business_area__slug=business_area_slug)
        return qs.filter(q_obj)


class UserRoleNode(DjangoObjectType):
    class Meta:
        model = UserRole
        exclude = ("id", "user")


class RoleNode(DjangoObjectType):
    class Meta:
        model = Role
        exclude = ("id",)


class UserBusinessAreaNode(DjangoObjectType):
    permissions = graphene.List(graphene.String)

    def resolve_permissions(self, info):
        user_roles = UserRole.objects.filter(user=info.context.user, business_area_id=self.id)
        return permissions_resolver(user_roles)

    class Meta:
        model = BusinessArea
        filter_fields = ["id"]
        interfaces = (graphene.relay.Node,)
        connection_class = ExtendedConnection


class UserObjectType(DjangoObjectType):
    business_areas = DjangoFilterConnectionField(UserBusinessAreaNode)

    def resolve_business_areas(self, info):
        return BusinessArea.objects.filter(user_roles__user=self).distinct()

    class Meta:
        model = get_user_model()
        exclude = ("password",)


class UserNode(DjangoObjectType):
    business_areas = DjangoFilterConnectionField(UserBusinessAreaNode)

    def resolve_business_areas(self, info):
        return BusinessArea.objects.filter(user_roles__user=self).distinct()

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


class Query(graphene.ObjectType):
    me = graphene.Field(UserNode)
    all_users = DjangoPermissionFilterConnectionField(
        UserNode,
        filterset_class=UsersFilter,
        permission_classes=(hopePermissionClass(Permissions.USER_MANAGEMENT_VIEW_LIST),),
    )
    # all_log_entries = graphene.ConnectionField(LogEntryObjectConnection, object_id=graphene.String(required=False))
    user_roles_choices = graphene.List(ChoiceObject)
    user_status_choices = graphene.List(ChoiceObject)
    user_partner_choices = graphene.List(ChoiceObject)
    has_available_users_to_export = graphene.Boolean(business_area_slug=graphene.String(required=True))

    # def resolve_all_log_entries(self, info, **kwargs):
    #     object_id = kwargs.get('object_id')
    #     queryset = LogEntry.objects
    #     if object_id:
    #         id = decode_id_string(object_id)
    #         queryset = queryset.filter(~Q(action=0))
    #         queryset = queryset.filter(object_pk=id)
    #     return queryset.all()

    def resolve_all_users(self, info, **kwargs):
        return User.objects.all().distinct()

    def resolve_me(self, info, **kwargs):
        if not info.context.user.is_authenticated:
            raise PermissionDenied("Permission Denied: User is not authenticated.")
        return info.context.user

    def resolve_user_roles_choices(self, info, **kwargs):
        return to_choice_object(Role.get_roles_as_choices())

    def resolve_user_status_choices(self, info, **kwargs):
        return to_choice_object(USER_STATUS_CHOICES)

    def resolve_user_partner_choices(self, info, **kwargs):
        return to_choice_object(USER_PARTNER_CHOICES)

    def resolve_has_available_users_to_export(self, info, business_area_slug, **kwargs):
        return (
            get_user_model()
            .objects.prefetch_related("user_roles")
            .filter(available_for_export=True, is_superuser=False, user_roles__business_area__slug=business_area_slug)
            .exists()
        )
