import itertools
from typing import TYPE_CHECKING, Any

from constance import config
from django.db import transaction
from django.db.models import (
    Avg,
    Case,
    CharField,
    Count,
    DateField,
    F,
    Q,
    QuerySet,
    Value,
    When,
)
from django.db.models.functions import Extract
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.encoding import force_str
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.filters import OrderingFilter
from rest_framework.mixins import (
    CreateModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
)
from rest_framework.parsers import JSONParser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_extensions.cache.decorators import cache_response

from hope.api.caches import etag_decorator
from hope.apps.account.permissions import (
    Permissions,
    check_creator_or_owner_permission,
    check_permissions,
    has_creator_or_owner_permission,
)
from hope.apps.activity_log.models import log_create
from hope.apps.core.api.mixins import (
    BaseViewSet,
    BusinessAreaVisibilityMixin,
    CountActionMixin,
    ProgramVisibilityMixin,
    SerializerActionMixin,
)
from hope.apps.core.api.parsers import DictDrfNestedParser
from hope.apps.core.api.serializers import FieldAttributeSerializer
from hope.apps.core.field_attributes.core_fields_attributes import FieldFactory
from hope.apps.core.field_attributes.fields_types import Scope
from hope.apps.core.models import FlexibleAttribute
from hope.apps.core.utils import check_concurrency_version_in_mutation, sort_by_attr
from hope.apps.grievance.api.caches import GrievanceTicketListKeyConstructor
from hope.apps.grievance.api.mixins import (
    GrievanceMutationMixin,
    GrievancePermissionsMixin,
)
from hope.apps.grievance.api.serializers.dashboard import GrievanceDashboardSerializer
from hope.apps.grievance.api.serializers.grievance_ticket import (
    BulkGrievanceTicketsAddNoteSerializer,
    BulkUpdateGrievanceTicketsAssigneesSerializer,
    BulkUpdateGrievanceTicketsPrioritySerializer,
    BulkUpdateGrievanceTicketsUrgencySerializer,
    CreateGrievanceTicketSerializer,
    GrievanceChoicesSerializer,
    GrievanceCreateNoteSerializer,
    GrievanceDeleteHouseholdApproveStatusSerializer,
    GrievanceHouseholdDataChangeApproveSerializer,
    GrievanceIndividualDataChangeApproveSerializer,
    GrievanceNeedsAdjudicationApproveSerializer,
    GrievanceReassignRoleSerializer,
    GrievanceStatusChangeSerializer,
    GrievanceTicketDetailSerializer,
    GrievanceTicketListSerializer,
    GrievanceUpdateApproveStatusSerializer,
    TicketNoteSerializer,
    UpdateGrievanceTicketSerializer,
)
from hope.apps.grievance.filters import GrievanceTicketFilter
from hope.apps.grievance.models import (
    GrievanceTicket,
    TicketNeedsAdjudicationDetails,
    TicketNote,
)
from hope.apps.grievance.notifications import GrievanceNotification
from hope.apps.grievance.services.bulk_action_service import BulkActionService
from hope.apps.grievance.services.data_change_services import update_data_change_extras
from hope.apps.grievance.services.payment_verification_services import (
    update_ticket_payment_verification_service,
)
from hope.apps.grievance.services.referral_services import update_referral_service
from hope.apps.grievance.services.ticket_based_on_payment_record_services import (
    update_ticket_based_on_payment_record_service,
)
from hope.apps.grievance.services.ticket_creator_service import (
    TicketCreatorService,
    TicketDetailsCreatorFactory,
)
from hope.apps.grievance.services.ticket_status_changer_service import (
    TicketStatusChangerService,
)
from hope.apps.grievance.utils import (
    clear_cache,
    validate_individual_for_need_adjudication,
)
from hope.apps.grievance.validators import DataChangeValidator
from hope.apps.household.models import HEAD, Household, IndividualRoleInHousehold
from hope.apps.utils.exceptions import log_and_raise

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractUser


TICKET_ORDERING_KEYS = [
    "Data Change",
    "Grievance Complaint",
    "Needs Adjudication",
    "Negative Feedback",
    "Payment Verification",
    "Positive Feedback",
    "Referral",
    "Sensitive Grievance",
    "System Flagging",
]

TICKET_ORDERING = {
    "Data Change": 0,
    "Grievance Complaint": 1,
    "Needs Adjudication": 2,
    "Negative Feedback": 3,
    "Payment Verification": 4,
    "Positive Feedback": 5,
    "Referral": 6,
    "Sensitive Grievance": 7,
    "System Flagging": 8,
}


def transform_to_chart_dataset(qs: QuerySet) -> dict[str, Any]:
    labels, data = [], []
    for q in qs:
        label, value = q
        labels.append(label)
        data.append(value)

    return {"labels": labels, "datasets": [{"data": data}]}


def display_value(choices: tuple, field: str, default_field: Any = None) -> Case:
    options = [When(**{field: k, "then": Value(force_str(v))}) for k, v in choices]
    return Case(*options, default=default_field, output_field=CharField())


def create_type_generated_queries() -> tuple[Q, Q]:
    user_generated, system_generated = Q(), Q()
    for category in GrievanceTicket.CATEGORY_CHOICES:
        category_num, category_str = category
        if category_num in dict(GrievanceTicket.MANUAL_CATEGORIES):
            user_generated |= Q(category_name=force_str(category_str))
        else:
            system_generated |= Q(category_name=force_str(category_str))
    return user_generated, system_generated


