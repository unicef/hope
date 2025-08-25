import logging
from enum import Enum, auto, unique
from typing import TYPE_CHECKING, Any, Iterable, Optional, Union

from django.core.exceptions import PermissionDenied

from models.core import BusinessArea
from hope.apps.core.utils import get_program_id_from_headers

if TYPE_CHECKING:
    from models.program import Program

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


def check_permissions(user: Any, permissions: Iterable[Permissions], **kwargs: Any) -> bool:
    from models.program import Program

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
