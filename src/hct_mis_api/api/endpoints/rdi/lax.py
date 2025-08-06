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
from hct_mis_api.apps.household.models import (
    IDENTIFICATION_TYPE_CHOICE,
    PendingDocument,
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


class IndividualSerializer(serializers.ModelSerializer, DocumentMixin, AccountMixin, PhotoMixin):
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
        documents_data = validated_data.pop("documents", [])
        accounts_data = validated_data.pop("accounts", [])
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

        for document_data in documents_data:
            self.save_document(individual, document_data)

        for account_data in accounts_data:
            self.save_account(individual, account_data)

        return individual


class CreateLaxIndividuals(HOPEAPIBusinessAreaView):
    """API to import individuals with selected RDI."""

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
                individual = serializer.save()
                individual_id_mapping[individual.individual_id] = individual.unicef_id
                errs.append({"pk": individual.unicef_id})
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
