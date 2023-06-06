from dataclasses import asdict
from typing import TYPE_CHECKING, Any, Dict, Optional

from django.db.models import QuerySet
from django.db.transaction import atomic
from django.http import HttpRequest
from django.http.response import HttpResponseBase
from django.utils.functional import cached_property

from rest_framework import serializers, status
from rest_framework.generics import CreateAPIView, UpdateAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from hct_mis_api.api.endpoints.base import HOPEAPIBusinessAreaView, HOPEAPIView
from hct_mis_api.api.endpoints.mixin import HouseholdUploadMixin
from hct_mis_api.api.endpoints.upload import HouseholdSerializer
from hct_mis_api.api.models import Grant
from hct_mis_api.api.utils import humanize_errors
from hct_mis_api.apps.registration_data.models import RegistrationDataImport
from hct_mis_api.apps.registration_datahub.models import (
    ImportedHousehold,
    RegistrationDataImportDatahub,
)

if TYPE_CHECKING:
    from hct_mis_api.apps.core.models import BusinessArea


class RDISerializer(serializers.ModelSerializer):
    class Meta:
        model = RegistrationDataImportDatahub
        exclude = ("business_area_slug", "import_data", "hct_id")

    def create(self, validated_data: Dict) -> None:
        return super().create(validated_data)


class CreateRDIView(HOPEAPIBusinessAreaView, CreateAPIView):
    """Api to Create RDI for selected business area"""

    permission = Grant.API_RDI_CREATE
    serializer_class = RDISerializer

    def get_queryset(self) -> QuerySet:
        return RegistrationDataImportDatahub.objects.filter(business_area=self.selected_business_area)

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponseBase:
        return super().dispatch(request, *args, **kwargs)

    @atomic()
    @atomic(using="registration_datahub")
    def perform_create(self, serializer: serializers.BaseSerializer) -> Optional[RegistrationDataImport]:  # type: ignore # FIXME: perform_create from CreateModelMixin returns None
        obj = serializer.save(
            business_area_slug=self.selected_business_area.slug, import_done=RegistrationDataImportDatahub.LOADING
        )
        return RegistrationDataImport.objects.create(
            **serializer.validated_data,
            imported_by=self.request.user,
            data_source=RegistrationDataImport.API,
            number_of_individuals=0,
            number_of_households=0,
            datahub_id=str(obj.pk),
            business_area=self.selected_business_area,
        )

    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        r2 = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            {"id": serializer.instance.pk, "name": r2.name, "public_id": r2.pk},
            status=status.HTTP_201_CREATED,
            headers=headers,
        )


class PushToRDIView(HOPEAPIBusinessAreaView, HouseholdUploadMixin, HOPEAPIView):
    """Api to link Households with selected RDI"""

    permission = Grant.API_RDI_CREATE

    @cached_property
    def selected_rdi(self) -> RegistrationDataImportDatahub:
        return RegistrationDataImportDatahub.objects.get(
            id=self.kwargs["rdi"], business_area_slug=self.kwargs["business_area"]
        )

    @atomic(using="registration_datahub")
    def post(self, request: Request, business_area: "BusinessArea", rdi: RegistrationDataImport) -> Response:
        serializer = HouseholdSerializer(data=request.data, many=True)

        if serializer.is_valid():
            totals = self.save_households(self.selected_rdi, serializer.validated_data)
            return Response({"id": self.selected_rdi.id, **asdict(totals)}, status=status.HTTP_201_CREATED)
        return Response(humanize_errors(serializer.errors), status=status.HTTP_400_BAD_REQUEST)


class PushLaxToRDIView(HOPEAPIBusinessAreaView, HouseholdUploadMixin, HOPEAPIView):
    """Api to link Households with selected RDI"""

    permission = Grant.API_RDI_CREATE

    @cached_property
    def selected_rdi(self) -> QuerySet[RegistrationDataImport]:
        return RegistrationDataImportDatahub.objects.get(
            id=self.kwargs["rdi"], business_area_slug=self.kwargs["business_area"]
        )

    def post(self, request: Request, business_area: "BusinessArea", rdi: RegistrationDataImport) -> Response:
        # The initial serializer
        total_households = 0
        total_errors = 0
        total_accepted = 0
        out = []
        for household_data in request.data:
            total_households += 1
            serializer = HouseholdSerializer(data=household_data)
            if serializer.is_valid():
                ImportedHousehold.objects.create(registration_data_import=self.selected_rdi, **serializer.data)
                out.append({"status": "success"})
                total_accepted += 1
            else:
                out.append(serializer.errors)
                total_errors += 1
        results = humanize_errors({"households": out})
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
    """Api to Create RDI for selected business area"""

    permission = Grant.API_RDI_CREATE
    serializer_class = RDISerializer

    @cached_property
    def selected_rdi(self) -> QuerySet[RegistrationDataImport]:
        return RegistrationDataImportDatahub.objects.get(
            id=self.kwargs["rdi"], business_area_slug=self.kwargs["business_area"]
        )

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return self.update(request, *args, **kwargs)

    @atomic()
    @atomic(using="registration_datahub")
    def update(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        self.selected_rdi.import_done = RegistrationDataImportDatahub.DONE
        self.selected_rdi.save()

        sibling = self.selected_rdi.linked_rdi
        sibling.status = RegistrationDataImport.IN_REVIEW
        sibling.save()

        return Response(
            [
                {"id": self.selected_rdi.pk, "status": self.selected_rdi.import_done},
                {"id": self.selected_rdi.linked_rdi.pk, "status": self.selected_rdi.linked_rdi.status},
            ]
        )
