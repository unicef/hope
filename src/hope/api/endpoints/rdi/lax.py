from dataclasses import dataclass, field
from functools import cached_property
from typing import TYPE_CHECKING
from uuid import UUID

from django.core.files import File
from django.db.transaction import atomic
from django.http import Http404
from django.utils import timezone

from django_countries import Countries
from drf_spectacular.utils import extend_schema
from rest_framework import serializers, status
from rest_framework.request import Request
from rest_framework.response import Response

from hct_mis_api.api.endpoints.base import HOPEAPIBusinessAreaView
from hct_mis_api.api.endpoints.rdi.mixin import PhotoMixin
from hct_mis_api.api.endpoints.rdi.upload import BirthDateValidator
from hct_mis_api.api.models import Grant
from hct_mis_api.apps.core.utils import IDENTIFICATION_TYPE_TO_KEY_MAPPING
from hct_mis_api.apps.geo.models import Area, Country
from hct_mis_api.apps.household.models import (
    DATA_SHARING_CHOICES,
    IDENTIFICATION_TYPE_CHOICE,
    ROLE_ALTERNATE,
    ROLE_PRIMARY,
    DocumentType,
    IndividualRoleInHousehold,
    PendingDocument,
    PendingHousehold,
    PendingIndividual,
)
from hct_mis_api.apps.payment.models import (
    AccountType,
    FinancialInstitution,
    PendingAccount,
)
from hct_mis_api.apps.periodic_data_update.utils import populate_pdu_with_null_values
from hct_mis_api.apps.registration_data.models import RegistrationDataImport
from hct_mis_api.apps.utils.phone import calculate_phone_numbers_validity
import contextlib

if TYPE_CHECKING:
    from hct_mis_api.apps.core.models import BusinessArea


BATCH_SIZE = 100


@dataclass
class IndividualsBulkStaging:
    valid_individuals: list[PendingIndividual] = field(default_factory=list)
    individual_external_ids_by_pk: dict[str, str] = field(default_factory=dict)
    prepared_documents: list[dict] = field(default_factory=list)
    prepared_accounts: list[dict] = field(default_factory=list)
    doc_country_codes: set[str] = field(default_factory=set)
    doc_type_keys: set[str] = field(default_factory=set)
    saved_file_fields: list = field(default_factory=list)


class DocumentSerializer(serializers.ModelSerializer):
    type = serializers.ChoiceField(
        choices=[(IDENTIFICATION_TYPE_TO_KEY_MAPPING[value], label) for (value, label) in IDENTIFICATION_TYPE_CHOICE],
        required=True,
    )
    country = serializers.ChoiceField(choices=Countries())
    image = serializers.CharField(allow_blank=True, required=False)
    document_number = serializers.CharField(required=True)
    issuance_date = serializers.DateField(required=False)
    expiry_date = serializers.DateField(required=False)

    class Meta:
        model = PendingDocument
        fields = ["type", "country", "image", "document_number", "issuance_date", "expiry_date"]


class AccountSerializer(serializers.ModelSerializer):
    account_type = serializers.SlugRelatedField(slug_field="key", required=True, queryset=AccountType.objects.all())
    number = serializers.CharField(allow_blank=True, required=False)
    financial_institution = serializers.PrimaryKeyRelatedField(
        required=False, queryset=FinancialInstitution.objects.all()
    )
    data = serializers.JSONField(required=False, default=dict)  # type: ignore

    class Meta:
        model = PendingAccount
        fields = ["account_type", "number", "financial_institution", "data"]


class IndividualSerializer(serializers.ModelSerializer):
    first_registration_date = serializers.DateTimeField(default=timezone.now)
    last_registration_date = serializers.DateTimeField(default=timezone.now)
    household = serializers.ReadOnlyField()
    observed_disability = serializers.CharField(allow_blank=True, required=False)
    marital_status = serializers.CharField(allow_blank=True, required=False)
    documents = DocumentSerializer(many=True, required=False)
    birth_date = serializers.DateField(validators=[BirthDateValidator()])
    accounts = AccountSerializer(many=True, required=False)
    photo = serializers.CharField(allow_blank=True, required=False)
    individual_id = serializers.CharField(required=True)

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
            "version",
            "vector_column",
            "unicef_id",
            "program",
            "rdi_merge_status",
            "is_removed",
        ]


