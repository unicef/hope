from typing import Any

from django.db.models import Q, QuerySet
from django.utils import timezone

from constance import config
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rest_framework_extensions.cache.decorators import cache_response

from hope.api.caches import etag_decorator
from hope.apps.account.models import RoleAssignment
from hope.apps.accountability.models import Feedback
from hope.apps.core.api.caches import BusinessAreaKeyConstructor
from hope.apps.core.api.filters import BusinessAreaFilter
from hope.apps.core.api.mixins import BaseViewSet, CountActionMixin
from hope.apps.core.api.serializers import (
    BusinessAreaSerializer,
    ChoiceSerializer,
    CollectorAttributeSerializer,
    FieldAttributeSerializer,
    GetKoboAssetListSerializer,
    KoboAssetObjectSerializer,
)
from hope.apps.core.currencies import CURRENCY_CHOICES
from hope.apps.core.field_attributes.fields_types import TYPE_STRING
from hope.apps.core.languages import Languages
from hope.apps.core.models import BusinessArea
from hope.apps.core.utils import (
    get_fields_attr_generators,
    resolve_assets_list,
    to_choice_object,
)
from hope.apps.geo.models import Country
from hope.apps.payment.models import (
    AccountType,
    DeliveryMechanism,
    PaymentPlan,
    PaymentVerificationPlan,
    PaymentVerificationSummary,
)


class BusinessAreaViewSet(
    CountActionMixin,
    RetrieveModelMixin,
    ListModelMixin,
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
        return BusinessArea.objects.filter(role_assignments__in=role_assignments).order_by("id").distinct()

    @etag_decorator(BusinessAreaKeyConstructor)
    @cache_response(timeout=config.REST_API_TTL, key_func=BusinessAreaKeyConstructor())
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
    @action(detail=True, methods=["get"], url_path="all-fields-attributes")
    def all_fields_attributes(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        program_id = request.query_params.get("program_id", None)
        business_area_slug = self.kwargs["slug"]
        result_list = get_fields_attr_generators(business_area_slug=business_area_slug, program_id=program_id)
        return Response(FieldAttributeSerializer(result_list, many=True).data, status=200)

    @extend_schema(
        request=GetKoboAssetListSerializer,
        responses={
            200: KoboAssetObjectSerializer(many=True),
        },
    )
    @action(detail=True, methods=["post"], url_path="all-kobo-projects", pagination_class=None)
    def all_kobo_projects(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """
        All Kobo projects/assets.
        """
        assets_list = resolve_assets_list(
            business_area_slug=self.kwargs["slug"], only_deployed=request.data.get("only_deployed", False)
        )
        return Response(KoboAssetObjectSerializer(assets_list, many=True).data, status=200)


class ChoicesViewSet(ViewSet):
    """
    return choices used in the system like statuses, currencies
        Response([{"value": k, "name": v} for k, v in PaymentPlan.Status.choices])
    """

    @extend_schema(responses={200: ChoiceSerializer(many=True)})
    @action(detail=False, methods=["get"], url_path="currencies")
    def currencies(self, request: Request) -> Response:
        resp = ChoiceSerializer(to_choice_object([c for c in CURRENCY_CHOICES if c[0] != ""]), many=True).data
        return Response(resp)

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
    @action(detail=False, methods=["get"], url_path="payment-verification-plan-status")
    def payment_verification_plan_status(self, request: Request) -> Response:
        resp = ChoiceSerializer(to_choice_object(PaymentVerificationPlan.STATUS_CHOICES), many=True).data
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
        country_tuples = tuple((country.name, country.iso_code3) for country in countries)
        resp = ChoiceSerializer(to_choice_object(list(country_tuples)), many=True).data
        return Response(resp)
