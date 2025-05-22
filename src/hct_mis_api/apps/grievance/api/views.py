from typing import Any, Dict

from django.contrib.auth.models import AbstractUser
from django.db.models import Case, DateField, F, QuerySet, When
from django.utils import timezone

from cfgv import ValidationError
from constance import config
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.mixins import CreateModelMixin, ListModelMixin, RetrieveModelMixin
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_extensions.cache.decorators import cache_response

from hct_mis_api.api.caches import etag_decorator
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.api.mixins import (
    BaseViewSet,
    BusinessAreaVisibilityMixin,
    CountActionMixin,
    ProgramVisibilityMixin,
    SerializerActionMixin,
)
from hct_mis_api.apps.grievance.api.caches import GrievanceTicketListKeyConstructor
from hct_mis_api.apps.grievance.api.mixins import GrievancePermissionsMixin
from hct_mis_api.apps.grievance.api.serializers.grievance_ticket import (
    CreateGrievanceTicketSerializer,
    GrievanceChoicesSerializer,
    GrievanceTicketDetailSerializer,
    GrievanceTicketListSerializer,
)
from hct_mis_api.apps.grievance.filters import GrievanceTicketFilter
from hct_mis_api.apps.grievance.models import GrievanceTicket
from hct_mis_api.apps.grievance.services.ticket_creator_service import (
    TicketCreatorService,
    TicketDetailsCreatorFactory,
)
from hct_mis_api.apps.utils.exceptions import log_and_raise


def verify_required_arguments(input_data: Dict, field_name: str, options: Dict) -> None:
    from hct_mis_api.apps.core.utils import nested_dict_get

    for key, value in options.items():
        if key != input_data.get(field_name):
            continue
        for required in value.get("required"):
            if nested_dict_get(input_data, required) is None:
                log_and_raise(f"You have to provide {required} in {key}")
        for not_allowed in value.get("not_allowed"):
            if nested_dict_get(input_data, not_allowed) is not None:
                log_and_raise(f"You can't provide {not_allowed} in {key}")


