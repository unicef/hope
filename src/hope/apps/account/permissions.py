import logging
from collections import OrderedDict
from enum import Enum, auto, unique
from functools import partial
from typing import TYPE_CHECKING, Any, Callable, Iterable, Optional, Union

import graphene
from django.core.exceptions import PermissionDenied
from django.db.models import Model
from graphene import Mutation
from graphene.relay import ClientIDMutation
from graphene.types.argument import to_arguments
from graphene_django.filter.utils import (
    get_filtering_args_from_filterset,
    get_filterset_class,
)

from hope.apps.core.extended_connection import DjangoFastConnectionField
from hope.apps.core.models import BusinessArea
from hope.apps.core.utils import get_program_id_from_headers

if TYPE_CHECKING:
    from django.contrib.auth.base_user import AbstractBaseUser
    from django.contrib.auth.models import AnonymousUser

    from hope.apps.account.models import User
    from hope.apps.program.models import Program

logger = logging.getLogger(__name__)


@unique
class Permissions(Enum):
    def _generate_next_value_(  # type: ignore # https://github.com/python/mypy/issues/7591
        name: str, start: int, count: int, last_values: list[Any]
    ) -> Any:
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
    POPULATION_VIEW_INDIVIDUAL_DELIVERY_MECHANISMS_SECTION = auto()

    # Programme
    PROGRAMME_VIEW_LIST_AND_DETAILS = auto()
    PROGRAMME_MANAGEMENT_VIEW = auto()
    PROGRAMME_VIEW_PAYMENT_RECORD_DETAILS = auto()
    PROGRAMME_CREATE = auto()
    PROGRAMME_UPDATE = auto()
    PROGRAMME_REMOVE = auto()
    PROGRAMME_ACTIVATE = auto()
    PROGRAMME_FINISH = auto()
    PROGRAMME_DUPLICATE = auto()

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

    # Payment Managerial View
    PAYMENT_VIEW_LIST_MANAGERIAL = auto()
    PAYMENT_VIEW_LIST_MANAGERIAL_RELEASED = auto()

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
    PAYMENT_VERIFICATION_MARK_AS_FAILED = auto()

    # Payment Module
    PM_VIEW_LIST = auto()
    PM_CREATE = auto()
    PM_VIEW_DETAILS = auto()
    PM_IMPORT_XLSX_WITH_ENTITLEMENTS = auto()
    PM_APPLY_RULE_ENGINE_FORMULA_WITH_ENTITLEMENTS = auto()
    PM_SPLIT = auto()
    PM_VIEW_PAYMENT_LIST = auto()

    PM_LOCK_AND_UNLOCK = auto()
    PM_LOCK_AND_UNLOCK_FSP = auto()
    PM_SEND_FOR_APPROVAL = auto()
    PM_EXCLUDE_BENEFICIARIES_FROM_FOLLOW_UP_PP = auto()
    PM_ACCEPTANCE_PROCESS_APPROVE = auto()
    PM_ACCEPTANCE_PROCESS_AUTHORIZE = auto()
    PM_ACCEPTANCE_PROCESS_FINANCIAL_REVIEW = auto()
    PM_IMPORT_XLSX_WITH_RECONCILIATION = auto()
    PM_EXPORT_XLSX_FOR_FSP = auto()
    PM_DOWNLOAD_XLSX_FOR_FSP = auto()
    PM_MARK_PAYMENT_AS_FAILED = auto()
    PM_EXPORT_PDF_SUMMARY = auto()
    PM_SEND_TO_PAYMENT_GATEWAY = auto()
    PM_VIEW_FSP_AUTH_CODE = auto()
    PM_DOWNLOAD_FSP_AUTH_CODE = auto()
    PM_SEND_XLSX_PASSWORD = auto()
    PM_ASSIGN_FUNDS_COMMITMENTS = auto()
    PM_SYNC_PAYMENT_PLAN_WITH_PG = auto()
    PM_SYNC_PAYMENT_WITH_PG = auto()

    # PaymentPlanSupportingDocument
    PM_DOWNLOAD_SUPPORTING_DOCUMENT = auto()
    PM_UPLOAD_SUPPORTING_DOCUMENT = auto()
    PM_DELETE_SUPPORTING_DOCUMENT = auto()

    # Payment Module Admin
    PM_ADMIN_FINANCIAL_SERVICE_PROVIDER_UPDATE = auto()

    # Programme Cycle
    PM_PROGRAMME_CYCLE_VIEW_LIST = auto()
    PM_PROGRAMME_CYCLE_VIEW_DETAILS = auto()
    PM_PROGRAMME_CYCLE_CREATE = auto()
    PM_PROGRAMME_CYCLE_UPDATE = auto()
    PM_PROGRAMME_CYCLE_DELETE = auto()

    # User Management
    USER_MANAGEMENT_VIEW_LIST = auto()

    # Dashboard
    # Note: view HQ dashboard will be available for users in business area global and permission view_country
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
    GRIEVANCE_DOCUMENTS_UPLOAD = auto()
    GRIEVANCES_CROSS_AREA_FILTER = auto()
    GRIEVANCES_VIEW_BIOMETRIC_RESULTS = auto()

    # Feedback
    GRIEVANCES_FEEDBACK_VIEW_CREATE = auto()
    GRIEVANCES_FEEDBACK_VIEW_LIST = auto()
    GRIEVANCES_FEEDBACK_VIEW_DETAILS = auto()
    GRIEVANCES_FEEDBACK_VIEW_UPDATE = auto()
    GRIEVANCES_FEEDBACK_MESSAGE_VIEW_CREATE = auto()

    # Periodic Data Update
    PDU_VIEW_LIST_AND_DETAILS = auto()
    PDU_TEMPLATE_CREATE = auto()
    PDU_TEMPLATE_DOWNLOAD = auto()
    PDU_UPLOAD = auto()

    # All
    ALL_VIEW_PII_DATA_ON_LISTS = auto()

    # Activity Log
    ACTIVITY_LOG_VIEW = auto()
    ACTIVITY_LOG_DOWNLOAD = auto()

    # Core
    UPLOAD_STORAGE_FILE = auto()
    DOWNLOAD_STORAGE_FILE = auto()

    # Beneficiary Group
    BENEFICIARY_GROUP_VIEW_LIST = auto()

    # Communication
    ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_LIST = auto()
    ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_DETAILS = auto()
    ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_CREATE = auto()
    ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_DETAILS_AS_CREATOR = auto()

    # Feedback
    ACCOUNTABILITY_SURVEY_VIEW_CREATE = auto()
    ACCOUNTABILITY_SURVEY_VIEW_LIST = auto()
    ACCOUNTABILITY_SURVEY_VIEW_DETAILS = auto()

    # Geo
    GEO_VIEW_LIST = auto()

    # Django Admin
    CAN_ADD_BUSINESS_AREA_TO_PARTNER = auto()

    @classmethod
    def choices(cls) -> tuple:
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