class CreateLaxBaseView(HOPEAPIBusinessAreaView):
    permission = Grant.API_RDI_CREATE

    @cached_property
    def selected_rdi(self) -> RegistrationDataImport:
        """Get the selected RDI with proper error handling."""
        try:
            return RegistrationDataImport.objects.get(
                status=RegistrationDataImport.LOADING,
                id=self.kwargs["rdi"],
                business_area__slug=self.kwargs["business_area"],
            )
        except RegistrationDataImport.DoesNotExist:
            raise Http404("Registration Data Import not found or not in LOADING status")


class CreateLaxIndividuals(CreateLaxBaseView, PhotoMixin):
    """API to import individuals with selected RDI."""

    def _prepare_documents(
        self,
        documents_data: list[dict],
        ind: PendingIndividual,
    ) -> None:
        for document_data in documents_data:
            image_b64 = document_data.pop("image", None)
            doc_photo = self.get_photo(image_b64)
            country_code = document_data.get("country")
            type_key = document_data.get("type")
            if country_code:
                self.staging.doc_country_codes.add(country_code)
            if type_key:
                self.staging.doc_type_keys.add(type_key)
            self.staging.prepared_documents.append(
                {
                    "individual": ind,
                    "photo_file": doc_photo,
                    "country_code": country_code,
                    "type_key": type_key,
                    "document_number": document_data.get("document_number"),
                    "issuance_date": document_data.get("issuance_date"),
                    "expiry_date": document_data.get("expiry_date"),
                }
            )

    def _prepare_accounts(
        self,
        accounts_data: list[dict],
        ind: PendingIndividual,
    ) -> None:
        for account_data in accounts_data:
            self.staging.prepared_accounts.append({"individual": ind, **account_data})

    def _prepare_individual(
        self,
        serializer: serializers.Serializer,
    ) -> UUID:
        documents_data = serializer.validated_data.pop("documents", [])
        accounts_data = serializer.validated_data.pop("accounts", [])
        external_individual_id = serializer.validated_data.pop("individual_id")

        photo_b64 = serializer.validated_data.pop("photo", None)
        photo_file = self.get_photo(photo_b64)

        validated_data = dict(serializer.validated_data)
        validated_data["flex_fields"] = populate_pdu_with_null_values(
            self.selected_rdi.program, validated_data.get("flex_fields")
        )

        ind = PendingIndividual(
            household=None,
            program=self.selected_rdi.program,
            registration_data_import=self.selected_rdi,
            business_area=self.selected_rdi.business_area,
            **validated_data,
        )
        if photo_file:
            ind.photo.save(photo_file.name, File(photo_file), save=False)
            self.staging.saved_file_fields.append(ind.photo)

        calculate_phone_numbers_validity(ind)

        self.staging.valid_individuals.append(ind)
        self.staging.individual_external_ids_by_pk[str(ind.id)] = external_individual_id

        self._prepare_documents(documents_data, ind)
        self._prepare_accounts(accounts_data, ind)
        return ind.pk

    def _bulk_create_individuals_and_get_unicef_ids(self, batch_size: int) -> dict[str, str]:
        PendingIndividual.objects.bulk_create(self.staging.valid_individuals, batch_size=batch_size)
        created_ids = [ind.id for ind in self.staging.valid_individuals]
        return {
            str(row["id"]): row["unicef_id"]
            for row in PendingIndividual.objects.filter(id__in=created_ids).values("id", "unicef_id")
        }

    def _resolve_document_mappings(self) -> tuple[dict[str, int], dict[str, int]]:
        country_map: dict[str, int] = {}
        if self.staging.doc_country_codes:
            country_map = {
                c.iso_code2: c.id for c in Country.objects.filter(iso_code2__in=self.staging.doc_country_codes)
            }
        doc_type_map: dict[str, int] = {}
        if self.staging.doc_type_keys:
            doc_type_map = {dt.key: dt.id for dt in DocumentType.objects.filter(key__in=self.staging.doc_type_keys)}
        return country_map, doc_type_map

    def _bulk_create_documents(
        self, country_map: dict[str, int], doc_type_map: dict[str, int], batch_size: int
    ) -> None:
        doc_instances: list[PendingDocument] = []
        for item in self.staging.prepared_documents:
            ind = item["individual"]
            photo_file = item["photo_file"]
            country_id = country_map.get(item["country_code"]) if item["country_code"] else None
            type_id = doc_type_map.get(item["type_key"]) if item["type_key"] else None

            doc = PendingDocument(
                individual_id=ind.id,
                program_id=ind.program_id,
                document_number=item["document_number"] or "",
                type_id=type_id,
                country_id=country_id,
                issuance_date=item["issuance_date"],
                expiry_date=item["expiry_date"],
            )
            if photo_file:
                doc.photo.save(photo_file.name, File(photo_file), save=False)
                self.staging.saved_file_fields.append(doc.photo)
            doc_instances.append(doc)

        if doc_instances:
            PendingDocument.objects.bulk_create(doc_instances, batch_size=batch_size)

    def _bulk_create_accounts(self, batch_size: int) -> None:
        account_instances: list[PendingAccount] = []
        for acc in self.staging.prepared_accounts:
            ind = acc.pop("individual")
            account_instances.append(PendingAccount(individual_id=ind.id, **acc))
        if account_instances:
            PendingAccount.objects.bulk_create(account_instances, batch_size=batch_size)

    @extend_schema(request=IndividualSerializer(many=True))
    @atomic
    def post(self, request: Request, business_area: "BusinessArea", rdi: RegistrationDataImport) -> Response:
        individual_id_mapping = {}
        total_individuals = 0
        total_errors = 0
        results = []

        self.staging = IndividualsBulkStaging()

        try:
            for individual_raw_data in request.data:
                total_individuals += 1
                serializer = IndividualSerializer(data=individual_raw_data)

                if serializer.is_valid():
                    pk = self._prepare_individual(serializer)
                    results.append({"pk": pk})
                else:
                    results.append(serializer.errors)
                    total_errors += 1

            if not self.staging.valid_individuals:
                return Response(
                    {
                        "id": self.selected_rdi.id,
                        "processed": total_individuals,
                        "accepted": 0,
                        "errors": total_errors,
                        "individual_id_mapping": {},
                        "results": results,
                    },
                    status=status.HTTP_201_CREATED,
                )

            id_to_unicef = self._bulk_create_individuals_and_get_unicef_ids(BATCH_SIZE)

            country_map, doc_type_map = self._resolve_document_mappings()

            self._bulk_create_documents(country_map, doc_type_map, BATCH_SIZE)

            self._bulk_create_accounts(BATCH_SIZE)

            for ind in self.staging.valid_individuals:
                if external := self.staging.individual_external_ids_by_pk.get(str(ind.id)):
                    individual_id_mapping[external] = id_to_unicef.get(str(ind.id))

            accepted_count = len(self.staging.valid_individuals)
            response_payload = {
                "id": self.selected_rdi.id,
                "processed": total_individuals,
                "accepted": accepted_count,
                "errors": total_errors,
                "individual_id_mapping": individual_id_mapping,
                "results": results,
            }

        except Exception:
            for field_file in self.staging.saved_file_fields:
                with contextlib.suppress(Exception):
                    field_file.delete(save=False)
            raise

        return Response(response_payload, status=status.HTTP_201_CREATED)


