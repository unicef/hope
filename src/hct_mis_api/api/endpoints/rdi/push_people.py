from typing import Any, Dict, List, Optional
from uuid import UUID

from django.db.transaction import atomic
from django.http import Http404
from django.utils import timezone
from django.utils.functional import cached_property

from django_countries import Countries
from drf_spectacular.utils import extend_schema
from rest_framework import serializers, status
from rest_framework.request import Request
from rest_framework.response import Response

from hct_mis_api.api.endpoints.base import HOPEAPIBusinessAreaView, HOPEAPIView
from hct_mis_api.api.endpoints.rdi.mixin import get_photo_from_stream
from hct_mis_api.api.endpoints.rdi.upload import BirthDateValidator, DocumentSerializer
from hct_mis_api.api.models import Grant
from hct_mis_api.apps.geo.models import Area, Country
from hct_mis_api.apps.household.models import (
    BLANK,
    COLLECT_TYPES,
    HEAD,
    NON_BENEFICIARY,
    RESIDENCE_STATUS_CHOICE,
    ROLE_PRIMARY,
    DocumentType,
    PendingDocument,
    PendingHousehold,
    PendingIndividual,
)
from hct_mis_api.apps.periodic_data_update.utils import populate_pdu_with_null_values
from hct_mis_api.apps.registration_data.models import RegistrationDataImport

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

    country_origin = serializers.ChoiceField(choices=Countries(), required=False)
    country = serializers.ChoiceField(choices=Countries())
    collect_individual_data = serializers.ChoiceField(choices=COLLECT_TYPES)
    residence_status = serializers.ChoiceField(choices=RESIDENCE_STATUS_CHOICE)
    village = serializers.CharField(allow_blank=True, allow_null=True, required=False)

    phone_no = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    phone_no_alternative = serializers.CharField(allow_null=True, allow_blank=True, required=False)

    admin1 = serializers.ChoiceField(allow_blank=True, allow_null=True, required=False, default="", choices=[])
    admin2 = serializers.ChoiceField(allow_blank=True, allow_null=True, required=False, default="", choices=[])
    admin3 = serializers.ChoiceField(allow_blank=True, allow_null=True, required=False, default="", choices=[])
    admin4 = serializers.ChoiceField(allow_blank=True, allow_null=True, required=False, default="", choices=[])

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.fields["admin1"].choices = Area.objects.filter(area_type__area_level=1).values_list("p_code", "name")
        self.fields["admin2"].choices = Area.objects.filter(area_type__area_level=2).values_list("p_code", "name")
        self.fields["admin3"].choices = Area.objects.filter(area_type__area_level=3).values_list("p_code", "name")
        self.fields["admin4"].choices = Area.objects.filter(area_type__area_level=4).values_list("p_code", "name")

    class Meta:
        model = PendingIndividual
        exclude = [
            "id",
            "registration_data_import",
            "business_area",
            "deduplication_batch_results",
            "deduplication_golden_record_results",
            "deduplication_batch_status",
            "created_at",
            "updated_at",
            "unicef_id",
            "household",
            "detail_id",
        ]


class PeopleUploadMixin:
    def save_people(self, rdi: RegistrationDataImport, people_data: List[Dict]) -> List[int]:
        people_ids = []
        for person_data in people_data:
            documents = person_data.pop("documents", [])

            hh = self._create_household(person_data, rdi)
            ind = self._create_individual(documents, hh, person_data, rdi)
            people_ids.append(ind.id)
        return people_ids

    def _create_household(self, person_data: Dict, rdi: RegistrationDataImport) -> Optional[PendingHousehold]:
        if person_data.get("type") == NON_BENEFICIARY:
            return None
        household_fields = [field.name for field in PendingHousehold._meta.get_fields()]
        household_data = {field: value for field, value in person_data.items() if field in household_fields}
        household_data["village"] = household_data.get("village") or ""
        admin_areas = [
            household_data.pop("admin4"),
            household_data.pop("admin3"),
            household_data.pop("admin2"),
            household_data.pop("admin1"),
        ]

        if country := household_data.pop("country"):
            household_data["country"] = Country.objects.get(iso_code2=country)

        if country_origin := household_data.pop("country_origin", None):
            household_data["country_origin"] = Country.objects.get(iso_code2=country_origin)

        household = PendingHousehold.objects.create(
            business_area=rdi.business_area,
            registration_data_import=rdi,
            program_id=rdi.program_id,
            collect_type=PendingHousehold.CollectType.SINGLE.value,
            **household_data,
        )
        the_lowest_p_code = next((admin_area for admin_area in admin_areas if admin_area), None)
        if the_lowest_p_code:
            admin_area_to_set = Area.objects.filter(p_code=the_lowest_p_code).first()
            household.set_admin_areas(admin_area_to_set)
        household.save()
        return household

    def _create_individual(
        self,
        documents: List[Dict],
        hh: Optional[PendingHousehold],
        person_data: Dict,
        rdi: RegistrationDataImport,
    ) -> PendingIndividual:
        individual_fields = [field.name for field in PendingIndividual._meta.get_fields()]
        individual_data = {field: value for field, value in person_data.items() if field in individual_fields}
        person_type = person_data.get("type")
        individual_data.pop("relationship", None)
        relationship = NON_BENEFICIARY if person_type is NON_BENEFICIARY else HEAD
        individual_data["phone_no"] = individual_data.get("phone_no") or ""
        individual_data["phone_no_alternative"] = individual_data.get("phone_no_alternative") or ""
        individual_data["flex_fields"] = populate_pdu_with_null_values(
            rdi.program, individual_data.get("flex_fields", None)
        )

        ind = PendingIndividual.objects.create(
            business_area=rdi.business_area,
            household=hh,
            registration_data_import=rdi,
            program_id=rdi.program_id,
            relationship=relationship,
            **individual_data,
        )
        ind.validate_phone_numbers()
        ind.save(update_fields=("phone_no_valid", "phone_no_alternative_valid"))

        if person_type is not NON_BENEFICIARY:
            hh.head_of_household = ind
            hh.individuals_and_roles.create(individual=ind, role=ROLE_PRIMARY)
            hh.save()

        for doc in documents:
            self._create_document(ind, doc)
        return ind

    def _create_document(self, member: PendingIndividual, doc: Dict) -> None:
        PendingDocument.objects.create(
            document_number=doc["document_number"],
            photo=get_photo_from_stream(doc.get("image", None)),
            individual=member,
            country=Country.objects.get(iso_code2=doc["country"]),
            type=DocumentType.objects.get(key=doc["type"]),
            program=member.program,
        )


class PushPeopleToRDIView(HOPEAPIBusinessAreaView, PeopleUploadMixin, HOPEAPIView):
    permission = Grant.API_RDI_UPLOAD

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

    @extend_schema(request=PushPeopleSerializer)
    @atomic()
    def post(self, request: "Request", business_area: str, rdi: UUID) -> Response:
        serializer = PushPeopleSerializer(data=request.data, many=True)
        if serializer.is_valid():
            people_ids = self.save_people(self.selected_rdi, serializer.validated_data)

            response = {
                "id": self.selected_rdi.id,
                "people": people_ids,
            }
            return Response(response, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