POPULATION_LIST = (
    Permissions.POPULATION_VIEW_HOUSEHOLDS_LIST,
    Permissions.POPULATION_VIEW_INDIVIDUALS_LIST,
)

POPULATION_DETAILS = (
    Permissions.POPULATION_VIEW_HOUSEHOLDS_DETAILS,
    Permissions.POPULATION_VIEW_INDIVIDUALS_DETAILS,
)

DEFAULT_PERMISSIONS_IS_UNICEF_PARTNER = (
    Permissions.RDI_VIEW_LIST,
    Permissions.RDI_VIEW_DETAILS,
    Permissions.POPULATION_VIEW_HOUSEHOLDS_LIST,
    Permissions.POPULATION_VIEW_HOUSEHOLDS_DETAILS,
    Permissions.POPULATION_VIEW_INDIVIDUALS_LIST,
    Permissions.POPULATION_VIEW_INDIVIDUALS_DETAILS,
    Permissions.DASHBOARD_VIEW_COUNTRY,
    Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS,
    Permissions.TARGETING_VIEW_LIST,
    Permissions.TARGETING_VIEW_DETAILS,
    Permissions.PM_VIEW_LIST,
    Permissions.PM_VIEW_DETAILS,
    Permissions.PM_VIEW_PAYMENT_LIST,
    Permissions.PAYMENT_VERIFICATION_VIEW_LIST,
    Permissions.PAYMENT_VERIFICATION_VIEW_DETAILS,
    Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE,
    Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE,
    Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE,
    Permissions.GRIEVANCES_VIEW_DETAILS_SENSITIVE,
    Permissions.GRIEVANCES_FEEDBACK_VIEW_LIST,
    Permissions.GRIEVANCES_FEEDBACK_VIEW_DETAILS,
    Permissions.GRIEVANCES_CROSS_AREA_FILTER,
    Permissions.USER_MANAGEMENT_VIEW_LIST,
    Permissions.ACTIVITY_LOG_VIEW,
)

