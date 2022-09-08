import logging
from collections import OrderedDict
from enum import Enum, auto, unique
from functools import partial

from django.core.exceptions import PermissionDenied

from graphene import Mutation
from graphene.relay import ClientIDMutation
from graphene.types.argument import to_arguments
from graphene_django import DjangoConnectionField
from graphene_django.filter.utils import (
    get_filtering_args_from_filterset,
    get_filterset_class,
)
from graphql import GraphQLError

from hct_mis_api.apps.core.models import BusinessArea

logger = logging.getLogger(__name__)


@unique
class Permissions(Enum):
    def _generate_next_value_(name, *args):
        return name

    # RDI
    RDI_VIEW_LIST = auto()
    RDI_VIEW_DETAILS = auto()
    RDI_IMPORT_DATA = auto()
    RDI_RERUN_DEDUPE = auto()
    RDI_MERGE_IMPORT = auto()
    RDI_REFUSE_IMPORT = auto()

    # Population
    POPULATION_VIEW_HOUSEHOLDS_LIST = auto()
    POPULATION_VIEW_HOUSEHOLDS_DETAILS = auto()
    POPULATION_VIEW_INDIVIDUALS_LIST = auto()
    POPULATION_VIEW_INDIVIDUALS_DETAILS = auto()

    # Programme
    PRORGRAMME_VIEW_LIST_AND_DETAILS = auto()
    PROGRAMME_VIEW_PAYMENT_RECORD_DETAILS = auto()
    PROGRAMME_CREATE = auto()
    PROGRAMME_UPDATE = auto()
    PROGRAMME_REMOVE = auto()
    PROGRAMME_ACTIVATE = auto()
    PROGRAMME_FINISH = auto()

    # Targeting
    TARGETING_VIEW_LIST = auto()
    TARGETING_VIEW_DETAILS = auto()
    TARGETING_CREATE = auto()
    TARGETING_UPDATE = auto()
    TARGETING_DUPLICATE = auto()
    TARGETING_REMOVE = auto()
    TARGETING_LOCK = auto()
    TARGETING_UNLOCK = auto()
    TARGETING_SEND = auto()

    # Payment Verification
    PAYMENT_VERIFICATION_VIEW_LIST = auto()
    PAYMENT_VERIFICATION_VIEW_DETAILS = auto()
    PAYMENT_VERIFICATION_CREATE = auto()
    PAYMENT_VERIFICATION_UPDATE = auto()
    PAYMENT_VERIFICATION_ACTIVATE = auto()
    PAYMENT_VERIFICATION_DISCARD = auto()
    PAYMENT_VERIFICATION_FINISH = auto()
    PAYMENT_VERIFICATION_EXPORT = auto()
    PAYMENT_VERIFICATION_IMPORT = auto()
    PAYMENT_VERIFICATION_VERIFY = auto()
    PAYMENT_VERIFICATION_VIEW_PAYMENT_RECORD_DETAILS = auto()
    PAYMENT_VERIFICATION_DELETE = auto()
    PAYMENT_VERIFICATION_INVALID = auto()

    # User Management
    USER_MANAGEMENT_VIEW_LIST = auto()

    # Dashboard
    # Note: view HQ dashboard will be available for users in business area global and permission view_country
    # DASHBOARD_VIEW_HQ = auto()
    DASHBOARD_VIEW_COUNTRY = auto()
    DASHBOARD_EXPORT = auto()

    # Grievances
    # We have different permissions that allow to view/edit etc all grievances
    # or only the ones user created or the ones user is assigned to
    GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE = auto()
    GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE_AS_CREATOR = auto()
    GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE_AS_OWNER = auto()
    GRIEVANCES_VIEW_LIST_SENSITIVE = auto()
    GRIEVANCES_VIEW_LIST_SENSITIVE_AS_CREATOR = auto()
    GRIEVANCES_VIEW_LIST_SENSITIVE_AS_OWNER = auto()
    GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE = auto()
    GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE_AS_CREATOR = auto()
    GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE_AS_OWNER = auto()
    GRIEVANCES_VIEW_DETAILS_SENSITIVE = auto()
    GRIEVANCES_VIEW_DETAILS_SENSITIVE_AS_CREATOR = auto()
    GRIEVANCES_VIEW_DETAILS_SENSITIVE_AS_OWNER = auto()
    GRIEVANCES_VIEW_HOUSEHOLD_DETAILS = auto()
    GRIEVANCES_VIEW_HOUSEHOLD_DETAILS_AS_CREATOR = auto()
    GRIEVANCES_VIEW_HOUSEHOLD_DETAILS_AS_OWNER = auto()
    GRIEVANCES_VIEW_INDIVIDUALS_DETAILS = auto()
    GRIEVANCES_VIEW_INDIVIDUALS_DETAILS_AS_CREATOR = auto()
    GRIEVANCES_VIEW_INDIVIDUALS_DETAILS_AS_OWNER = auto()
    GRIEVANCES_CREATE = auto()
    GRIEVANCES_UPDATE = auto()
    GRIEVANCES_UPDATE_AS_CREATOR = auto()
    GRIEVANCES_UPDATE_AS_OWNER = auto()
    GRIEVANCES_UPDATE_REQUESTED_DATA_CHANGE = auto()
    GRIEVANCES_UPDATE_REQUESTED_DATA_CHANGE_AS_CREATOR = auto()
    GRIEVANCES_UPDATE_REQUESTED_DATA_CHANGE_AS_OWNER = auto()
    GRIEVANCES_ADD_NOTE = auto()
    GRIEVANCES_ADD_NOTE_AS_CREATOR = auto()
    GRIEVANCES_ADD_NOTE_AS_OWNER = auto()
    GRIEVANCES_SET_IN_PROGRESS = auto()
    GRIEVANCES_SET_IN_PROGRESS_AS_CREATOR = auto()
    GRIEVANCES_SET_IN_PROGRESS_AS_OWNER = auto()
    GRIEVANCES_SET_ON_HOLD = auto()
    GRIEVANCES_SET_ON_HOLD_AS_CREATOR = auto()
    GRIEVANCES_SET_ON_HOLD_AS_OWNER = auto()
    GRIEVANCES_SEND_FOR_APPROVAL = auto()
    GRIEVANCES_SEND_FOR_APPROVAL_AS_CREATOR = auto()
    GRIEVANCES_SEND_FOR_APPROVAL_AS_OWNER = auto()
    GRIEVANCES_SEND_BACK = auto()
    GRIEVANCES_SEND_BACK_AS_CREATOR = auto()
    GRIEVANCES_SEND_BACK_AS_OWNER = auto()
    GRIEVANCES_APPROVE_DATA_CHANGE = auto()
    GRIEVANCES_APPROVE_DATA_CHANGE_AS_CREATOR = auto()
    GRIEVANCES_APPROVE_DATA_CHANGE_AS_OWNER = auto()
    GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK = auto()
    GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK_AS_CREATOR = auto()
    GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK_AS_OWNER = auto()
    GRIEVANCES_CLOSE_TICKET_FEEDBACK = auto()
    GRIEVANCES_CLOSE_TICKET_FEEDBACK_AS_CREATOR = auto()
    GRIEVANCES_CLOSE_TICKET_FEEDBACK_AS_OWNER = auto()
    GRIEVANCES_APPROVE_FLAG_AND_DEDUPE = auto()
    GRIEVANCES_APPROVE_FLAG_AND_DEDUPE_AS_CREATOR = auto()
    GRIEVANCES_APPROVE_FLAG_AND_DEDUPE_AS_OWNER = auto()
    GRIEVANCES_APPROVE_PAYMENT_VERIFICATION = auto()
    GRIEVANCES_APPROVE_PAYMENT_VERIFICATION_AS_CREATOR = auto()
    GRIEVANCES_APPROVE_PAYMENT_VERIFICATION_AS_OWNER = auto()
    GRIEVANCE_ASSIGN = auto()

    # Reporting
    REPORTING_EXPORT = auto()

    # All
    ALL_VIEW_PII_DATA_ON_LISTS = auto()

    # Activity Log
    ACTIVITY_LOG_VIEW = auto()
    ACTIVITY_LOG_DOWNLOAD = auto()

    # Core
    UPLOAD_STORAGE_FILE = auto()
    DOWNLOAD_STORAGE_FILE = auto()

    # Django Admin
    # ...

    # ...

    @classmethod
    def choices(cls):
        return tuple((i.value, i.value.replace("_", " ")) for i in cls)


