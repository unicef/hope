from typing import Any, Dict, List
from uuid import UUID

from django.db.transaction import atomic
from django.utils import timezone

from drf_spectacular.utils import extend_schema
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request
from rest_framework.response import Response

from hct_mis_api.api.endpoints.base import HOPEAPIBusinessAreaView
from hct_mis_api.api.endpoints.rdi.mixin import get_photo_from_stream
from hct_mis_api.api.endpoints.rdi.upload import BirthDateValidator, DocumentSerializer
from hct_mis_api.api.models import Grant
from hct_mis_api.api.utils import humanize_errors
from hct_mis_api.apps.core.models import BusinessArea, DataCollectingType
from hct_mis_api.apps.household.models import (
    COLLECT_TYPES,
    RESIDENCE_STATUS_CHOICE,
    ROLE_PRIMARY,
)
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.registration_data.models import (
    ImportedDocument,
    ImportedDocumentType,
    ImportedHousehold,
    ImportedIndividual,
    RegistrationDataImport,
    RegistrationDataImportDatahub,
)


class PeopleSerializer(serializers.ModelSerializer):
    first_registration_date = serializers.DateTimeField(default=timezone.now)
    last_registration_date = serializers.DateTimeField(default=timezone.now)
    observed_disability = serializers.CharField(allow_blank=True, required=False)
    marital_status = serializers.CharField(allow_blank=True, required=False)
    documents = DocumentSerializer(many=True, required=False)
    birth_date = serializers.DateField(validators=[BirthDateValidator()])

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
        ]
        ref_name = "PeopleUploadSerializer"


class PeopleUploadMixin:
    def save_document(self, member: ImportedIndividual, doc: Dict) -> None:
        ImportedDocument.objects.create(
            document_number=doc["document_number"],
            photo=get_photo_from_stream(doc.get("image", None)),
            doc_date=doc["doc_date"],
            individual=member,
            country=doc["country"],
            type=ImportedDocumentType.objects.get(key=doc["type"]),
        )

    def save_people(self, rdi: RegistrationDataImportDatahub, program_id: UUID, people_data: List[Dict]) -> int:
        counter = 0
        for person_data in people_data:
            counter += 1
            documents = person_data.pop("documents", [])

            household_fields = [field.name for field in ImportedHousehold._meta.get_fields()]
            household_data = {field: value for field, value in person_data.items() if field in household_fields}
            hh = ImportedHousehold.objects.create(
                registration_data_import=rdi,
                program_id=program_id,
                collect_type=ImportedHousehold.CollectType.SINGLE.value,
                **household_data,
            )

            individual_fields = [field.name for field in ImportedIndividual._meta.get_fields()]
            individual_data = {field: value for field, value in person_data.items() if field in individual_fields}

            ind = ImportedIndividual.objects.create(
                household=hh,
                registration_data_import=rdi,
                program_id=program_id,
                **individual_data,
            )
            hh.head_of_household = ind
            hh.individuals_and_roles.create(individual=ind, role=ROLE_PRIMARY)
            hh.save()
            for doc in documents:
                self.save_document(ind, doc)
        return counter


class RDIPeopleSerializer(PeopleUploadMixin, serializers.ModelSerializer):
    name = serializers.CharField(required=True)
    people = PeopleSerializer(many=True, required=True)
    program = serializers.SlugRelatedField(
        slug_field="id", required=True, queryset=Program.objects.all(), write_only=True
    )

    class Meta:
        model = RegistrationDataImportDatahub
        exclude = ("business_area_slug", "import_data", "hct_id")

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.business_area = kwargs.pop("business_area", None)
        super().__init__(*args, **kwargs)

    def validate_people(self, value: Any) -> Any:
        if not value:
            raise ValidationError("This field is required.")
        return value

    def validate_program(self, program: Program) -> Program:
        if program.data_collecting_type.type != DataCollectingType.Type.SOCIAL:
            raise ValidationError("Program should be a social type")
        return program

    @atomic()
    @atomic(using="registration_datahub")
    def create(self, validated_data: Dict) -> Dict:
        created_by = validated_data.pop("user")
        people = validated_data.pop("people")
        program = validated_data.pop("program")

        rdi_datahub = RegistrationDataImportDatahub.objects.create(
            **validated_data, business_area_slug=self.business_area.slug
        )
        validated_data.pop("import_done", None)
        rdi_mis = RegistrationDataImport.objects.create(
            **validated_data,
            imported_by=created_by,
            data_source=RegistrationDataImport.API,
            number_of_individuals=1,
            number_of_households=1,
            datahub_id=str(rdi_datahub.pk),
            business_area=self.business_area,
            program=program,
        )
        rdi_datahub.hct_id = rdi_mis.id
        rdi_datahub.save()
        number_of_people = self.save_people(rdi_datahub, program.id, people)

        return dict(id=rdi_datahub.pk, name=rdi_mis.name, public_id=rdi_mis.pk, people=number_of_people)


class UploadPeopleRDIView(HOPEAPIBusinessAreaView):
    permission = Grant.API_RDI_UPLOAD

    @extend_schema(request=RDIPeopleSerializer)
    @atomic()
    @atomic(using="registration_datahub")
    def post(self, request: "Request", business_area: "BusinessArea") -> Response:
        serializer = RDIPeopleSerializer(data=request.data, business_area=self.selected_business_area)
        if serializer.is_valid():
            info = serializer.save(user=request.user)
            return Response(info, status=status.HTTP_201_CREATED)
        errors = humanize_errors(serializer.errors)
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)