class GrievanceTicketViewSet(
    ProgramVisibilityMixin,
    SerializerActionMixin,
    GrievancePermissionsMixin,
    CountActionMixin,
    ListModelMixin,
    CreateModelMixin,
    BaseViewSet,
):
    queryset = GrievanceTicket.objects.filter(ignored=False)
    serializer_class = GrievanceTicketListSerializer
    PERMISSIONS = [
        Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE,
        Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE_AS_CREATOR,
        Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE_AS_OWNER,
        Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE,
        Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE_AS_CREATOR,
        Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE_AS_OWNER,
    ]
    filter_backends = (OrderingFilter, DjangoFilterBackend)
    filterset_class = GrievanceTicketFilter
    admin_area_model_fields = ["admin2"]
    program_model_field = "programs"
    serializer_classes_by_action = {
        "list": GrievanceTicketListSerializer,
        "retrieve": GrievanceTicketDetailSerializer,
        "create": CreateGrievanceTicketSerializer,
    }
    permissions_by_action = {
        # "list": [],   # TODO: will add later
        # "retrieve": [],
        "create": [Permissions.GRIEVANCES_CREATE],
    }

    CATEGORY_OPTIONS = {
        GrievanceTicket.CATEGORY_PAYMENT_VERIFICATION: {
            "required": [],
            "not_allowed": [
                "extras.category.sensitive_grievance_ticket_extras",
                "extras.category.grievance_complaint_ticket_extras",
            ],
        },
        GrievanceTicket.CATEGORY_DATA_CHANGE: {
            "required": [],
            "not_allowed": [
                "extras.category.sensitive_grievance_ticket_extras",
                "extras.category.grievance_complaint_ticket_extras",
            ],
        },
        GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE: {
            "required": ["issue_type"],
            "not_allowed": ["extras.category.grievance_complaint_ticket_extras"],
        },
        GrievanceTicket.CATEGORY_GRIEVANCE_COMPLAINT: {
            "required": ["issue_type"],
            "not_allowed": ["extras.category.sensitive_grievance_ticket_extras"],
        },
        GrievanceTicket.CATEGORY_REFERRAL: {
            "required": [],
            "not_allowed": [
                "extras.category.sensitive_grievance_ticket_extras",
                "extras.category.grievance_complaint_ticket_extras",
            ],
        },
        GrievanceTicket.CATEGORY_SYSTEM_FLAGGING: {
            "required": [],
            "not_allowed": [
                "extras.category.sensitive_grievance_ticket_extras",
                "extras.category.grievance_complaint_ticket_extras",
            ],
        },
        GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION: {
            "required": [],
            "not_allowed": [
                "extras.category.sensitive_grievance_ticket_extras",
                "extras.category.grievance_complaint_ticket_extras",
            ],
        },
    }

    ISSUE_TYPE_OPTIONS = {
        GrievanceTicket.ISSUE_TYPE_HOUSEHOLD_DATA_CHANGE_DATA_UPDATE: {
            "required": ["extras.issue_type.household_data_update_issue_type_extras"],
            "not_allowed": [
                "individual_data_update_issue_type_extras",
                "individual_delete_issue_type_extras",
            ],
        },
        GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_DELETE_HOUSEHOLD: {
            "required": ["extras.issue_type.household_delete_issue_type_extras"],
            "not_allowed": [
                "household_data_update_issue_type_extras",
                "individual_data_update_issue_type_extras",
            ],
        },
        GrievanceTicket.ISSUE_TYPE_INDIVIDUAL_DATA_CHANGE_DATA_UPDATE: {
            "required": ["extras.issue_type.individual_data_update_issue_type_extras"],
            "not_allowed": [
                "household_data_update_issue_type_extras",
                "individual_delete_issue_type_extras",
            ],
        },
        GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_ADD_INDIVIDUAL: {
            "required": ["extras.issue_type.add_individual_issue_type_extras"],
            "not_allowed": [
                "household_data_update_issue_type_extras",
                "individual_data_update_issue_type_extras",
                "individual_delete_issue_type_extras",
            ],
        },
        GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_DELETE_INDIVIDUAL: {
            "required": ["extras.issue_type.individual_delete_issue_type_extras"],
            "not_allowed": [
                "household_data_update_issue_type_extras",
                "individual_data_update_issue_type_extras",
            ],
        },
        GrievanceTicket.ISSUE_TYPE_DATA_BREACH: {"required": [], "not_allowed": []},
        GrievanceTicket.ISSUE_TYPE_BRIBERY_CORRUPTION_KICKBACK: {
            "required": [],
            "not_allowed": [],
        },
        GrievanceTicket.ISSUE_TYPE_FRAUD_FORGERY: {"required": [], "not_allowed": []},
        GrievanceTicket.ISSUE_TYPE_FRAUD_MISUSE: {"required": [], "not_allowed": []},
        GrievanceTicket.ISSUE_TYPE_HARASSMENT: {"required": [], "not_allowed": []},
        GrievanceTicket.ISSUE_TYPE_INAPPROPRIATE_STAFF_CONDUCT: {
            "required": [],
            "not_allowed": [],
        },
        GrievanceTicket.ISSUE_TYPE_UNAUTHORIZED_USE: {
            "required": [],
            "not_allowed": [],
        },
        GrievanceTicket.ISSUE_TYPE_CONFLICT_OF_INTEREST: {
            "required": [],
            "not_allowed": [],
        },
        GrievanceTicket.ISSUE_TYPE_GROSS_MISMANAGEMENT: {
            "required": [],
            "not_allowed": [],
        },
        GrievanceTicket.ISSUE_TYPE_PERSONAL_DISPUTES: {
            "required": [],
            "not_allowed": [],
        },
        GrievanceTicket.ISSUE_TYPE_SEXUAL_HARASSMENT: {
            "required": [],
            "not_allowed": [],
        },
        GrievanceTicket.ISSUE_TYPE_MISCELLANEOUS: {"required": [], "not_allowed": []},
    }

    def get_queryset(self) -> QuerySet:
        to_prefetch = []
        for key, value in GrievanceTicket.SEARCH_TICKET_TYPES_LOOKUPS.items():
            to_prefetch.append(key)
            if "household" in value:
                to_prefetch.append(f"{key}__{value['household']}")
                to_prefetch.append(f"{key}__{value['household']}__admin2")
            if "golden_records_individual" in value:
                to_prefetch.append(f"{key}__{value['golden_records_individual']}__household")
                to_prefetch.append(f"{key}__{value['golden_records_individual']}__household__admin2")
        return (
            super()
            .get_queryset()
            .filter(self.grievance_permissions_query)
            .select_related("admin2", "assigned_to", "created_by")
            .prefetch_related("programs", *to_prefetch)
            .annotate(
                total=Case(
                    When(
                        status=GrievanceTicket.STATUS_CLOSED,
                        then=F("updated_at") - F("created_at"),
                    ),
                    default=timezone.now() - F("created_at"),  # type: ignore
                    output_field=DateField(),
                )
            )
            .annotate(total_days=F("total__day"))
            .order_by("created_at")
        )

    @etag_decorator(GrievanceTicketListKeyConstructor)
    @cache_response(timeout=config.REST_API_TTL, key_func=GrievanceTicketListKeyConstructor())
    def list(self, request: Any, *args: Any, **kwargs: Any) -> Any:
        return super().list(request, *args, **kwargs)

    @extend_schema(responses={201: GrievanceTicketDetailSerializer(many=True)})
    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # TODO: check later
        # if serializer.validated_data.get("documentation"):
        #     self.has_permission(request, Permissions.GRIEVANCE_DOCUMENTS_UPLOAD, self.business_area)

        user: AbstractUser = request.user  # type: ignore
        input_data = serializer.validated_data

        if input_data.get("category") in (
            GrievanceTicket.CATEGORY_NEGATIVE_FEEDBACK,
            GrievanceTicket.CATEGORY_POSITIVE_FEEDBACK,
        ):
            raise ValidationError("Feedback tickets are not allowed to be created through this mutation.")

        verify_required_arguments(input_data, "category", self.CATEGORY_OPTIONS)
        if input_data.get("issue_type"):
            verify_required_arguments(input_data, "issue_type", self.ISSUE_TYPE_OPTIONS)

        details_creator = TicketDetailsCreatorFactory.get_for_category(input_data.get("category"))
        creator = TicketCreatorService(details_creator)
        grievances = creator.create(user, self.business_area, input_data)

        resp = GrievanceTicketDetailSerializer(grievances, many=True)
        headers = self.get_success_headers(resp.data)
        return Response(resp.data, status=status.HTTP_201_CREATED, headers=headers)