ALL_GRIEVANCES_CREATE_MODIFY = (
    Permissions.GRIEVANCES_CREATE,
    Permissions.GRIEVANCES_UPDATE,
    Permissions.GRIEVANCES_UPDATE_AS_CREATOR,
    Permissions.GRIEVANCES_UPDATE_AS_OWNER,
    Permissions.GRIEVANCES_UPDATE_REQUESTED_DATA_CHANGE,
    Permissions.GRIEVANCES_UPDATE_REQUESTED_DATA_CHANGE_AS_CREATOR,
    Permissions.GRIEVANCES_UPDATE_REQUESTED_DATA_CHANGE_AS_OWNER,
)


class BasePermission:
    @classmethod
    def has_permission(cls, info, **kwargs):
        return False


class AllowAny(BasePermission):
    @classmethod
    def has_permission(cls, info, **kwargs):
        return True


class AllowAuthenticated(BasePermission):
    @classmethod
    def has_permission(cls, info, **kwargs):
        return info.context.user.is_authenticated


def hopePermissionClass(permission):
    class XDPerm(BasePermission):
        @classmethod
        def has_permission(cls, info, **kwargs):
            business_area_arg = kwargs.get("business_area")
            if isinstance(business_area_arg, BusinessArea):
                business_area = business_area_arg
            else:
                if business_area_arg is None:
                    return False
                business_area = BusinessArea.objects.filter(slug=business_area_arg).first()
                if business_area is None:
                    return False
            return info.context.user.is_authenticated and info.context.user.has_permission(
                permission.name, business_area
            )

    return XDPerm