class GrievanceDashboardMixin:
    """Common dashboard logic for grievance tickets."""

    def get_dashboard_base_queryset(self, program: Any = None) -> QuerySet:
        """Get base queryset for dashboard data with optional program filtering."""
        base_queryset = GrievanceTicket.objects.filter(ignored=False, business_area__slug=self.business_area_slug)

        if program:
            base_queryset = base_queryset.filter(programs__in=[program])

        return base_queryset

    def get_dashboard_data(self, base_queryset: QuerySet) -> dict[str, Any]:
        """Generate dashboard data from base queryset."""
        # Tickets by type data
        user_generated, system_generated = create_type_generated_queries()
        tickets_by_type = (
            base_queryset.annotate(
                category_name=display_value(GrievanceTicket.CATEGORY_CHOICES, "category"),
                days_diff=Extract(F("updated_at") - F("created_at"), "days"),
            )
            .values_list("category_name", "days_diff")
            .aggregate(
                user_generated_count=Count("category_name", filter=user_generated),
                system_generated_count=Count("category_name", filter=system_generated),
                closed_user_generated_count=Count("category_name", filter=user_generated & Q(status=6)),
                closed_system_generated_count=Count("category_name", filter=system_generated & Q(status=6)),
                user_generated_avg_resolution=Avg("days_diff", filter=user_generated & Q(status=6)),
                system_generated_avg_resolution=Avg("days_diff", filter=system_generated & Q(status=6)),
            )
        )

        # Handle None values
        tickets_by_type = {k: (0.00 if v is None else v) for k, v in tickets_by_type.items()}
        tickets_by_type["user_generated_avg_resolution"] = round(tickets_by_type["user_generated_avg_resolution"], 2)
        tickets_by_type["system_generated_avg_resolution"] = round(
            tickets_by_type["system_generated_avg_resolution"], 2
        )

        # Tickets by category data
        tickets_by_category_qs = (
            base_queryset.annotate(category_name=display_value(GrievanceTicket.CATEGORY_CHOICES, "category"))
            .values("category_name")
            .annotate(count=Count("category"))
            .values_list("category_name", "count")
            .order_by("-count")
        )
        tickets_by_category = transform_to_chart_dataset(tickets_by_category_qs)

        # Tickets by status data
        tickets_by_status_qs = (
            base_queryset.annotate(status_name=display_value(GrievanceTicket.STATUS_CHOICES, "status"))
            .values("status_name")
            .annotate(count=Count("status"))
            .values_list("status_name", "count")
            .order_by("-count", "status_name")
        )
        tickets_by_status = transform_to_chart_dataset(tickets_by_status_qs)

        # Tickets by location and category data
        tickets_by_location_qs = (
            base_queryset.select_related("admin2")
            .values_list("admin2__name", "category")
            .annotate(
                category_name=display_value(GrievanceTicket.CATEGORY_CHOICES, "category"),
                count=Count("category"),
            )
            .order_by("admin2__name", "-count")
        )

        results, labels, totals = [], [], []
        for key, group in itertools.groupby(tickets_by_location_qs, lambda x: x[0]):
            if key is None:
                continue

            labels.append(key)
            ticket_horizontal_counts = [0 for _ in range(9)]

            for item in group:
                _, _, ticket_name, ticket_count = item
                idx = TICKET_ORDERING[ticket_name]
                ticket_horizontal_counts[idx] = ticket_count
            results.append(ticket_horizontal_counts)

        ticket_vertical_counts = list(zip(*results, strict=True)) if results else []

        for key, value in enumerate(ticket_vertical_counts):
            totals.append({"label": TICKET_ORDERING_KEYS[key], "data": list(value)})

        tickets_by_location_and_category = {"labels": labels, "datasets": totals}

        return {
            "tickets_by_type": tickets_by_type,
            "tickets_by_status": tickets_by_status,
            "tickets_by_category": tickets_by_category,
            "tickets_by_location_and_category": tickets_by_location_and_category,
        }


