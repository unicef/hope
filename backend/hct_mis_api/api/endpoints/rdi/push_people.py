from typing import Dict, List, Optional
from uuid import UUID

from django.db.transaction import atomic
from django.http import Http404
from django.utils import timezone
from django.utils.functional import cached_property

from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers, status
from rest_framework.request import Request
from rest_framework.response import Response

from hct_mis_api.api.endpoints.base import HOPEAPIBusinessAreaView, HOPEAPIView
from hct_mis_api.api.endpoints.rdi.mixin import get_photo_from_stream
from hct_mis_api.api.endpoints.rdi.upload import BirthDateValidator, DocumentSerializer
from hct_mis_api.api.models import Grant
from hct_mis_api.apps.household.models import (
    BLANK,
    COLLECT_TYPES,
    HEAD,
    NON_BENEFICIARY,
    RESIDENCE_STATUS_CHOICE,
    ROLE_PRIMARY,
)
from hct_mis_api.apps.registration_data.models import RegistrationDataImport
from hct_mis_api.apps.registration_datahub.models import (
    ImportedDocument,
    ImportedDocumentType,
    ImportedHousehold,
    ImportedIndividual,
    RegistrationDataImportDatahub,
)

PEOPLE_TYPE_CHOICES = (
    (BLANK, "None"),
    (NON_BENEFICIARY, "Non Beneficiary"),
)


class PushPeopleSerializer(serializers.ModelSerializer):
    first_registration_date = serializers.DateTimeField(default=timezone.now)
    last_registration_date = serializers.DateTimeField(default=timezone.now)
    observed_disability = serializers.CharField(allow_blank=True, required=False)
    marital_status = serializers.CharField(allow_blank=True, required=False)
    documents = DocumentSerializer(many=True, required=False)
    birth_date = serializers.DateField(validators=[BirthDateValidator()])

    type = serializers.ChoiceField(choices=PEOPLE_TYPE_CHOICES, required=True)

    country_origin = serializers.CharField(allow_blank=True, required=False)
    country = serializers.CharField(allow_blank=True, required=True)
    collect_individual_data = serializers.ChoiceField(choices=COLLECT_TYPES)
    residence_status = serializers.ChoiceField(choices=RESIDENCE_STATUS_CHOICE)
    village = serializers.CharField(allow_blank=True, required=False)

    class Meta:
        model = ImportedIndividual
        exclude = [
            "id",
            "registration_data_import",
            "deduplication_batch_results",
            "deduplication_golden_record_results",
            "deduplication_batch_status",
            "created_at",
            "updated_at",
            "mis_unicef_id",
            "household",
            "kobo_asset_id",
            "row_id",
            "detail_id",
        ]


class PeopleUploadMixin:
    def save_people(self, rdi: RegistrationDataImportDatahub, program_id: UUID, people_data: List[Dict]) -> List[int]:
        people_ids = []
        for person_data in people_data:
            documents = person_data.pop("documents", [])

            hh = self._create_household(person_data, program_id, rdi)
            ind = self._create_individual(documents, hh, person_data, program_id, rdi)
            people_ids.append(ind.id)
        return people_ids

    def _create_household(
        self, person_data: Dict, program_id: UUID, rdi: RegistrationDataImportDatahub
    ) -> Optional[ImportedHousehold]:
        if person_data.get("type") == NON_BENEFICIARY:
            return None
        household_fields = [field.name for field in ImportedHousehold._meta.get_fields()]
        household_data = {field: value for field, value in person_data.items() if field in household_fields}
        return ImportedHousehold.objects.create(
            registration_data_import=rdi,
            program_id=program_id,
            collect_type=ImportedHousehold.CollectType.SINGLE.value,
            **household_data,
        )

    def _create_individual(
        self,
        documents: List[Dict],
        hh: Optional[ImportedHousehold],
        person_data: Dict,
        program_id: UUID,
        rdi: RegistrationDataImportDatahub,
    ) -> ImportedIndividual:
        individual_fields = [field.name for field in ImportedIndividual._meta.get_fields()]
        individual_data = {field: value for field, value in person_data.items() if field in individual_fields}
        person_type = person_data.get("type")
        relationship = NON_BENEFICIARY if person_type is NON_BENEFICIARY else HEAD

        ind = ImportedIndividual.objects.create(
            household=hh,
            registration_data_import=rdi,
            program_id=program_id,
            relationship=relationship,
            **individual_data,
        )

        if person_type is not NON_BENEFICIARY:
            hh.head_of_household = ind
            hh.individuals_and_roles.create(individual=ind, role=ROLE_PRIMARY)
            hh.save()

        for doc in documents:
            self._create_document(ind, doc)
        return ind

    def _create_document(self, member: ImportedIndividual, doc: Dict) -> None:
        ImportedDocument.objects.create(
            document_number=doc["document_number"],
            photo=get_photo_from_stream(doc.get("image", None)),
            doc_date=doc["doc_date"],
            individual=member,
            country=doc["country"],
            type=ImportedDocumentType.objects.get(key=doc["type"]),
        )


class PushPeopleToRDIView(HOPEAPIBusinessAreaView, PeopleUploadMixin, HOPEAPIView):
    permission = Grant.API_RDI_UPLOAD

    @cached_property
    def selected_rdi(self) -> RegistrationDataImportDatahub:
        try:
            return RegistrationDataImportDatahub.objects.get(
                import_done=RegistrationDataImportDatahub.LOADING,
                id=self.kwargs["rdi"],
                business_area_slug=self.kwargs["business_area"],
            )
        except RegistrationDataImportDatahub.DoesNotExist:
            raise Http404

    @swagger_auto_schema(request_body=PushPeopleSerializer)
    @atomic(using="registration_datahub")
    def post(self, request: "Request", business_area: str, rdi: UUID) -> Response:
        serializer = PushPeopleSerializer(data=request.data, many=True)
        program_id = RegistrationDataImport.objects.get(datahub_id=str(self.selected_rdi.id)).program_id

        if serializer.is_valid():
            people_ids = self.save_people(self.selected_rdi, program_id, serializer.validated_data)

            response = {
                "id": self.selected_rdi.id,
                "people": people_ids,
            }
            return Response(response, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