DEFAULT_PERMISSIONS_LIST_FOR_IS_UNICEF_PARTNER = [str(perm.value) for perm in DEFAULT_PERMISSIONS_IS_UNICEF_PARTNER]


class BasePermission:
    @classmethod
    def has_permission(cls, info: Any, **kwargs: Any) -> bool:
        return False


class AllowAny(BasePermission):
    @classmethod
    def has_permission(cls, info: Any, **kwargs: Any) -> bool:
        return True


class AllowAuthenticated(BasePermission):
    @classmethod
    def has_permission(cls, info: Any, **kwargs: Any) -> bool:
        return info.context.user.is_authenticated


def check_permissions(user: Any, permissions: Iterable[Permissions], **kwargs: Any) -> bool:
    from hope.apps.program.models import Program

    if not user.is_authenticated:
        return False

    business_area_arg = kwargs.get("business_area")
    if business_area_arg is None:
        return False
    business_area = (
        business_area_arg
        if isinstance(business_area_arg, BusinessArea)
        else BusinessArea.objects.filter(slug=business_area_arg).first()
    )
    if business_area is None:
        return False
    program = None
    if program_slug := kwargs.get("program"):
        program = Program.objects.filter(slug=program_slug, business_area=business_area).first()
    elif kwargs.get("Program"):  # TODO: GraphQL - remove after GraphQL complete removal
        program = Program.objects.filter(id=get_program_id_from_headers(kwargs)).first()
    obj = program or business_area

    return any(user.has_perm(permission.name, obj) for permission in permissions)


def check_creator_or_owner_permission(
    user: Union["User", "AnonymousUser", "AbstractBaseUser"],
    general_permission: Permissions,
    is_creator: bool,
    creator_permission: Permissions,
    is_owner: bool,
    owner_permission: Permissions,
    business_area: "BusinessArea",
    program: Optional["Program"],
) -> None:
    scope = program or business_area
    if not user.is_authenticated or not (
        user.has_perm(general_permission.value, scope)
        or (is_creator and user.has_perm(creator_permission.value, scope))
        or (is_owner and user.has_perm(owner_permission.value, scope))
    ):
        raise PermissionDenied("Permission Denied")


def has_creator_or_owner_permission(
    user: Union["User", "AnonymousUser", "AbstractBaseUser"],
    general_permission: Permissions,
    is_creator: bool,
    creator_permission: Permissions,
    is_owner: bool,
    owner_permission: Permissions,
    business_area: "BusinessArea",
    program: Optional["Program"],
) -> bool:
    scope = program or business_area
    return user.is_authenticated and (
        user.has_perm(general_permission.value, scope)
        or (is_creator and user.has_perm(creator_permission.value, scope))
        or (is_owner and user.has_perm(owner_permission.value, scope))
    )


def hopePermissionClass(permission: Permissions) -> type[BasePermission]:
    class XDPerm(BasePermission):
        @classmethod
        def has_permission(cls, info: Any, **kwargs: Any) -> bool:
            user = info.context.user
            permissions = [permission]
            kwargs["Program"] = info.context.headers.get("Program")
            kwargs["Referer"] = info.context.headers.get("Referer")
            return check_permissions(user, permissions, **kwargs)

    return XDPerm


def hopeOneOfPermissionClass(*permissions: Permissions) -> type[BasePermission]:
    class XDPerm(BasePermission):
        @classmethod
        def has_permission(cls, info: Any, **kwargs: Any) -> bool:
            user = info.context.user
            kwargs["Program"] = info.context.headers.get("Program")
            return check_permissions(user, permissions, **kwargs)

    return XDPerm