class HouseholdSerializer(serializers.ModelSerializer):
    first_registration_date = serializers.DateTimeField(default=timezone.now)
    last_registration_date = serializers.DateTimeField(default=timezone.now)
    country = serializers.ChoiceField(choices=Countries())
    country_origin = serializers.ChoiceField(choices=Countries(), required=False)
    size = serializers.IntegerField(required=False, allow_null=True)
    consent_sharing = serializers.MultipleChoiceField(choices=DATA_SHARING_CHOICES, required=False)
    village = serializers.CharField(allow_blank=True, allow_null=True, required=False)
    head_of_household = serializers.SlugRelatedField(
        slug_field="unicef_id",
        required=True,
        queryset=PendingIndividual.objects.all(),
    )
    primary_collector = serializers.SlugRelatedField(
        slug_field="unicef_id",
        required=True,
        queryset=PendingIndividual.objects.all(),
    )
    alternate_collector = serializers.SlugRelatedField(
        slug_field="unicef_id",
        required=False,
        queryset=PendingIndividual.objects.all(),
    )
    members = serializers.ListField(child=serializers.CharField(), allow_empty=False)

    admin1 = serializers.SlugRelatedField(
        slug_field="p_code",
        required=False,
        allow_null=True,
        queryset=Area.objects.filter(area_type__area_level=1),
    )
    admin2 = serializers.SlugRelatedField(
        slug_field="p_code",
        required=False,
        allow_null=True,
        queryset=Area.objects.filter(area_type__area_level=2),
    )
    admin3 = serializers.SlugRelatedField(
        slug_field="p_code",
        required=False,
        allow_null=True,
        queryset=Area.objects.filter(area_type__area_level=3),
    )
    admin4 = serializers.SlugRelatedField(
        slug_field="p_code",
        required=False,
        allow_null=True,
        queryset=Area.objects.filter(area_type__area_level=4),
    )

    class Meta:
        model = PendingHousehold
        exclude = [
            "id",
            "registration_data_import",
            "business_area",
            "program",
            "kobo_submission_uuid",
            "kobo_submission_time",
            "latitude",
            "longitude",
            "detail_id",
            "version",
            "unicef_id",
        ]


