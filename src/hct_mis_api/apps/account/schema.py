import json
import logging
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Set

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.encoding import force_str
from django.utils.functional import Promise

import graphene
from flags.state import flag_state
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from hct_mis_api.apps.account.filters import UsersFilter
from hct_mis_api.apps.account.models import (
    USER_STATUS_CHOICES,
    Partner,
    Role,
    RoleAssignment,
    User,
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
from hct_mis_api.apps.core.utils import (
    decode_id_string,
    get_program_id_from_headers,
    to_choice_object,
)
from hct_mis_api.apps.geo.models import Area
from hct_mis_api.apps.geo.schema import AreaNode
from hct_mis_api.apps.household.models import Household, Individual

logger = logging.getLogger(__name__)


if TYPE_CHECKING:
    from django.db.models.query import QuerySet

    from graphene import Node


def permissions_resolver(user_roles: "QuerySet[RoleAssignment]") -> Set:
    all_user_roles = user_roles
    permissions_set = set()
    for user_role in all_user_roles:
        if user_role.role and user_role.role.permissions:
            permissions_set.update(user_role.role.permissions)
    return permissions_set


class RoleAssignmentNode(DjangoObjectType):
    class Meta:
        model = RoleAssignment
        exclude = ("id", "user")


class RoleNode(DjangoObjectType):
    class Meta:
        model = Role
        exclude = ("id",)


class PartnerRoleNode(DjangoObjectType):
    class Meta:
        model = RoleAssignment
        exclude = ("id",)


class UserRoleNode(DjangoObjectType):
    class Meta:
        model = RoleAssignment
        exclude = ("id",)


class RoleChoiceObject(graphene.ObjectType):
    name = graphene.String()
    value = graphene.String()
    subsystem = graphene.String()


class UserBusinessAreaNode(DjangoObjectType):
    permissions = graphene.List(graphene.String)
    is_accountability_applicable = graphene.Boolean()

    def resolve_permissions(self, info: Any) -> Set:
        return info.context.user.permissions_in_business_area(self.slug)

    def resolve_is_accountability_applicable(self, info: Any) -> bool:
        return all([bool(flag_state("ALLOW_ACCOUNTABILITY_MODULE")), self.is_accountability_applicable])

    class Meta:
        model = BusinessArea
        filter_fields = ["id"]
        interfaces = (graphene.relay.Node,)
        connection_class = ExtendedConnection


class PartnerType(DjangoObjectType):
    class Meta:
        model = Partner


class UserNode(DjangoObjectType):
    business_areas = DjangoFilterConnectionField(UserBusinessAreaNode)
    permissions_in_scope = graphene.List(graphene.String)
    partner_roles = graphene.List(PartnerRoleNode)
    user_roles = graphene.List(UserRoleNode)

    def resolve_business_areas(self, info: Any) -> "QuerySet[BusinessArea]":
        return info.context.user.business_areas

    def resolve_partner_roles(self, info: Any) -> "QuerySet[Role]":
        return self.partner.role_assignments.order_by("business_area__slug")

    def resolve_user_roles(self, info: Any) -> "QuerySet[Role]":
        return self.role_assignments.order_by("business_area__slug")

    def resolve_permissions_in_scope(self, info: Any) -> Set:
        user = info.context.user
        program_id = get_program_id_from_headers(info.context.headers)
        business_area_slug = info.context.headers.get("Business-Area")
        return user.permissions_in_business_area(business_area_slug, program_id)

    class Meta:
        model = get_user_model()
        exclude = ("password",)
        filter_fields = []
        interfaces = (graphene.relay.Node,)
        connection_class = ExtendedConnection


class LazyEncoder(DjangoJSONEncoder):
    def default(self, obj: Any) -> str:
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
    def serialize(dt: Any) -> str:
        return json.dumps(dt, cls=LazyEncoder)

    @staticmethod
    def parse_literal(node: "Node") -> Optional[Dict]:
        if isinstance(node, graphene.String):
            return json.loads(node.value)
        return None

    @staticmethod
    def parse_value(value: Any) -> Dict:
        return json.loads(value)


class PartnerNode(DjangoObjectType):
    name = graphene.String()
    areas = graphene.List(AreaNode)
    area_access = graphene.String()

    class Meta:
        model = Partner

    def resolve_areas(self, info: Any) -> "List[Area]":
        return self.get_areas_for_program(self.partner_program).order_by("name")

    def resolve_area_access(self, info: Any, **kwargs: Any) -> str:
        if self.has_area_limits_in_program(self.partner_program):
            return "ADMIN_AREA"
        else:
            return "BUSINESS_AREA"


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
    user_roles_choices = graphene.List(RoleChoiceObject)
    user_status_choices = graphene.List(ChoiceObject)
    user_partner_choices = graphene.List(ChoiceObject)
    partner_for_grievance_choices = graphene.Field(
        graphene.List(ChoiceObject),
        household_id=graphene.Argument(graphene.ID),
        individual_id=graphene.Argument(graphene.ID),
    )
    has_available_users_to_export = graphene.Boolean(business_area_slug=graphene.String(required=True))

    def resolve_all_users(self, info: Any, **kwargs: Any) -> "QuerySet[User]":
        return User.objects.all().distinct()

    def resolve_me(self, info: Any, **kwargs: Any) -> "User":
        if not info.context.user.is_authenticated:
            raise PermissionDenied("Permission Denied: User is not authenticated.")
        return info.context.user

    def resolve_user_roles_choices(self, info: Any) -> List[Dict[str, Any]]:
        return [
            dict(name=role.name, value=role.id, subsystem=role.subsystem)
            for role in Role.objects.all().order_by("name")
        ]

    def resolve_user_status_choices(self, info: Any) -> List[Dict[str, Any]]:
        return to_choice_object(USER_STATUS_CHOICES)

    def resolve_user_partner_choices(self, info: Any) -> List[Dict[str, Any]]:
        business_area_slug = info.context.headers.get("Business-Area")
        return to_choice_object(
            list(
                Partner.objects.exclude(name=settings.DEFAULT_EMPTY_PARTNER)
                .filter(allowed_business_areas__slug=business_area_slug)
                .exclude(id__in=Partner.objects.filter(parent__isnull=False).values_list("parent_id", flat=True))
                .values_list("id", "name")
            )
        )

    def resolve_partner_for_grievance_choices(
        self, info: Any, household_id: Optional[str] = None, individual_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        business_area_id = str(BusinessArea.objects.get(slug=info.context.headers.get("Business-Area")).id)
        encoded_program_id = info.context.headers.get("Program")
        if encoded_program_id and encoded_program_id != "all":
            program_id = decode_id_string(encoded_program_id)
        elif household_id:
            program_id = str(Household.objects.get(id=decode_id_string(household_id)).program_id)
        elif individual_id:
            program_id = str(Individual.objects.get(id=decode_id_string(individual_id)).program_id)
        else:
            program_id = None
        return to_choice_object(Partner.get_partners_for_program_as_choices(business_area_id, program_id))

    def resolve_has_available_users_to_export(self, info: Any, business_area_slug: str) -> bool:
        return (
            get_user_model()
            .objects.prefetch_related("role_assignments")
            .filter(is_superuser=False, role_assignments__business_area__slug=business_area_slug)
            .exists()
        )
