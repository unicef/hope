from functools import cached_property
from typing import TYPE_CHECKING

from django.http import Http404
from django.utils import timezone

from django_countries import Countries
from drf_spectacular.utils import extend_schema
from rest_framework import serializers, status
from rest_framework.request import Request
from rest_framework.response import Response

from hct_mis_api.api.endpoints.base import HOPEAPIBusinessAreaView
from hct_mis_api.api.endpoints.rdi.mixin import AccountMixin, DocumentMixin, PhotoMixin
from hct_mis_api.api.endpoints.rdi.upload import BirthDateValidator
from hct_mis_api.api.models import Grant
from hct_mis_api.apps.core.utils import IDENTIFICATION_TYPE_TO_KEY_MAPPING
from hct_mis_api.apps.geo.models import Area, Country
from hct_mis_api.apps.household.models import (
    DATA_SHARING_CHOICES,
    IDENTIFICATION_TYPE_CHOICE,
    ROLE_ALTERNATE,
    ROLE_PRIMARY,
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

if TYPE_CHECKING:
    from hct_mis_api.apps.core.models import BusinessArea


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


class IndividualSerializer(serializers.ModelSerializer, PhotoMixin):
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

    def create(self, validated_data: dict) -> PendingIndividual:
        """Create individual with associated documents and accounts using existing mixins."""
        photo_data = validated_data.pop("photo", None)

        rdi = self.context.get("rdi")

        validated_data["flex_fields"] = populate_pdu_with_null_values(rdi.program, validated_data.get("flex_fields"))

        individual = PendingIndividual.objects.create(
            household=None,
            program=rdi.program,
            registration_data_import=rdi,
            business_area=rdi.business_area,
            photo=self.get_photo(photo_data),
            **validated_data,
        )

        return individual


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


class CreateLaxIndividuals(CreateLaxBaseView, DocumentMixin, AccountMixin, PhotoMixin):
    """API to import individuals with selected RDI."""

    @extend_schema(request=IndividualSerializer(many=True))
    def post(self, request: Request, business_area: "BusinessArea", rdi: RegistrationDataImport) -> Response:
        individual_id_mapping = {}
        total_individuals = 0
        total_errors = 0
        total_accepted = 0
        errs = []

        serializer_context = {
            "rdi": self.selected_rdi,
        }

        for individual_raw_data in request.data:
            total_individuals += 1
            serializer = IndividualSerializer(data=individual_raw_data, context=serializer_context)

            if serializer.is_valid():
                documents_data = serializer.validated_data.pop("documents", [])
                accounts_data = serializer.validated_data.pop("accounts", [])
                individual = serializer.save()

                for document_data in documents_data:
                    document_data["photo"] = self.get_photo(document_data.pop("image", None))
                    self.save_document(individual, document_data)

                for account_data in accounts_data:
                    self.save_account(individual, account_data)

                individual_id_mapping[individual.individual_id] = individual.unicef_id
                errs.append({"pk": individual.pk})
                total_accepted += 1
            else:
                errs.append(serializer.errors)
                total_errors += 1

        return Response(
            {
                "id": self.selected_rdi.id,
                "processed": total_individuals,
                "accepted": total_accepted,
                "errors": total_errors,
                "individual_id_mapping": individual_id_mapping,
                "results": errs,
            },
            status=status.HTTP_201_CREATED,
        )


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

    def create(self, validated_data: dict) -> PendingHousehold:
        rdi = self.context.get("rdi")
        business_area = self.context.get("business_area")

        validated_data["flex_fields"] = populate_pdu_with_null_values(rdi.program, validated_data.get("flex_fields"))

        if country := validated_data.get("country"):
            validated_data["country"] = Country.objects.get(iso_code2=country)
        if country_origin := validated_data.get("country_origin"):
            validated_data["country_origin"] = Country.objects.get(iso_code2=country_origin)

        household = PendingHousehold.objects.create(
            registration_data_import=rdi,
            program_id=rdi.program.id,
            business_area=business_area,
            **validated_data,
        )
        return household


class CreateLaxHouseholds(CreateLaxBaseView):
    """API to import households with selected RDI."""

    @extend_schema(request=HouseholdSerializer(many=True))
    def post(self, request: Request, business_area: "BusinessArea", rdi: RegistrationDataImport) -> Response:
        total_households = 0
        total_errors = 0
        total_accepted = 0
        errs = []

        serializer_context = {
            "rdi": self.selected_rdi,
            "business_area": self.selected_business_area,
        }

        for household_data in request.data:
            total_households += 1
            serializer: HouseholdSerializer = HouseholdSerializer(data=household_data, context=serializer_context)
            if serializer.is_valid():
                members: list[str] = serializer.validated_data.pop("members", [])
                primary_collector = serializer.validated_data.pop("primary_collector")
                alternate_collector = serializer.validated_data.pop("alternate_collector", None)
                household = serializer.save()

                PendingIndividual.objects.filter(unicef_id__in=members).update(household=household)
                household.individuals_and_roles.create(individual=primary_collector, role=ROLE_PRIMARY)
                if alternate_collector:
                    household.individuals_and_roles.create(individual=alternate_collector, role=ROLE_ALTERNATE)

                errs.append({"pk": household.pk})
                total_accepted += 1
            else:
                errs.append(serializer.errors)
                total_errors += 1

        return Response(
            {
                "id": self.selected_rdi.id,
                "processed": total_households,
                "accepted": total_accepted,
                "errors": total_errors,
                "results": errs,
            },
            status=status.HTTP_201_CREATED,
        )