class GrievanceTicketGlobalViewSet(
    BusinessAreaVisibilityMixin,
    GrievancePermissionsMixin,
    SerializerActionMixin,
    CountActionMixin,
    ListModelMixin,
    RetrieveModelMixin,
    BaseViewSet,
):
    queryset = GrievanceTicket.objects.all()
    serializer_classes_by_action = {
        "list": GrievanceTicketListSerializer,
        "retrieve": GrievanceTicketDetailSerializer,
        "choices": GrievanceChoicesSerializer,
    }
    permissions_by_action = {
        "list": [
            Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE,
            Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE_AS_CREATOR,
            Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE_AS_OWNER,
            Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE,
            Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE_AS_CREATOR,
            Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE_AS_OWNER,
        ],
        "retrieve": [
            Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE,
            Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE_AS_CREATOR,
            Permissions.GRIEVANCES_VIEW_DETAILS_EXCLUDING_SENSITIVE_AS_OWNER,
            Permissions.GRIEVANCES_VIEW_DETAILS_SENSITIVE,
            Permissions.GRIEVANCES_VIEW_DETAILS_SENSITIVE_AS_CREATOR,
            Permissions.GRIEVANCES_VIEW_DETAILS_SENSITIVE_AS_OWNER,
        ],
        "choices": [
            Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE,
            Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE_AS_CREATOR,
            Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE_AS_OWNER,
            Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE,
            Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE_AS_CREATOR,
            Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE_AS_OWNER,
        ],
    }
    filter_backends = (OrderingFilter, DjangoFilterBackend)
    filterset_class = GrievanceTicketFilter
    admin_area_model_fields = ["admin2"]
    program_model_field = "programs"

    def get_queryset(self) -> QuerySet:
        to_prefetch = []
        for key, value in GrievanceTicket.SEARCH_TICKET_TYPES_LOOKUPS.items():
            to_prefetch.append(key)
            if "household" in value:
                to_prefetch.append(f"{key}__{value['household']}")
            if "golden_records_individual" in value:
                to_prefetch.append(f"{key}__{value['golden_records_individual']}__household")
        return (
            super()
            .get_queryset()
            .filter(self.grievance_permissions_query)
            .select_related("admin2", "assigned_to", "created_by")
            .prefetch_related("programs", *to_prefetch)
            .annotate(
                total=Case(
                    When(
                        status=GrievanceTicket.STATUS_CLOSED,
                        then=F("updated_at") - F("created_at"),
                    ),
                    default=timezone.now() - F("created_at"),  # type: ignore
                    output_field=DateField(),
                )
            )
            .annotate(total_days=F("total__day"))
            .order_by("created_at")
        )

    @action(detail=False, methods=["get"])
    def choices(self, request: Any, *args: Any, **kwargs: Any) -> Any:
        return Response(data=self.get_serializer(instance={}).data)