def hopeOneOfPermissionClass(*permissions):
    class XDPerm(BasePermission):
        @classmethod
        def has_permission(cls, info, **kwargs):
            if info.context.user.is_authenticated:
                business_area_arg = kwargs.get("business_area")
                if isinstance(business_area_arg, BusinessArea):
                    business_area = business_area_arg
                else:
                    if business_area_arg is None:
                        return False
                    business_area = BusinessArea.objects.filter(slug=business_area_arg).first()
                    if business_area is None:
                        return False
                for permission in permissions:
                    if info.context.user.has_permission(permission.name, business_area):
                        return True
            return False

    return XDPerm


class BaseNodePermissionMixin:
    permission_classes = (AllowAny,)

    @classmethod
    def check_node_permission(cls, info, object_instance):
        business_area = object_instance.business_area
        if not any(perm.has_permission(info, business_area=business_area) for perm in cls.permission_classes):
            logger.error("Permission Denied")
            raise GraphQLError("Permission Denied")

    @classmethod
    def get_node(cls, info, object_id):
        try:
            object_instance = cls._meta.model.objects.get(pk=object_id)  # type: ignore
            cls.check_node_permission(info, object_instance)
        except cls._meta.model.DoesNotExist:  # type: ignore
            object_instance = None
        return object_instance

    @classmethod
    def check_creator_or_owner_permission(
        cls,
        info,
        object_instance,
        general_permission,
        is_creator,
        creator_permission,
        is_owner,
        owner_permission,
    ):
        user = info.context.user
        business_area = object_instance.business_area
        if not info.context.user.is_authenticated or not (
            user.has_permission(general_permission, business_area)
            or (is_creator and user.has_permission(creator_permission, business_area))
            or (is_owner and user.has_permission(owner_permission, business_area))
        ):
            logger.error("Permission Denied")
            raise GraphQLError("Permission Denied")


