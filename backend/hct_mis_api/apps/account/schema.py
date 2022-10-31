import json
import logging
from typing import Set

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.encoding import force_str
from django.utils.functional import Promise

import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from hct_mis_api.apps.account.filters import UsersFilter
from hct_mis_api.apps.account.models import (
    USER_STATUS_CHOICES,
    Partner,
    Role,
    User,
    UserRole,
)
from hct_mis_api.apps.account.permissions import (
    ALL_GRIEVANCES_CREATE_MODIFY,
    DjangoPermissionFilterConnectionField,
    Permissions,
    hopeOneOfPermissionClass,
)
from hct_mis_api.apps.core.extended_connection import ExtendedConnection
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.schema import ChoiceObject
from hct_mis_api.apps.core.utils import to_choice_object

logger = logging.getLogger(__name__)


def permissions_resolver(user_roles) -> Set:
    all_user_roles = user_roles
    permissions_set = set()
    for user_role in all_user_roles:
        if user_role.role and user_role.role.permissions:
            permissions_set.update(user_role.role.permissions)
    return permissions_set


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


class PartnerType(DjangoObjectType):
    class Meta:
        model = Partner


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
            return force_str(obj)
        return super().default(obj)


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
        permission_classes=(
            hopeOneOfPermissionClass(Permissions.USER_MANAGEMENT_VIEW_LIST, *ALL_GRIEVANCES_CREATE_MODIFY),
        ),
        max_limit=1000,
    )
    user_roles_choices = graphene.List(ChoiceObject)
    user_status_choices = graphene.List(ChoiceObject)
    user_partner_choices = graphene.List(ChoiceObject)
    has_available_users_to_export = graphene.Boolean(business_area_slug=graphene.String(required=True))

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
        return to_choice_object(Partner.get_partners_as_choices())

    def resolve_has_available_users_to_export(self, info, business_area_slug, **kwargs):
        return (
            get_user_model()
            .objects.prefetch_related("user_roles")
            .filter(available_for_export=True, is_superuser=False, user_roles__business_area__slug=business_area_slug)
            .exists()
        )