class CreateLaxHouseholds(CreateLaxBaseView):
    """API to import households with selected RDI."""

    @extend_schema(request=HouseholdSerializer(many=True))
    @atomic
    def post(self, request: Request, business_area: "BusinessArea", rdi: RegistrationDataImport) -> Response:
        total_households = 0
        total_errors = 0
        total_accepted = 0
        results = []
        country_map = {}

        valid_payloads = []
        country_codes = set()

        for household_data in request.data:
            total_households += 1
            serializer: HouseholdSerializer = HouseholdSerializer(data=household_data)
            if serializer.is_valid():
                data = dict(serializer.validated_data)
                members: list[str] = data.pop("members", [])
                primary_collector = data.pop("primary_collector")
                alternate_collector = data.pop("alternate_collector", None)

                country_code = data.pop("country", None)
                if country_code:
                    country_codes.add(country_code)
                country_origin_code = data.pop("country_origin", None)
                if country_origin_code:
                    country_codes.add(country_origin_code)

                data["flex_fields"] = populate_pdu_with_null_values(self.selected_rdi.program, data.get("flex_fields"))

                household_instance = PendingHousehold(
                    registration_data_import=self.selected_rdi,
                    program_id=self.selected_rdi.program.id,
                    business_area=self.selected_business_area,
                    **data,
                )

                valid_payloads.append(
                    {
                        "instance": household_instance,
                        "members": members,
                        "primary": primary_collector,
                        "alternate": alternate_collector,
                        "country_code": country_code,
                        "country_origin_code": country_origin_code,
                    }
                )
            else:
                results.append(dict(serializer.errors))
                total_errors += 1

        if not valid_payloads:
            return Response(
                {
                    "id": self.selected_rdi.id,
                    "processed": total_households,
                    "accepted": total_accepted,
                    "errors": total_errors,
                    "results": results,
                },
                status=status.HTTP_201_CREATED,
            )

        if country_codes:
            country_map = {c.iso_code2: c for c in Country.objects.filter(iso_code2__in=country_codes)}

        for payload in valid_payloads:
            hh: PendingHousehold = payload["instance"]
            if cc := payload.get("country_code"):
                hh.country = country_map.get(cc)
            if coc := payload.get("country_origin_code"):
                hh.country_origin = country_map.get(coc)

        PendingHousehold.objects.bulk_create([p["instance"] for p in valid_payloads], batch_size=BATCH_SIZE)

        roles_to_create: list[IndividualRoleInHousehold] = []
        for payload in valid_payloads:
            primary = payload["primary"]
            alternate = payload["alternate"]

            if payload["members"]:
                PendingIndividual.objects.filter(
                    registration_data_import=self.selected_rdi,
                    program=self.selected_rdi.program,
                    unicef_id__in=payload["members"],
                ).update(household=payload["instance"])

            roles_to_create.append(
                IndividualRoleInHousehold(individual=primary, household=payload["instance"], role=ROLE_PRIMARY)
            )
            if alternate:
                roles_to_create.append(
                    IndividualRoleInHousehold(
                        individual=alternate,
                        household=payload["instance"],
                        role=ROLE_ALTERNATE,
                    )
                )

            total_accepted += 1
            results.append({"pk": payload["instance"].pk})  # noqa

        if roles_to_create:
            IndividualRoleInHousehold.objects.bulk_create(roles_to_create, batch_size=BATCH_SIZE)

        return Response(
            {
                "id": self.selected_rdi.id,
                "processed": total_households,
                "accepted": total_accepted,
                "errors": total_errors,
                "results": results,
            },
            status=status.HTTP_201_CREATED,
        )
