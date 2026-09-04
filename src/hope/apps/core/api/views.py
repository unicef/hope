from typing import Any

from django.db.models import Q, QuerySet
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.generics import get_object_or_404
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from hope.api.caches import cached_response, etag_decorator
from hope.apps.account.api.serializers import UserChoicesSerializer
from hope.apps.account.permissions import Permissions
from hope.apps.core.api.caches import BusinessAreaKeyConstructor
from hope.apps.core.api.filters import BusinessAreaFilter
from hope.apps.core.api.mixins import (
    BaseViewSet,
    BusinessAreaMixin,
    CountActionMixin,
    PermissionsMixin,
    SerializerActionMixin,
)
from hope.apps.core.api.serializers import (
    BusinessAreaSerializer,
    ChoiceSerializer,
    CollectorAttributeSerializer,
    CurrencyChoiceSerializer,
    DataCollectingTypeChoiceSerializer,
    FieldAttributeSerializer,
    GetKoboAssetListSerializer,
    KoboAssetObjectSerializer,
)
from hope.apps.core.field_attributes.fields_types import TYPE_STRING
from hope.apps.core.languages import Languages
from hope.apps.core.utils import (
    get_fields_attr_generators,
    resolve_assets_list,
    to_choice_object,
)
from hope.apps.grievance.api.serializers.grievance_ticket import (
    GrievanceChoicesSerializer,
)
from hope.apps.household.api.serializers.household import (
    HouseholdChoicesSerializer,
    IndividualChoicesSerializer,
)
from hope.apps.household.const import SEX_CHOICE
from hope.apps.payment.api.serializers import PaymentChoicesSerializer
from hope.apps.program.api.serializers import ProgramChoicesSerializer
from hope.models import (
    AccountType,
    BusinessArea,
    Country,
    DataCollectingType,
    DeliveryMechanism,
    DocumentType,
    Feedback,
    LogEntry,
    PaymentPlan,
    PaymentVerification,
    PaymentVerificationPlan,
    PaymentVerificationSummary,
    Program,
    RegistrationDataImport,
    RoleAssignment,
    Survey,
)