class DjangoPermissionFilterConnectionField(DjangoConnectionField):
    def __init__(
        self,
        type,
        fields=None,
        order_by=None,
        extra_filter_meta=None,
        filterset_class=None,
        permission_classes=(AllowAny,),
        *args,
        **kwargs,
    ):
        self._fields = fields
        self._provided_filterset_class = filterset_class
        self._filterset_class = None
        self._extra_filter_meta = extra_filter_meta
        self._base_args = None
        self.permission_classes = permission_classes
        super().__init__(type, *args, **kwargs)

    @property
    def args(self):
        return to_arguments(self._base_args or OrderedDict(), self.filtering_args)

    @args.setter
    def args(self, args):
        self._base_args = args

    @property
    def filterset_class(self):
        if not self._filterset_class:
            fields = self._fields or self.node_type._meta.filter_fields
            meta = dict(model=self.model, fields=fields)
            if self._extra_filter_meta:
                meta.update(self._extra_filter_meta)

            filterset_class = self._provided_filterset_class or (self.node_type._meta.filterset_class)
            self._filterset_class = get_filterset_class(filterset_class, **meta)

        return self._filterset_class

    @property
    def filtering_args(self):
        return get_filtering_args_from_filterset(self.filterset_class, self.node_type)

    @classmethod
    def resolve_queryset(
        cls,
        connection,
        iterable,
        info,
        args,
        filtering_args,
        filterset_class,
        permission_classes,
    ):
        filter_kwargs = {k: v for k, v in args.items() if k in filtering_args}
        if not any(perm.has_permission(info, **filter_kwargs) for perm in permission_classes):
            logger.error("Permission Denied")
            raise GraphQLError("Permission Denied")
        if "permissions" in filtering_args:
            filter_kwargs["permissions"] = info.context.user.permissions_in_business_area(
                filter_kwargs.get("business_area")
            )
        qs = super().resolve_queryset(connection, iterable, info, args)
        return filterset_class(data=filter_kwargs, queryset=qs, request=info.context).qs

    def get_queryset_resolver(self):
        return partial(
            self.resolve_queryset,
            filterset_class=self.filterset_class,
            filtering_args=self.filtering_args,
            permission_classes=self.permission_classes,
        )


class BaseMutationPermissionMixin:
    @classmethod
    def is_authenticated(cls, info):
        if not info.context.user.is_authenticated:
            cls.raise_permission_denied_error(True)
        return True

    @classmethod
    def has_permission(cls, info, permission, business_area_arg, raise_error=True):
        cls.is_authenticated(info)
        if not isinstance(permission, list):
            permissions = (permission,)
        else:
            permissions = permission
        if isinstance(business_area_arg, BusinessArea):
            business_area = business_area_arg
        else:
            if business_area_arg is None:
                return cls.raise_permission_denied_error(raise_error=raise_error)
            business_area = BusinessArea.objects.filter(slug=business_area_arg).first()
            if business_area is None:
                return cls.raise_permission_denied_error(raise_error=raise_error)
        if not any(
            [
                permission.name
                for permission in permissions
                if info.context.user.has_permission(permission.name, business_area)
            ]
        ):
            return cls.raise_permission_denied_error(raise_error=raise_error)
        return True

    @classmethod
    def has_creator_or_owner_permission(
        cls,
        info,
        business_area_arg,
        general_permission,
        is_creator,
        creator_permission,
        is_owner,
        owner_permission,
        raise_error=True,
    ):
        cls.is_authenticated(info)
        if not (
            cls.has_permission(info, general_permission, business_area_arg, False)
            or (is_creator and cls.has_permission(info, creator_permission, business_area_arg, False))
            or (is_owner and cls.has_permission(info, owner_permission, business_area_arg, False))
        ):
            return cls.raise_permission_denied_error(raise_error=raise_error)
        return True

    @staticmethod
    def raise_permission_denied_error(not_authenticated=False, raise_error=True):
        if not raise_error:
            return False
        if not_authenticated:
            logger.error("Permission Denied: User is not authenticated.")
            raise PermissionDenied("Permission Denied: User is not authenticated.")
        else:
            logger.error("Permission Denied: User does not have correct permission.")
            raise PermissionDenied("Permission Denied: User does not have correct permission.")


class PermissionMutation(BaseMutationPermissionMixin, Mutation):
    @classmethod
    def mutate(cls, root, info, **kwargs):
        return super().mutate(root, info, **kwargs)


class PermissionRelayMutation(BaseMutationPermissionMixin, ClientIDMutation):
    @classmethod
    def mutate_and_get_payload(cls, root, info, **kwargs):
        return super().mutate_and_get_payload(root, info, **kwargs)


class ViewPermissionsMixinBase:
    def has_permissions(self):
        return NotImplemented

    def dispatch(self, request, *args, **kwargs):
        if not self.has_permissions():
            raise PermissionDenied
        return super(ViewPermissionsMixinBase, self).dispatch(request, *args, **kwargs)


class UploadFilePermissionMixin(ViewPermissionsMixinBase):
    def has_permissions(self):
        roles = self.request.user.user_roles.all()

        return self.request.user.is_authenticated and any(
            self.request.user.has_permission(
                Permissions.UPLOAD_STORAGE_FILE.name, role.business_area
            ) for role in roles
        )