class AdminUrlNodeMixin:
    admin_url = graphene.String()

    def resolve_admin_url(self, info: Any, **kwargs: Any) -> graphene.String | None:
        if info.context.user.is_superuser:
            return self.admin_url
        return None


class BaseNodePermissionMixin:
    permission_classes: tuple[type[BasePermission], ...] = (AllowAny,)

    @classmethod
    def check_node_permission(cls, info: Any, object_instance: Any) -> None:
        business_area = getattr(object_instance, "business_area", None)  # not every object has business_area attr
        if (
            business_area
            and not any(perm.has_permission(info, business_area=business_area) for perm in cls.permission_classes)
        ) or not (business_area or info.context.user.is_authenticated):
            raise PermissionDenied("Permission Denied")

    @classmethod
    def get_node(cls, info: Any, object_id: str, **kwargs: Any) -> Model | None:
        try:
            if "get_object_queryset" in kwargs:
                object_instance = kwargs.get("get_object_queryset").get(pk=object_id)
            else:
                object_instance = cls.get_queryset(cls._meta.model.objects, info).get(pk=object_id)
            cls.check_node_permission(info, object_instance)
        except cls._meta.model.DoesNotExist:
            object_instance = None
        return object_instance

    @classmethod
    def check_creator_or_owner_permission(
        cls,
        info: Any,
        object_instance: Any,
        general_permission: str,
        is_creator: bool,
        creator_permission: str,
        is_owner: bool,
        owner_permission: str,
    ) -> None:
        from hope.apps.program.models import Program

        user = info.context.user
        business_area = object_instance.business_area
        program = Program.objects.filter(id=get_program_id_from_headers(info.context.headers)).first()
        scope = program or business_area
        if not user.is_authenticated or not (
            user.has_perm(general_permission, scope)
            or (is_creator and user.has_perm(creator_permission, scope))
            or (is_owner and user.has_perm(owner_permission, scope))
        ):
            raise PermissionDenied("Permission Denied")


class DjangoPermissionFilterFastConnectionField(DjangoFastConnectionField):
    def __init__(
        self,
        typology: type,
        fields: Any | None = None,
        order_by: Any | None = None,
        extra_filter_meta: Any | None = None,
        filterset_class: Any | None = None,
        permission_classes: tuple[type[BasePermission], ...] = (AllowAny,),
        *args: Any,
        **kwargs: Any,
    ) -> None:
        self._fields = fields
        self._provided_filterset_class = filterset_class
        self._filterset_class = None
        self._extra_filter_meta = extra_filter_meta
        self._base_args = None
        self.permission_classes = permission_classes
        super().__init__(typology, *args, **kwargs)

    @property
    def args(self) -> dict:
        return to_arguments(self._base_args or OrderedDict(), self.filtering_args)

    @args.setter
    def args(self, args: Any) -> None:
        self._base_args = args

    @property
    def filterset_class(self) -> Any:
        if not self._filterset_class:
            fields = self._fields or self.node_type._meta.filter_fields
            meta = {"model": self.model, "fields": fields}
            if self._extra_filter_meta:
                meta.update(self._extra_filter_meta)

            filterset_class = self._provided_filterset_class or (self.node_type._meta.filterset_class)
            self._filterset_class = get_filterset_class(filterset_class, **meta)

        return self._filterset_class

    @property
    def filtering_args(self) -> Any:
        return get_filtering_args_from_filterset(self.filterset_class, self.node_type)

    @classmethod
    def connection_resolver(
        cls,
        resolver: Any,
        connection: Any,
        default_manager: Any,
        queryset_resolver: Any,
        max_limit: Any,
        enforce_first_or_last: Any,
        root: Any,
        info: Any,
        **args: Any,
    ) -> Any:
        if not info.context.user.is_authenticated:
            raise PermissionDenied("Permission Denied: User is not authenticated.")
        return super().connection_resolver(
            resolver,
            connection,
            default_manager,
            queryset_resolver,
            max_limit,
            enforce_first_or_last,
            root,
            info,
            **args,
        )

    @classmethod
    def resolve_queryset(
        cls,
        connection: Any,
        iterable: Iterable,
        info: Any,
        args: Any,
        filtering_args: list,
        filterset_class: Any,
        permission_classes: list,
    ) -> Any:
        filter_kwargs = {k: v for k, v in args.items() if k in filtering_args}
        if business_area := info.context.headers.get("Business-Area"):
            filter_kwargs["business_area"] = business_area
        if program_id := get_program_id_from_headers(info.context.headers):
            filter_kwargs["Program"] = program_id

        if not any(perm.has_permission(info, **filter_kwargs) for perm in permission_classes):
            raise PermissionDenied("Permission Denied")
        if "permissions" in filtering_args:
            filter_kwargs["permissions"] = info.context.user.permissions_in_business_area(
                business_area_slug=filter_kwargs.get("business_area"),
                program_id=program_id,
            )
        qs = super().resolve_queryset(connection, iterable, info, args)
        return filterset_class(data=filter_kwargs, queryset=qs, request=info.context).qs

    def get_queryset_resolver(self) -> Callable:
        return partial(
            self.resolve_queryset,
            filterset_class=self.filterset_class,
            filtering_args=self.filtering_args,
            permission_classes=self.permission_classes,
        )


