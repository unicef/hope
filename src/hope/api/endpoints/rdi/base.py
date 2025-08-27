from dataclasses import asdict
from typing import Any

from django.contrib.auth import get_user_model
from django.db.models import QuerySet
from django.db.transaction import atomic
from django.http import HttpRequest
from django.http.response import Http404, HttpResponseBase
from django.utils.functional import cached_property
from rest_framework import serializers, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import CreateAPIView, UpdateAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from hope.api.endpoints.base import HOPEAPIBusinessAreaView, HOPEAPIView
from hope.api.endpoints.rdi.mixin import HouseholdUploadMixin
from hope.api.endpoints.rdi.upload import HouseholdSerializer
from hope.models.grant import Grant
from hope.api.utils import humanize_errors
from hope.models.country import Country
from hope.models.household import PendingHousehold
from hope.models.program import Program
from hope.models.registration_data_import import RegistrationDataImport


class RDISerializer(serializers.ModelSerializer):
    program = serializers.SlugRelatedField(
        slug_field="id", required=True, queryset=Program.objects.all(), write_only=True
    )
    imported_by_email = serializers.EmailField(required=True, write_only=True)

    class Meta:
        model = RegistrationDataImport
        fields = ("name", "program", "imported_by_email")

    def create(self, validated_data: dict) -> None:
        validated_data.pop("imported_by_email", None)
        return super().create(validated_data)


class CreateRDIView(HOPEAPIBusinessAreaView, CreateAPIView):
    """Api to Create RDI for selected business area."""

    permission = Grant.API_RDI_CREATE
    serializer_class = RDISerializer

    def get_queryset(self) -> QuerySet[RegistrationDataImport]:
        return RegistrationDataImport.objects.filter(business_area=self.selected_business_area)

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponseBase:
        return super().dispatch(request, *args, **kwargs)

    @atomic()
    def perform_create(self, serializer: serializers.BaseSerializer) -> None:
        imported_by_email = serializer.validated_data.get("imported_by_email")
        User = get_user_model()  # noqa
        try:
            imported_by = User.objects.get(email=imported_by_email)
        except User.DoesNotExist:
            raise PermissionDenied("User with this email does not exist.")
        self.rdi = serializer.save(
            business_area=self.selected_business_area,
            status=RegistrationDataImport.LOADING,
            imported_by=imported_by,
            data_source=RegistrationDataImport.API,
            number_of_individuals=0,
            number_of_households=0,
        )

    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            {"id": serializer.instance.pk, "name": self.rdi.name},
            status=status.HTTP_201_CREATED,
            headers=headers,
        )


class PushToRDIView(HOPEAPIBusinessAreaView, HouseholdUploadMixin, HOPEAPIView):
    """Api to link Households with selected RDI."""

    permission = Grant.API_RDI_CREATE

    @cached_property
    def selected_rdi(self) -> RegistrationDataImport:
        try:
            return RegistrationDataImport.objects.get(
                status=RegistrationDataImport.LOADING,
                id=self.kwargs["rdi"],
                business_area__slug=self.kwargs["business_area"],
            )
        except RegistrationDataImport.DoesNotExist:
            raise Http404

    @atomic()
    def post(
        self,
        request: Request,
        business_area: "BusinessArea",
        rdi: RegistrationDataImport,
    ) -> Response:
        serializer = HouseholdSerializer(data=request.data, many=True)

        if serializer.is_valid():
            totals = self.save_households(self.selected_rdi, serializer.validated_data)
            return Response(
                {"id": self.selected_rdi.id, **asdict(totals)},
                status=status.HTTP_201_CREATED,
            )
        return Response(humanize_errors(serializer.errors), status=status.HTTP_400_BAD_REQUEST)


class PushLaxToRDIView(HOPEAPIBusinessAreaView, HouseholdUploadMixin, HOPEAPIView):
    """Api to link Households with selected RDI."""

    permission = Grant.API_RDI_CREATE

    @cached_property
    def selected_rdi(self) -> RegistrationDataImport:
        try:
            return RegistrationDataImport.objects.get(
                status=RegistrationDataImport.LOADING,
                id=self.kwargs["rdi"],
                business_area__slug=self.kwargs["business_area"],
            )
        except RegistrationDataImport.DoesNotExist:
            raise Http404

    def post(
        self,
        request: Request,
        business_area: "BusinessArea",
        rdi: RegistrationDataImport,
    ) -> Response:
        # The initial serializer
        total_households = 0
        total_errors = 0
        total_accepted = 0
        errs = []

        program_id = self.selected_rdi.program.id

        for household_data in request.data:
            total_households += 1
            serializer: HouseholdSerializer = HouseholdSerializer(data=household_data)
            if serializer.is_valid():
                members: list[dict] = serializer.validated_data.pop("members", [])

                if country := serializer.validated_data.get("country"):
                    serializer.validated_data["country"] = Country.objects.get(iso_code2=country)
                if country_origin := serializer.validated_data.get("country_origin"):
                    serializer.validated_data["country_origin"] = Country.objects.get(iso_code2=country_origin)

                hh = PendingHousehold.objects.create(
                    registration_data_import=self.selected_rdi,
                    program_id=program_id,
                    business_area=self.selected_business_area,
                    **serializer.validated_data,
                )

                for member_data in members:
                    self.save_member(self.selected_rdi, hh, member_data)
                errs.append({"pk": hh.pk})
                total_accepted += 1
            else:
                errs.append(serializer.errors)
                total_errors += 1

        results = humanize_errors({"households": errs})
        return Response(
            {
                "id": self.selected_rdi.id,
                "processed": total_households,
                "accepted": total_accepted,
                "errors": total_errors,
                **results,
            },
            status=status.HTTP_201_CREATED,
        )


class CompleteRDIView(HOPEAPIBusinessAreaView, UpdateAPIView):
    """Api to Create RDI for selected business area."""

    permission = Grant.API_RDI_CREATE
    serializer_class = RDISerializer

    @cached_property
    def selected_rdi(self) -> RegistrationDataImport:
        try:
            return RegistrationDataImport.objects.get(
                status=RegistrationDataImport.LOADING,
                id=self.kwargs["rdi"],
                business_area__slug=self.kwargs["business_area"],
            )
        except RegistrationDataImport.DoesNotExist:
            raise Http404

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return self.update(request, *args, **kwargs)

    @atomic()
    def update(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        self.selected_rdi.status = RegistrationDataImport.IN_REVIEW
        self.selected_rdi.save()

        return Response(
            [
                {"id": self.selected_rdi.pk, "status": self.selected_rdi.status},
            ]
        )