class BusinessAreaViewSet(
    CountActionMixin,
    RetrieveModelMixin,
    ListModelMixin,
    PermissionsMixin,
    BaseViewSet,
):
    permission_classes = [IsAuthenticated]
    serializer_class = BusinessAreaSerializer
    filter_backends = (OrderingFilter, DjangoFilterBackend)
    filterset_class = BusinessAreaFilter
    lookup_field = "slug"

    def get_queryset(self) -> QuerySet[BusinessArea]:
        user = self.request.user
        role_assignments = RoleAssignment.objects.filter(Q(user=user) | Q(partner__user=user)).exclude(
            expiry_date__lt=timezone.now()
        )
        return (
            BusinessArea.objects.filter(role_assignments__in=role_assignments)
            .order_by("id")
            .distinct()
            .prefetch_related("countries")
        )

    @etag_decorator(BusinessAreaKeyConstructor)
    @cached_response(key_func=BusinessAreaKeyConstructor())
    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().list(request, *args, **kwargs)

    @extend_schema(
        responses={
            200: CollectorAttributeSerializer(many=True),
        },
    )
    @action(detail=False, methods=["get"], url_path="all-collector-fields-attributes")
    def all_collector_fields_attributes(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        account_types = AccountType.objects.all()
        definitions = [
            {
                "id": f"{account_type.key}__{field}",
                "type": TYPE_STRING,
                "name": f"{account_type.key}__{field}",
                "lookup": f"{account_type.key}__{field}",
                "label": {"English(EN)": f"{account_type.key.title()} {field.title()}"},
                "hint": "",
                "required": False,
                "choices": [],
            }
            for account_type in account_types
            for field in account_type.unique_fields
        ]
        result_list = sorted(definitions, key=lambda attr: attr["label"]["English(EN)"])  # type: ignore
        return Response(CollectorAttributeSerializer(result_list, many=True).data, status=200)

    @extend_schema(parameters=[OpenApiParameter(name="program_id")])
    @extend_schema(
        responses={
            200: FieldAttributeSerializer(many=True),
        },
    )
    @action(detail=True, methods=["get"], url_path="all-fields-attributes", pagination_class=None)
    def all_fields_attributes(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        program_id = request.query_params.get("program_id", None)
        business_area_slug = self.kwargs["slug"]
        if program_id:
            # checked for scope only, the generator below takes the id
            get_object_or_404(Program, id=program_id, business_area__slug=business_area_slug)
        result_list = get_fields_attr_generators(business_area_slug=business_area_slug, program_id=program_id)
        return Response(FieldAttributeSerializer(result_list, many=True).data, status=200)

    @extend_schema(
        request=GetKoboAssetListSerializer,
        responses={
            200: KoboAssetObjectSerializer(many=True),
        },
    )
    @action(
        detail=True,
        methods=["post"],
        url_path="all-kobo-projects",
        pagination_class=None,
    )
    def all_kobo_projects(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Return all Kobo projects/assets."""
        assets_list = resolve_assets_list(
            business_area_slug=self.kwargs["slug"],
            only_deployed=request.data.get("only_deployed", False),
        )
        return Response(KoboAssetObjectSerializer(assets_list, many=True).data, status=200)


class DataCollectingTypeViewSet(BusinessAreaMixin, SerializerActionMixin, BaseViewSet):
    """Serve the data collecting types available in a business area."""

    queryset = DataCollectingType.objects.all()
    permissions_by_action = {
        "choices": [Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS],
    }
    serializer_classes_by_action = {
        "choices": DataCollectingTypeChoiceSerializer,
    }

    def get_queryset(self) -> QuerySet:
        return (
            DataCollectingType.objects.filter(
                Q(limit_to=self.business_area) | Q(limit_to__isnull=True),
                active=True,
                deprecated=False,
            )
            .exclude(code__iexact="unknown")
            .distinct()
            .order_by("label")
        )

    @extend_schema(responses={200: DataCollectingTypeChoiceSerializer(many=True)})
    @action(detail=False, methods=["get"], url_path="choices", url_name="choices", pagination_class=None)
    def choices(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Return the data collecting types a program in this business area can use."""
        return Response(self.get_serializer(self.get_queryset(), many=True).data)


class ChoicesViewSet(ViewSet):
    """Return business-area-independent choices used in the system."""

    # Two kinds of actions live here:
    # * flat - a single list, [{"name": ..., "value": ...}].
    # * bundles - an object grouping several related lists.

    enum_source = True

    # --- flat choices -------------------------------------------------------

    @extend_schema(responses={200: CurrencyChoiceSerializer(many=True)})
    @action(detail=False, methods=["get"], url_path="currencies")
    def currencies(self, request: Request) -> Response:
        from hope.models.currency import Currency

        currencies = Currency.objects.filter(active=True).order_by("code")
        return Response(CurrencyChoiceSerializer(currencies, many=True).data)

    @extend_schema(responses={200: ChoiceSerializer(many=True)})
    @action(detail=False, methods=["get"], url_path="payment-plan-status")
    def payment_plan_status(self, request: Request) -> Response:
        resp = ChoiceSerializer(to_choice_object(PaymentPlan.Status.choices), many=True).data
        return Response(resp)

    @extend_schema(responses={200: ChoiceSerializer(many=True)})
    @action(detail=False, methods=["get"], url_path="payment-plan-background-action-status")
    def payment_plan_background_action_status(self, request: Request) -> Response:
        resp = ChoiceSerializer(to_choice_object(PaymentPlan.BackgroundActionStatus.choices), many=True).data
        return Response(resp)

    @extend_schema(responses={200: ChoiceSerializer(many=True)})
    @action(detail=False, methods=["get"], url_path="payment-plan-type")
    def payment_plan_type(self, request: Request) -> Response:
        resp = ChoiceSerializer(to_choice_object(PaymentPlan.PlanType.choices), many=True).data
        return Response(resp)

    @extend_schema(responses={200: ChoiceSerializer(many=True)})
    @action(detail=False, methods=["get"], url_path="payment-verification-plan-status")
    def payment_verification_plan_status(self, request: Request) -> Response:
        resp = ChoiceSerializer(to_choice_object(PaymentVerificationPlan.STATUS_CHOICES), many=True).data
        return Response(resp)

    @extend_schema(responses={200: ChoiceSerializer(many=True)})
    @action(detail=False, methods=["get"], url_path="payment-verification-status")
    def payment_verification_status(self, request: Request) -> Response:
        resp = ChoiceSerializer(to_choice_object(PaymentVerification.STATUS_CHOICES), many=True).data
        return Response(resp)

    @extend_schema(responses={200: ChoiceSerializer(many=True)})
    @action(detail=False, methods=["get"], url_path="payment-verification-summary-status")
    def payment_verification_summary_status(self, request: Request) -> Response:
        resp = ChoiceSerializer(to_choice_object(PaymentVerificationSummary.STATUS_CHOICES), many=True).data
        return Response(resp)

    @extend_schema(responses={200: ChoiceSerializer(many=True)})
    @action(detail=False, methods=["get"], url_path="payment-verification-plan-sampling")
    def payment_verification_plan_sampling(self, request: Request) -> Response:
        resp = ChoiceSerializer(to_choice_object(PaymentVerificationPlan.SAMPLING_CHOICES), many=True).data
        return Response(resp)

    @extend_schema(responses={200: ChoiceSerializer(many=True)})
    @action(detail=False, methods=["get"], url_path="payment-verification-plan-channel")
    def payment_verification_plan_channel(self, request: Request) -> Response:
        resp = ChoiceSerializer(to_choice_object(PaymentVerificationPlan.VERIFICATION_CHANNEL_CHOICES), many=True).data
        return Response(resp)

    @extend_schema(responses={200: ChoiceSerializer(many=True)})
    @action(detail=False, methods=["get"], url_path="sex")
    def sex(self, request: Request) -> Response:
        resp = ChoiceSerializer(to_choice_object(SEX_CHOICE), many=True).data
        return Response(resp)

    @extend_schema(responses={200: ChoiceSerializer(many=True)})
    @action(detail=False, methods=["get"], url_path="payment-record-delivery-type")
    def payment_record_delivery_type(self, request: Request) -> Response:
        resp = ChoiceSerializer(to_choice_object(DeliveryMechanism.get_choices()), many=True).data
        return Response(resp)

    @extend_schema(responses={200: ChoiceSerializer(many=True)})
    @action(detail=False, methods=["get"], url_path="feedback-issue-type")
    def feedback_issue_type(self, request: Request) -> Response:
        resp = ChoiceSerializer(to_choice_object(Feedback.ISSUE_TYPE_CHOICES), many=True).data
        return Response(resp)

    @extend_schema(responses={200: ChoiceSerializer(many=True)})
    @action(detail=False, methods=["get"], url_path="languages")
    def languages(self, request: Request) -> Response:
        filter_code = request.query_params.get("code", "")
        filtered_languages_data = Languages.filter_by_code(filter_code)
        language_tuples = tuple((lang.code, lang.english) for lang in filtered_languages_data)
        resp = ChoiceSerializer(to_choice_object(list(language_tuples)), many=True).data
        return Response(resp)

    @extend_schema(responses={200: ChoiceSerializer(many=True)})
    @action(detail=False, methods=["get"], url_path="countries")
    def countries(self, request: Request) -> Response:
        countries = Country.objects.all().order_by("name")
        country_tuples = tuple((country.iso_code3, country.name) for country in countries)
        resp = ChoiceSerializer(to_choice_object(list(country_tuples)), many=True).data
        return Response(resp)

    @extend_schema(responses={200: ChoiceSerializer(many=True)})
    @action(detail=False, methods=["get"], url_path="permissions")
    def permissions(self, request: Request) -> Response:
        resp = ChoiceSerializer(to_choice_object(Permissions.choices()), many=True).data
        return Response(resp)

    @extend_schema(responses={200: ChoiceSerializer(many=True)})
    @action(detail=False, methods=["get"], url_path="activity-log-actions")
    def activity_log_actions(self, request: Request) -> Response:
        """Return the actions an activity log entry can record."""
        resp = ChoiceSerializer(to_choice_object(LogEntry.LOG_ENTRY_ACTION_CHOICES), many=True).data
        return Response(resp)

    @extend_schema(responses={200: ChoiceSerializer(many=True)})
    @action(detail=False, methods=["get"], url_path="registration-data-import-statuses")
    def registration_data_import_statuses(self, request: Request) -> Response:
        """Return the statuses a registration data import can be in."""
        resp = ChoiceSerializer(to_choice_object(RegistrationDataImport.STATUS_CHOICE), many=True).data
        return Response(resp)

    @extend_schema(responses={200: ChoiceSerializer(many=True)})
    @action(detail=False, methods=["get"], url_path="survey-categories")
    def survey_categories(self, request: Request) -> Response:
        """Return the categories a survey can belong to."""
        resp = ChoiceSerializer(to_choice_object(Survey.CATEGORY_CHOICES), many=True).data
        return Response(resp)

    @extend_schema(responses={200: ChoiceSerializer(many=True)})
    @action(detail=False, methods=["get"], url_path="document-types", enum_source=False)
    def document_types(self, request: Request) -> Response:
        """Return the document types a person can hold."""
        choices = [{"name": x.label, "value": x.key} for x in DocumentType.objects.order_by("key")]
        return Response(ChoiceSerializer(choices, many=True).data)

    # --- bundles ------------------------------------------------------------

    @extend_schema(responses={200: HouseholdChoicesSerializer})
    @action(detail=False, methods=["get"], url_path="households", enum_source=False)
    def households(self, request: Request) -> Response:
        """Return the choice lists used by the household screens."""
        return Response(HouseholdChoicesSerializer(instance={}, context={"request": request}).data)

    @extend_schema(responses={200: IndividualChoicesSerializer})
    @action(detail=False, methods=["get"], url_path="individuals", enum_source=False)
    def individuals(self, request: Request) -> Response:
        """Return the choice lists used by the individual screens."""
        return Response(IndividualChoicesSerializer(instance={}, context={"request": request}).data)

    @extend_schema(responses={200: GrievanceChoicesSerializer})
    @action(detail=False, methods=["get"], url_path="grievance-tickets", enum_source=False)
    def grievance_tickets(self, request: Request) -> Response:
        """Return the choice lists used by the grievance ticket screens."""
        return Response(GrievanceChoicesSerializer(instance={}, context={"request": request}).data)

    @extend_schema(responses={200: PaymentChoicesSerializer})
    @action(detail=False, methods=["get"], url_path="payments", enum_source=False)
    def payments(self, request: Request) -> Response:
        """Return the choice lists used by the payment screens."""
        return Response(PaymentChoicesSerializer(instance={}, context={"request": request}).data)

    @extend_schema(responses={200: ProgramChoicesSerializer})
    @action(detail=False, methods=["get"], url_path="programs", enum_source=False)
    def programs(self, request: Request) -> Response:
        """Return the choice lists used by the program screens."""
        return Response(ProgramChoicesSerializer(instance={}, context={"request": request}).data)

    @extend_schema(responses={200: UserChoicesSerializer})
    @action(detail=False, methods=["get"], url_path="users", enum_source=False)
    def users(self, request: Request) -> Response:
        """Return the choice lists used by the user screens."""
        return Response(UserChoicesSerializer(instance={}, context={"request": request}).data)