class GrievanceTicketViewSet(
    ProgramVisibilityMixin,
    GrievancePermissionsMixin,
    GrievanceDashboardMixin,
    CountActionMixin,
    ListModelMixin,
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
            .prefetch_related("programs", "programs__sanction_lists", *to_prefetch)
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
            .order_by("-created_at")
        )

    @etag_decorator(GrievanceTicketListKeyConstructor)
    @cache_response(timeout=config.REST_API_TTL, key_func=GrievanceTicketListKeyConstructor())
    def list(self, request: Any, *args: Any, **kwargs: Any) -> Any:
        return super().list(request, *args, **kwargs)

    @extend_schema(responses={200: GrievanceDashboardSerializer})
    @action(detail=False, methods=["get"], url_path="dashboard")
    def dashboard(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Get grievance dashboard data filtered by program."""
        base_queryset = self.get_dashboard_base_queryset(self.program)
        dashboard_data = self.get_dashboard_data(base_queryset)
        return Response(dashboard_data, status=status.HTTP_200_OK)


class GrievanceTicketGlobalViewSet(
    BusinessAreaVisibilityMixin,
    GrievancePermissionsMixin,
    GrievanceDashboardMixin,
    SerializerActionMixin,
    CountActionMixin,
    ListModelMixin,
    RetrieveModelMixin,
    CreateModelMixin,
    UpdateModelMixin,
    BaseViewSet,
    GrievanceMutationMixin,
    DataChangeValidator,
):
    queryset = GrievanceTicket.objects.all()
    serializer_classes_by_action = {
        "list": GrievanceTicketListSerializer,
        "retrieve": GrievanceTicketDetailSerializer,
        "choices": GrievanceChoicesSerializer,
        "create": CreateGrievanceTicketSerializer,
        "partial_update": UpdateGrievanceTicketSerializer,
        "status_change": GrievanceStatusChangeSerializer,
        "create_note": GrievanceCreateNoteSerializer,
        "approve_individual_data_change": GrievanceIndividualDataChangeApproveSerializer,
        "approve_household_data_change": GrievanceHouseholdDataChangeApproveSerializer,
        "approve_status_update": GrievanceUpdateApproveStatusSerializer,
        "approve_delete_household": GrievanceDeleteHouseholdApproveStatusSerializer,
        "approve_needs_adjudication": GrievanceNeedsAdjudicationApproveSerializer,
        "approve_payment_details": GrievanceUpdateApproveStatusSerializer,
        "reassign_role": GrievanceReassignRoleSerializer,
        "bulk_update_assignee": BulkUpdateGrievanceTicketsAssigneesSerializer,
        "bulk_update_priority": BulkUpdateGrievanceTicketsPrioritySerializer,
        "bulk_update_urgency": BulkUpdateGrievanceTicketsUrgencySerializer,
        "bulk_add_note": BulkGrievanceTicketsAddNoteSerializer,
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
        "create": [Permissions.GRIEVANCES_CREATE],
        "partial_update": [
            Permissions.GRIEVANCES_UPDATE,
            Permissions.GRIEVANCES_UPDATE_AS_CREATOR,
            Permissions.GRIEVANCES_UPDATE_AS_OWNER,
        ],
        "status_change": [
            Permissions.GRIEVANCES_UPDATE,
            Permissions.GRIEVANCES_UPDATE_AS_CREATOR,
            Permissions.GRIEVANCES_UPDATE_AS_OWNER,
            Permissions.GRIEVANCES_SET_IN_PROGRESS,
            Permissions.GRIEVANCES_SET_IN_PROGRESS_AS_CREATOR,
            Permissions.GRIEVANCES_SET_IN_PROGRESS_AS_OWNER,
            Permissions.GRIEVANCES_SET_IN_PROGRESS,
            Permissions.GRIEVANCES_SET_IN_PROGRESS_AS_CREATOR,
            Permissions.GRIEVANCES_SET_IN_PROGRESS_AS_OWNER,
            Permissions.GRIEVANCES_SEND_BACK,
            Permissions.GRIEVANCES_SEND_BACK_AS_CREATOR,
            Permissions.GRIEVANCES_SEND_BACK_AS_OWNER,
            Permissions.GRIEVANCES_SET_ON_HOLD,
            Permissions.GRIEVANCES_SET_ON_HOLD_AS_CREATOR,
            Permissions.GRIEVANCES_SET_ON_HOLD_AS_OWNER,
            Permissions.GRIEVANCES_CLOSE_TICKET_FEEDBACK,
            Permissions.GRIEVANCES_CLOSE_TICKET_FEEDBACK_AS_CREATOR,
            Permissions.GRIEVANCES_CLOSE_TICKET_FEEDBACK_AS_OWNER,
            Permissions.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK,
            Permissions.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK_AS_CREATOR,
            Permissions.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK_AS_OWNER,
        ],
        "create_note": [
            Permissions.GRIEVANCES_ADD_NOTE,
            Permissions.GRIEVANCES_ADD_NOTE_AS_CREATOR,
            Permissions.GRIEVANCES_ADD_NOTE_AS_OWNER,
        ],
        "approve_individual_data_change": [
            Permissions.GRIEVANCES_APPROVE_DATA_CHANGE,
            Permissions.GRIEVANCES_APPROVE_DATA_CHANGE_AS_CREATOR,
            Permissions.GRIEVANCES_APPROVE_DATA_CHANGE_AS_OWNER,
        ],
        "approve_household_data_change": [
            Permissions.GRIEVANCES_APPROVE_DATA_CHANGE,
            Permissions.GRIEVANCES_APPROVE_DATA_CHANGE_AS_CREATOR,
            Permissions.GRIEVANCES_APPROVE_DATA_CHANGE_AS_OWNER,
        ],
        "approve_status_update": [
            Permissions.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE,
            Permissions.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE_AS_CREATOR,
            Permissions.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE_AS_OWNER,
        ],
        "approve_delete_household": [
            Permissions.GRIEVANCES_APPROVE_DATA_CHANGE,
            Permissions.GRIEVANCES_APPROVE_DATA_CHANGE_AS_CREATOR,
            Permissions.GRIEVANCES_APPROVE_DATA_CHANGE_AS_OWNER,
        ],
        "approve_needs_adjudication": [
            Permissions.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE,
            Permissions.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE_AS_CREATOR,
            Permissions.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE_AS_OWNER,
        ],
        "approve_payment_details": [
            Permissions.GRIEVANCES_APPROVE_PAYMENT_VERIFICATION,
            Permissions.GRIEVANCES_APPROVE_PAYMENT_VERIFICATION_AS_CREATOR,
            Permissions.GRIEVANCES_APPROVE_PAYMENT_VERIFICATION_AS_OWNER,
        ],
        "reassign_role": [Permissions.GRIEVANCES_UPDATE],
        "bulk_update_assignee": [Permissions.GRIEVANCES_UPDATE],
        "bulk_update_priority": [Permissions.GRIEVANCES_UPDATE],
        "bulk_update_urgency": [Permissions.GRIEVANCES_UPDATE],
        "bulk_add_note": [Permissions.GRIEVANCES_UPDATE],
        "all_edit_household_fields_attributes": [Permissions.GRIEVANCES_CREATE],
        "all_edit_people_fields_attributes": [Permissions.GRIEVANCES_CREATE],
        "all_add_individuals_fields_attributes": [Permissions.GRIEVANCES_CREATE],
        "dashboard": [
            Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE,
            Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE_AS_CREATOR,
            Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE_AS_OWNER,
            Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE,
            Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE_AS_CREATOR,
            Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE_AS_OWNER,
        ],
    }
    http_method_names = ["get", "post", "patch"]
    filter_backends = (OrderingFilter, DjangoFilterBackend)
    filterset_class = GrievanceTicketFilter
    admin_area_model_fields = ["admin2"]
    program_model_field = "programs"
    parser_classes = (DictDrfNestedParser, JSONParser)

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
            .distinct()
            .order_by("-created_at")
        )

    @action(detail=False, methods=["get"])
    def choices(self, request: Any, *args: Any, **kwargs: Any) -> Any:
        return Response(data=self.get_serializer(instance={}).data)

    @transaction.atomic
    @extend_schema(responses={201: GrievanceTicketDetailSerializer(many=True)})
    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user: AbstractUser = request.user  # type: ignore
        input_data = serializer.validated_data
        # check if user has access to the program
        program = input_data.get("program")
        if program and not check_permissions(
            user,
            self.get_permissions_for_action(),
            business_area=self.business_area,
            program=program.slug,
        ):
            raise PermissionDenied

        if input_data.get("documentation") and not check_permissions(
            user,
            [Permissions.GRIEVANCE_DOCUMENTS_UPLOAD],
            business_area=self.business_area,
            program=program.slug if program else None,
        ):
            raise PermissionDenied

        if input_data.get("category") in (
            GrievanceTicket.CATEGORY_NEGATIVE_FEEDBACK,
            GrievanceTicket.CATEGORY_POSITIVE_FEEDBACK,
        ):
            raise ValidationError("Feedback tickets are not allowed to be created through this mutation.")

        self.verify_required_arguments(input_data, "category", self.CREATE_CATEGORY_OPTIONS)

        if input_data.get("issue_type"):
            self.verify_required_arguments(input_data, "issue_type", self.CREATE_ISSUE_TYPE_OPTIONS)

        details_creator = TicketDetailsCreatorFactory.get_for_category(input_data.get("category"))
        creator = TicketCreatorService(details_creator)
        grievances = creator.create(user, self.business_area, input_data)

        resp = GrievanceTicketDetailSerializer(grievances, many=True)
        headers = self.get_success_headers(resp.data)
        return Response(resp.data, status=status.HTTP_201_CREATED, headers=headers)

    @transaction.atomic
    @extend_schema(responses={200: GrievanceTicketDetailSerializer})
    def partial_update(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        grievance_ticket = self.get_object()
        user = request.user
        serializer = self.get_serializer(grievance_ticket, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        input_data = serializer.validated_data

        old_grievance_ticket = get_object_or_404(GrievanceTicket, id=str(grievance_ticket.id))

        check_concurrency_version_in_mutation(input_data.get("version"), grievance_ticket)
        check_creator_or_owner_permission(
            user,
            Permissions.GRIEVANCES_UPDATE,
            grievance_ticket.created_by == user,
            Permissions.GRIEVANCES_UPDATE_AS_CREATOR,
            grievance_ticket.assigned_to == user,
            Permissions.GRIEVANCES_UPDATE_AS_OWNER,
            self.business_area,
            grievance_ticket.programs.first(),
        )

        if grievance_ticket.status == GrievanceTicket.STATUS_CLOSED:
            raise ValidationError("Grievance Ticket in status Closed is not editable")

        if grievance_ticket.issue_type:
            self.verify_required_arguments(input_data, "issue_type", self.UPDATE_EXTRAS_OPTIONS)

        extras = input_data.pop("extras", {})
        grievance_ticket = self.update_basic_data(user, input_data, grievance_ticket)  # type: ignore

        update_extra_methods = {
            GrievanceTicket.CATEGORY_REFERRAL: update_referral_service,
            GrievanceTicket.CATEGORY_PAYMENT_VERIFICATION: update_ticket_payment_verification_service,
            GrievanceTicket.CATEGORY_SENSITIVE_GRIEVANCE: update_ticket_based_on_payment_record_service,
            GrievanceTicket.CATEGORY_GRIEVANCE_COMPLAINT: update_ticket_based_on_payment_record_service,
        }
        if has_creator_or_owner_permission(
            user,
            Permissions.GRIEVANCES_UPDATE_REQUESTED_DATA_CHANGE,
            grievance_ticket.created_by == user,
            Permissions.GRIEVANCES_UPDATE_REQUESTED_DATA_CHANGE_AS_CREATOR,
            grievance_ticket.assigned_to == user,
            Permissions.GRIEVANCES_UPDATE_REQUESTED_DATA_CHANGE_AS_OWNER,
            self.business_area,
            grievance_ticket.programs.first(),
        ):
            update_extra_methods[GrievanceTicket.CATEGORY_DATA_CHANGE] = update_data_change_extras
        if update_extra_method := update_extra_methods.get(grievance_ticket.category):
            grievance_ticket = update_extra_method(grievance_ticket, extras, input_data)
        log_create(
            GrievanceTicket.ACTIVITY_LOG_MAPPING,
            "business_area",
            user,
            grievance_ticket.programs.all(),
            old_grievance_ticket,
            grievance_ticket,
        )
        resp = GrievanceTicketDetailSerializer(grievance_ticket)
        return Response(resp.data, status.HTTP_200_OK)

    @transaction.atomic
    @extend_schema(
        request=GrievanceStatusChangeSerializer,
        responses={202: GrievanceTicketDetailSerializer},
    )
    @action(detail=True, methods=["post"], url_path="status-change")
    def status_change(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        grievance_ticket = self.get_object()
        serializer = self.get_serializer(grievance_ticket, data=request.data)
        serializer.is_valid(raise_exception=True)
        input_data = serializer.validated_data

        user = request.user
        new_status = input_data["status"]
        notifications = []
        old_grievance_ticket = get_object_or_404(GrievanceTicket, id=grievance_ticket.pk)
        check_concurrency_version_in_mutation(input_data.get("version"), grievance_ticket)
        if grievance_ticket.category in (
            GrievanceTicket.CATEGORY_NEGATIVE_FEEDBACK,
            GrievanceTicket.CATEGORY_POSITIVE_FEEDBACK,
        ):
            raise ValidationError("Feedback tickets are not allowed to be created through this mutation.")

        if grievance_ticket.status == new_status:
            return Response(
                GrievanceTicketDetailSerializer(grievance_ticket).data,
                status=status.HTTP_202_ACCEPTED,
            )
        if permissions_to_use := self.get_permissions_for_status_change(
            new_status, grievance_ticket.status, grievance_ticket.is_feedback
        ):
            check_creator_or_owner_permission(
                user,
                permissions_to_use[0],
                grievance_ticket.created_by == user,
                permissions_to_use[1],
                grievance_ticket.assigned_to == user,
                permissions_to_use[2],
                grievance_ticket.business_area,
                grievance_ticket.programs.first(),
            )

        if new_status == GrievanceTicket.STATUS_ASSIGNED and not grievance_ticket.assigned_to:
            if not check_permissions(
                user,
                [Permissions.GRIEVANCE_ASSIGN],
                business_area=self.business_area,
                program=grievance_ticket.programs.first(),
            ):
                raise PermissionDenied

            notifications.append(
                GrievanceNotification(grievance_ticket, GrievanceNotification.ACTION_ASSIGNMENT_CHANGED)
            )
        if new_status == GrievanceTicket.STATUS_CLOSED and isinstance(
            grievance_ticket.ticket_details, TicketNeedsAdjudicationDetails
        ):
            partner = user.partner

            for selected_individual in grievance_ticket.ticket_details.selected_individuals.all():
                if not partner.has_area_access(
                    area_id=selected_individual.household.admin2.id,
                    program_id=selected_individual.program.id,
                ):
                    raise PermissionDenied("Permission Denied: User does not have access to close ticket")

        if not grievance_ticket.can_change_status(new_status):
            log_and_raise("New status is incorrect")
        status_changer = TicketStatusChangerService(grievance_ticket, user)  # type: ignore
        status_changer.change_status(new_status)

        grievance_ticket.refresh_from_db()

        if grievance_ticket.status == GrievanceTicket.STATUS_FOR_APPROVAL:
            notifications.append(GrievanceNotification(grievance_ticket, GrievanceNotification.ACTION_SEND_TO_APPROVAL))

        if grievance_ticket.status == GrievanceTicket.STATUS_CLOSED:
            clear_cache(grievance_ticket.ticket_details, grievance_ticket.business_area.slug)

        if (
            old_grievance_ticket.status == GrievanceTicket.STATUS_FOR_APPROVAL
            and grievance_ticket.status == GrievanceTicket.STATUS_IN_PROGRESS
        ):
            notifications.append(
                GrievanceNotification(
                    grievance_ticket,
                    GrievanceNotification.ACTION_SEND_BACK_TO_IN_PROGRESS,
                    approver=user,
                )
            )
        log_create(
            GrievanceTicket.ACTIVITY_LOG_MAPPING,
            "business_area",
            user,
            grievance_ticket.programs.all(),
            old_grievance_ticket,
            grievance_ticket,
        )

        GrievanceNotification.send_all_notifications(notifications)
        return Response(
            GrievanceTicketDetailSerializer(grievance_ticket, context={"request": request}).data,
            status=status.HTTP_202_ACCEPTED,
        )

    @transaction.atomic
    @extend_schema(request=GrievanceCreateNoteSerializer, responses={201: TicketNoteSerializer})
    @action(detail=True, methods=["post"], url_path="create-note")
    def create_note(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        grievance_ticket = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        input_data = serializer.validated_data
        user = request.user

        check_concurrency_version_in_mutation(kwargs.get("version"), grievance_ticket)
        check_creator_or_owner_permission(
            user,
            Permissions.GRIEVANCES_ADD_NOTE,
            grievance_ticket.created_by == user,
            Permissions.GRIEVANCES_ADD_NOTE_AS_CREATOR,
            grievance_ticket.assigned_to == user,
            Permissions.GRIEVANCES_ADD_NOTE_AS_OWNER,
            self.business_area,
            grievance_ticket.programs.first(),
        )

        description = input_data["description"]
        ticket_note = TicketNote.objects.create(ticket=grievance_ticket, description=description, created_by=user)
        notification = GrievanceNotification(
            grievance_ticket,
            GrievanceNotification.ACTION_NOTES_ADDED,
            created_by=user,
            ticket_note=ticket_note,
        )
        notification.send_email_notification()

        return Response(TicketNoteSerializer(ticket_note).data, status=status.HTTP_201_CREATED)

    @transaction.atomic
    @extend_schema(
        request=GrievanceIndividualDataChangeApproveSerializer,
        responses={202: GrievanceTicketDetailSerializer},
    )
    @action(detail=True, methods=["post"], url_path="approve-individual-data-change")
    def approve_individual_data_change(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        grievance_ticket = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        input_data = serializer.validated_data
        individual_approve_data = input_data.get("individual_approve_data", {})
        flex_fields_approve_data = input_data.get("flex_fields_approve_data", {})
        user = request.user

        check_concurrency_version_in_mutation(input_data.get("version"), grievance_ticket)
        check_creator_or_owner_permission(
            user,
            Permissions.GRIEVANCES_APPROVE_DATA_CHANGE,
            grievance_ticket.created_by == user,
            Permissions.GRIEVANCES_APPROVE_DATA_CHANGE_AS_CREATOR,
            grievance_ticket.assigned_to == user,
            Permissions.GRIEVANCES_APPROVE_DATA_CHANGE_AS_OWNER,
            self.business_area,
            grievance_ticket.programs.first(),
        )

        self.verify_approve_data(individual_approve_data)
        self.verify_approve_data(flex_fields_approve_data)
        individual_data_details = grievance_ticket.individual_data_update_ticket_details
        individual_data = individual_data_details.individual_data
        if individual_approve_data:
            self.verify_approve_data_against_object_data(individual_data, individual_approve_data)
        if flex_fields_approve_data:
            self.verify_approve_data_against_object_data(individual_data.get("flex_fields"), flex_fields_approve_data)

        documents_mapping = {
            "documents": input_data.get("approved_documents_to_create", []),
            "documents_to_remove": input_data.get("approved_documents_to_remove", []),
            "documents_to_edit": input_data.get("approved_documents_to_edit", []),
            "identities": input_data.get("approved_identities_to_create", []),
            "identities_to_remove": input_data.get("approved_identities_to_remove", []),
            "identities_to_edit": input_data.get("approved_identities_to_edit", []),
            "accounts": input_data.get("approved_accounts_to_create", []),
            "accounts_to_edit": input_data.get("approved_accounts_to_edit", []),
        }

        for field_name, item in individual_data.items():
            field_to_approve = individual_approve_data.get(field_name)
            if field_name in documents_mapping:
                for index, document_data in enumerate(individual_data[field_name]):
                    approved_documents_indexes = documents_mapping.get(field_name, [])
                    document_data["approve_status"] = index in approved_documents_indexes
            elif field_name == "flex_fields":
                for flex_field_name in item:
                    individual_data["flex_fields"][flex_field_name]["approve_status"] = flex_fields_approve_data.get(
                        flex_field_name
                    )
            elif field_to_approve:
                individual_data[field_name]["approve_status"] = True
            else:
                individual_data[field_name]["approve_status"] = False

        individual_data_details.individual_data = individual_data
        individual_data_details.save()
        grievance_ticket.refresh_from_db()

        return Response(
            GrievanceTicketDetailSerializer(grievance_ticket).data,
            status=status.HTTP_202_ACCEPTED,
        )

    @transaction.atomic
    @extend_schema(
        request=GrievanceHouseholdDataChangeApproveSerializer,
        responses={202: GrievanceTicketDetailSerializer},
    )
    @action(detail=True, methods=["post"], url_path="approve-household-data-change")
    def approve_household_data_change(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        grievance_ticket = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        input_data = serializer.validated_data
        household_approve_data = input_data.get("household_approve_data", {})
        flex_fields_approve_data = input_data.get("flex_fields_approve_data", {})
        user = self.request.user

        check_concurrency_version_in_mutation(input_data.get("version"), grievance_ticket)
        check_creator_or_owner_permission(
            user,
            Permissions.GRIEVANCES_APPROVE_DATA_CHANGE,
            grievance_ticket.created_by == user,
            Permissions.GRIEVANCES_APPROVE_DATA_CHANGE_AS_CREATOR,
            grievance_ticket.assigned_to == user,
            Permissions.GRIEVANCES_APPROVE_DATA_CHANGE_AS_OWNER,
            self.business_area,
            grievance_ticket.programs.first(),
        )

        self.verify_approve_data(household_approve_data)
        self.verify_approve_data(flex_fields_approve_data)
        household_data_details = grievance_ticket.household_data_update_ticket_details
        household_data = household_data_details.household_data
        self.verify_approve_data_against_object_data(household_data, household_approve_data)
        self.verify_approve_data_against_object_data(household_data.get("flex_fields"), flex_fields_approve_data)

        for field_name, item in household_data.items():
            if field_name == "flex_fields":
                for flex_field_name in item:
                    household_data["flex_fields"][flex_field_name]["approve_status"] = flex_fields_approve_data.get(
                        flex_field_name
                    )
            elif field_name == "roles":
                approve_lookup = {
                    role["individual_id"]: str(role.get("approve_status", "")).lower() == "true"
                    for role in household_approve_data.get("roles", [])
                }
                household_data["roles"] = [
                    {**role, "approve_status": approve_lookup.get(role["individual_id"], False)}
                    for role in household_data.get("roles", [])
                ]
            elif household_approve_data.get(field_name):
                household_data[field_name]["approve_status"] = True
            else:
                household_data[field_name]["approve_status"] = False

        household_data_details.household_data = household_data
        household_data_details.save()
        grievance_ticket.refresh_from_db()

        return Response(
            GrievanceTicketDetailSerializer(grievance_ticket).data,
            status=status.HTTP_202_ACCEPTED,
        )

    @transaction.atomic
    @extend_schema(
        request=GrievanceUpdateApproveStatusSerializer,
        responses={202: GrievanceTicketDetailSerializer},
    )
    @action(detail=True, methods=["post"], url_path="approve-status-update")
    def approve_status_update(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Approve action.

        approve_add_individual, approve_delete_individual, approve_system_flagging.
        """
        grievance_ticket = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user

        check_concurrency_version_in_mutation(serializer.validated_data.get("version"), grievance_ticket)
        if grievance_ticket.category in (
            GrievanceTicket.CATEGORY_SYSTEM_FLAGGING,
            GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION,
        ):
            check_creator_or_owner_permission(
                user,
                Permissions.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE,
                grievance_ticket.created_by == user,
                Permissions.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE_AS_CREATOR,
                grievance_ticket.assigned_to == user,
                Permissions.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE_AS_OWNER,
                self.business_area,
                grievance_ticket.programs.first(),
            )
        else:
            check_creator_or_owner_permission(
                user,
                Permissions.GRIEVANCES_APPROVE_DATA_CHANGE,
                grievance_ticket.created_by == user,
                Permissions.GRIEVANCES_APPROVE_DATA_CHANGE_AS_CREATOR,
                grievance_ticket.assigned_to == user,
                Permissions.GRIEVANCES_APPROVE_DATA_CHANGE_AS_OWNER,
                self.business_area,
                grievance_ticket.programs.first(),
            )

        ticket_details = grievance_ticket.ticket_details
        ticket_details.approve_status = serializer.validated_data.get("approve_status")
        ticket_details.save()
        grievance_ticket.refresh_from_db()

        return Response(
            GrievanceTicketDetailSerializer(grievance_ticket).data,
            status=status.HTTP_202_ACCEPTED,
        )

    @transaction.atomic
    @extend_schema(
        request=GrievanceDeleteHouseholdApproveStatusSerializer,
        responses={202: GrievanceTicketDetailSerializer},
    )
    @action(detail=True, methods=["post"], url_path="approve-delete-household")
    def approve_delete_household(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        grievance_ticket = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reason_hh_id = serializer.validated_data.get("reason_hh_id")
        user = request.user

        check_concurrency_version_in_mutation(serializer.validated_data.get("version"), grievance_ticket)
        check_creator_or_owner_permission(
            user,
            Permissions.GRIEVANCES_APPROVE_DATA_CHANGE,
            grievance_ticket.created_by == user,
            Permissions.GRIEVANCES_APPROVE_DATA_CHANGE_AS_CREATOR,
            grievance_ticket.assigned_to == user,
            Permissions.GRIEVANCES_APPROVE_DATA_CHANGE_AS_OWNER,
            self.business_area,
            grievance_ticket.programs.first(),
        )

        ticket_details = grievance_ticket.ticket_details

        reason_hh_obj = None
        reason_hh_id = reason_hh_id.strip() if reason_hh_id else None
        if reason_hh_id:
            # validate reason HH id
            reason_hh_obj = get_object_or_404(
                Household,
                unicef_id=reason_hh_id,
                program=ticket_details.household.program,
            )
            if reason_hh_obj.withdrawn:
                raise ValidationError(f"The provided household {reason_hh_obj.unicef_id} has to be active.")
            if reason_hh_obj == ticket_details.household:
                raise ValidationError(
                    f"The provided household {reason_hh_obj.unicef_id} is the same as the one being withdrawn."
                )

        # update reason_household value
        ticket_details.reason_household = reason_hh_obj  # set HH or None
        ticket_details.approve_status = serializer.validated_data["approve_status"]
        ticket_details.save()
        grievance_ticket.refresh_from_db()

        return Response(
            GrievanceTicketDetailSerializer(grievance_ticket).data,
            status=status.HTTP_202_ACCEPTED,
        )

    @transaction.atomic
    @extend_schema(
        request=GrievanceNeedsAdjudicationApproveSerializer,
        responses={202: GrievanceTicketDetailSerializer},
    )
    @action(detail=True, methods=["post"], url_path="approve-needs-adjudication")
    def approve_needs_adjudication(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        grievance_ticket = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user

        check_concurrency_version_in_mutation(serializer.validated_data.get("version"), grievance_ticket)
        check_creator_or_owner_permission(
            user,
            Permissions.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE,
            grievance_ticket.created_by == user,
            Permissions.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE_AS_CREATOR,
            grievance_ticket.assigned_to == user,
            Permissions.GRIEVANCES_APPROVE_FLAG_AND_DEDUPE_AS_OWNER,
            self.business_area,
            grievance_ticket.programs.first(),
        )

        duplicate_individuals = serializer.validated_data.get("duplicate_individual_ids", [])
        distinct_individuals = serializer.validated_data.get("distinct_individual_ids", [])
        clear_individuals = serializer.validated_data.get("clear_individual_ids", [])
        selected_individual = serializer.validated_data.get("selected_individual_id")

        if any(
            [
                duplicate_individuals and (selected_individual or distinct_individuals or clear_individuals),
                clear_individuals and (duplicate_individuals or distinct_individuals or selected_individual),
            ]
        ):
            log_and_raise("Only one option for duplicate or distinct or clear individuals is available")

        if (
            duplicate_individuals or distinct_individuals or selected_individual
        ) and grievance_ticket.status != GrievanceTicket.STATUS_FOR_APPROVAL:
            raise ValidationError("A user can not flag individuals when a ticket is not in the 'For Approval' status")

        user = request.user
        partner = user.partner

        ticket_details: TicketNeedsAdjudicationDetails = grievance_ticket.ticket_details

        # using for old tickets
        if selected_individual:
            validate_individual_for_need_adjudication(partner, selected_individual, ticket_details)

            ticket_details.selected_individual = selected_individual
            ticket_details.role_reassign_data = {}

        if clear_individuals:
            # remove Individual from selected_individuals and selected_distinct
            ticket_details.selected_individuals.remove(*clear_individuals)
            ticket_details.selected_distinct.remove(*clear_individuals)

        if distinct_individuals:
            for individual in distinct_individuals:
                validate_individual_for_need_adjudication(partner, individual, ticket_details)

            ticket_details.selected_distinct.add(*distinct_individuals)
            ticket_details.selected_individuals.remove(*distinct_individuals)

        if duplicate_individuals:
            for individual in duplicate_individuals:
                validate_individual_for_need_adjudication(partner, individual, ticket_details)

            ticket_details.selected_individuals.add(*duplicate_individuals)
            ticket_details.selected_distinct.remove(*duplicate_individuals)

        ticket_details.save()
        grievance_ticket.refresh_from_db()

        return Response(
            GrievanceTicketDetailSerializer(grievance_ticket, context={"request": request}).data,
            status=status.HTTP_202_ACCEPTED,
        )

    @transaction.atomic
    @extend_schema(
        request=GrievanceUpdateApproveStatusSerializer,
        responses={202: GrievanceTicketDetailSerializer},
    )
    @action(detail=True, methods=["post"], url_path="approve-payment-details")
    def approve_payment_details(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        grievance_ticket = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user

        check_concurrency_version_in_mutation(serializer.validated_data.get("version"), grievance_ticket)
        check_creator_or_owner_permission(
            user,
            Permissions.GRIEVANCES_APPROVE_PAYMENT_VERIFICATION,
            grievance_ticket.created_by == user,
            Permissions.GRIEVANCES_APPROVE_PAYMENT_VERIFICATION_AS_CREATOR,
            grievance_ticket.assigned_to == user,
            Permissions.GRIEVANCES_APPROVE_PAYMENT_VERIFICATION_AS_OWNER,
            self.business_area,
            grievance_ticket.programs.first(),
        )

        if grievance_ticket.status != GrievanceTicket.STATUS_FOR_APPROVAL:
            log_and_raise("Payment Details changes can approve only for Grievance Ticket in status For Approval")

        grievance_ticket.payment_verification_ticket_details.approve_status = serializer.validated_data[
            "approve_status"
        ]
        grievance_ticket.payment_verification_ticket_details.save()
        grievance_ticket.refresh_from_db()
        return Response(
            GrievanceTicketDetailSerializer(grievance_ticket).data,
            status=status.HTTP_202_ACCEPTED,
        )

    @transaction.atomic
    @extend_schema(
        request=GrievanceReassignRoleSerializer,
        responses={202: GrievanceTicketDetailSerializer},
    )
    @action(detail=True, methods=["post"], url_path="reassign-role")
    def reassign_role(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        grievance_ticket = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        household = serializer.validated_data["household_id"]
        individual = serializer.validated_data["individual_id"]
        role = serializer.validated_data["role"]

        check_concurrency_version_in_mutation(serializer.validated_data.get("version"), grievance_ticket)
        check_concurrency_version_in_mutation(serializer.validated_data.get("household_version"), household)
        check_concurrency_version_in_mutation(serializer.validated_data.get("individual_version"), individual)

        ticket_details = grievance_ticket.ticket_details
        if grievance_ticket.category == GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION:
            if ticket_details.is_multiple_duplicates_version:
                ticket_individual = individual
            else:
                ticket_individual = ticket_details.selected_individual
        elif grievance_ticket.category == GrievanceTicket.CATEGORY_SYSTEM_FLAGGING:
            ticket_individual = ticket_details.golden_records_individual
        else:
            ticket_individual = ticket_details.individual
        self.verify_if_role_exists(household, ticket_individual, role)

        if role == HEAD:
            role_data_key = role
        else:
            role_object = get_object_or_404(
                IndividualRoleInHousehold,
                individual=ticket_individual,
                household=household,
                role=role,
            )
            role_data_key = str(role_object.id)

        ticket_details.role_reassign_data[role_data_key] = {
            "role": role,
            "household": str(household.pk),
            "individual": str(individual.id),
        }

        if getattr(ticket_details, "is_multiple_duplicates_version", False):
            ticket_details.role_reassign_data[role_data_key]["new_individual"] = str(
                serializer.validated_data["new_individual_id"].pk
            )
        ticket_details.save()
        grievance_ticket.refresh_from_db()
        return Response(
            GrievanceTicketDetailSerializer(grievance_ticket, context={"request": request}).data,
            status=status.HTTP_202_ACCEPTED,
        )

    @transaction.atomic
    @extend_schema(
        request=BulkUpdateGrievanceTicketsAssigneesSerializer,
        responses={202: GrievanceTicketDetailSerializer(many=True)},
    )
    @action(detail=False, methods=["post"], url_path="bulk-update-assignee")
    def bulk_update_assignee(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tickets = BulkActionService().bulk_assign(
            serializer.validated_data["grievance_ticket_ids"],
            serializer.validated_data["assigned_to"],
            self.business_area_slug,  # type: ignore
        )
        return Response(
            GrievanceTicketDetailSerializer(tickets, context={"request": request}, many=True).data,
            status=status.HTTP_202_ACCEPTED,
        )

    @transaction.atomic
    @extend_schema(
        request=BulkUpdateGrievanceTicketsPrioritySerializer,
        responses={202: GrievanceTicketDetailSerializer(many=True)},
    )
    @action(detail=False, methods=["post"], url_path="bulk-update-priority")
    def bulk_update_priority(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tickets = BulkActionService().bulk_set_priority(
            serializer.validated_data["grievance_ticket_ids"],
            serializer.validated_data["priority"],
            self.business_area_slug,  # type: ignore
        )
        return Response(
            GrievanceTicketDetailSerializer(tickets, context={"request": request}, many=True).data,
            status=status.HTTP_202_ACCEPTED,
        )

    @transaction.atomic
    @extend_schema(
        request=BulkUpdateGrievanceTicketsUrgencySerializer,
        responses={202: GrievanceTicketDetailSerializer(many=True)},
    )
    @action(detail=False, methods=["post"], url_path="bulk-update-urgency")
    def bulk_update_urgency(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tickets = BulkActionService().bulk_set_urgency(
            serializer.validated_data["grievance_ticket_ids"],
            serializer.validated_data["urgency"],
            self.business_area_slug,  # type: ignore
        )
        return Response(
            GrievanceTicketDetailSerializer(tickets, context={"request": request}, many=True).data,
            status=status.HTTP_202_ACCEPTED,
        )

    @transaction.atomic
    @extend_schema(
        request=BulkGrievanceTicketsAddNoteSerializer,
        responses={202: GrievanceTicketDetailSerializer(many=True)},
    )
    @action(detail=False, methods=["post"], url_path="bulk-add-note")
    def bulk_add_note(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tickets = BulkActionService().bulk_add_note(
            request.user,  # type: ignore
            serializer.validated_data["grievance_ticket_ids"],
            serializer.validated_data["note"],
            self.business_area_slug,  # type: ignore
        )
        return Response(
            GrievanceTicketDetailSerializer(tickets, context={"request": request}, many=True).data,
            status=status.HTTP_202_ACCEPTED,
        )

    @extend_schema(
        responses={200: FieldAttributeSerializer(many=True)},
    )
    @action(detail=False, methods=["get"], url_path="all-edit-household-fields-attributes")
    def all_edit_household_fields_attributes(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        fields = (
            FieldFactory.from_scope(Scope.HOUSEHOLD_UPDATE)
            .associated_with_household()
            .apply_business_area(self.business_area_slug)
        )
        all_options = list(fields) + list(
            FlexibleAttribute.objects.filter(
                associated_with=FlexibleAttribute.ASSOCIATED_WITH_HOUSEHOLD
            ).prefetch_related("choices")
        )
        sorted_list = sort_by_attr(all_options, "label.English(EN)")
        return Response(
            FieldAttributeSerializer(sorted_list, many=True).data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        responses={200: FieldAttributeSerializer(many=True)},
    )
    @action(detail=False, methods=["get"], url_path="all-edit-people-fields-attributes")
    def all_edit_people_fields_attributes(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        fields = FieldFactory.from_scope(Scope.PEOPLE_UPDATE).apply_business_area(self.business_area_slug)
        all_options = list(fields) + list(
            FlexibleAttribute.objects.filter(
                associated_with__in=[
                    FlexibleAttribute.ASSOCIATED_WITH_INDIVIDUAL,
                ]
            ).prefetch_related("choices")
        )
        sorted_list = sort_by_attr(all_options, "label.English(EN)")
        return Response(
            FieldAttributeSerializer(sorted_list, many=True).data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        responses={200: FieldAttributeSerializer(many=True)},
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="all-add-individuals-fields-attributes",
        pagination_class=None,
    )
    def all_add_individuals_fields_attributes(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        fields = (
            FieldFactory.from_scope(Scope.INDIVIDUAL_UPDATE)
            .associated_with_individual()
            .apply_business_area(self.business_area_slug)
        )
        all_options = list(fields) + list(
            FlexibleAttribute.objects.filter(associated_with=FlexibleAttribute.ASSOCIATED_WITH_INDIVIDUAL)
            .exclude(type=FlexibleAttribute.PDU)
            .prefetch_related("choices")
        )
        sorted_list = sort_by_attr(all_options, "label.English(EN)")
        return Response(
            FieldAttributeSerializer(sorted_list, many=True).data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(responses={200: GrievanceDashboardSerializer})
    @action(detail=False, methods=["get"], url_path="dashboard")
    def dashboard(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Get grievance dashboard data without program filtering (global view)."""
        base_queryset = self.get_dashboard_base_queryset()  # No program filtering
        dashboard_data = self.get_dashboard_data(base_queryset)
        return Response(dashboard_data, status=status.HTTP_200_OK)