class DjangoPermissionFilterConnectionField(DjangoPermissionFilterFastConnectionField):
    use_cached_count = False


class BaseMutationPermissionMixin:
    @classmethod
    def is_authenticated(cls, info: Any) -> bool | None:
        if not info.context.user.is_authenticated:
            cls.raise_not_authenticated_error()
        return True

    @classmethod
    def has_permission(
        cls,
        info: Any,
        permission: Any,
        business_area_arg: str | BusinessArea,
        raise_error: bool = True,
    ) -> bool:
        from hope.apps.program.models import Program

        cls.is_authenticated(info)
        permissions: Iterable = (permission,) if not isinstance(permission, list) else permission
        if isinstance(business_area_arg, BusinessArea):
            business_area = business_area_arg
        else:
            if business_area_arg is None:
                return cls.raise_permission_denied_error(raise_error=raise_error)
            business_area = BusinessArea.objects.filter(slug=business_area_arg).first()
            if business_area is None:
                return cls.raise_permission_denied_error(raise_error=raise_error)
        program = Program.objects.filter(id=get_program_id_from_headers(info.context.headers)).first()

        if not any(
            permission.name
            for permission in permissions
            if info.context.user.has_perm(permission.name, program or business_area)
        ):
            return cls.raise_permission_denied_error(raise_error=raise_error)
        return True

    @classmethod
    def has_creator_or_owner_permission(
        cls,
        info: Any,
        business_area_arg: str,
        general_permission: Any,
        is_creator: bool,
        creator_permission: Any,
        is_owner: bool,
        owner_permission: Any,
        raise_error: bool = True,
    ) -> bool:
        cls.is_authenticated(info)
        if not (
            cls.has_permission(info, general_permission, business_area_arg, False)
            or (is_creator and cls.has_permission(info, creator_permission, business_area_arg, False))
            or (is_owner and cls.has_permission(info, owner_permission, business_area_arg, False))
        ):
            return cls.raise_permission_denied_error(raise_error=raise_error)
        return True

    @staticmethod
    def raise_permission_denied_error(raise_error: bool = True) -> bool:
        if not raise_error:
            return False
        raise PermissionDenied("Permission Denied: User does not have correct permission.")

    @staticmethod
    def raise_not_authenticated_error() -> None:
        raise PermissionDenied("Permission Denied: User is not authenticated.")


class PermissionMutation(BaseMutationPermissionMixin, Mutation):
    @classmethod
    def mutate(cls, root: Any, info: Any, **kwargs: Any) -> None:
        return super().mutate(root, info, **kwargs)


class PermissionRelayMutation(BaseMutationPermissionMixin, ClientIDMutation):
    @classmethod
    def mutate_and_get_payload(cls, root: Any, info: Any, **kwargs: Any) -> None:
        return super().mutate_and_get_payload(root, info, **kwargs)
