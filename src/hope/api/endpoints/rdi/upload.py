from dataclasses import asdict
from datetime import date, datetime
import logging
from typing import Any

from django.db.transaction import atomic
from django.urls import reverse
from django.utils import timezone
from django_countries import Countries
from drf_spectacular.utils import extend_schema
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from hope.api.endpoints.base import HOPEAPIBusinessAreaView
from hope.api.endpoints.rdi.mixin import HouseholdUploadMixin
from hope.api.utils import humanize_errors
from hope.apps.core.utils import IDENTIFICATION_TYPE_TO_KEY_MAPPING
from hope.models.account import PendingAccount
from hope.models.account_type import AccountType
from hope.models.area import Area
from hope.models.document import PendingDocument
from hope.models.financial_institution import FinancialInstitution
from hope.models.grant import Grant
from hope.models.household import (
    DATA_SHARING_CHOICES,
    HEAD,
    IDENTIFICATION_TYPE_CHOICE,
    ROLE_ALTERNATE,
    ROLE_NO_ROLE,
    ROLE_PRIMARY,
    PendingHousehold,
)
from hope.models.individual import PendingIndividual
from hope.models.program import Program
from hope.models.registration_data_import import RegistrationDataImport

logger = logging.getLogger(__name__)


class BirthDateValidator:
    def __call__(self, value: date) -> None:
        if value >= datetime.today().date():
            raise ValidationError("Birth date must be in the past")


class HouseholdValidator:
    def __call__(self, value: Any) -> None:  # noqa
        head_of_household = None
        alternate_collector = None
        primary_collector = None
        members = value.get("members", [])
        errs = {}
        if not members:
            raise ValidationError({"members": "This field is required"})
        for data in members:
            rel = data.get("relationship", None)
            role = data.get("role", None)
            if rel == HEAD:
                if head_of_household:
                    errs["head_of_household"] = "Only one HoH allowed"
                head_of_household = data
            if role == ROLE_PRIMARY:
                if primary_collector:
                    errs["primary_collector"] = "Only one Primary Collector allowed"
                primary_collector = data
            elif role == ROLE_ALTERNATE:
                if alternate_collector:
                    errs["alternate_collector"] = "Only one Alternate Collector allowed"
                alternate_collector = data
        if not head_of_household:
            errs["head_of_household"] = "Missing Head Of Household"
        if not primary_collector:
            errs["primary_collector"] = "Missing Primary Collector"
        if errs:
            raise ValidationError(errs)


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
        exclude = [
            "individual",
            "photo",
            "program",
        ]


class AccountSerializer(serializers.ModelSerializer):
    account_type = serializers.SlugRelatedField(slug_field="key", required=True, queryset=AccountType.objects.all())
    number = serializers.CharField(allow_blank=True, required=False)
    financial_institution = serializers.PrimaryKeyRelatedField(
        required=False, queryset=FinancialInstitution.objects.all()
    )
    data = serializers.JSONField(required=False, default=dict)  # type: ignore

    class Meta:
        model = PendingAccount
        exclude = ["individual", "unique_key", "is_unique", "signature_hash"]


class IndividualSerializer(serializers.ModelSerializer):
    first_registration_date = serializers.DateTimeField(default=timezone.now)
    last_registration_date = serializers.DateTimeField(default=timezone.now)
    household = serializers.ReadOnlyField()
    role = serializers.CharField(allow_blank=True, required=False)
    observed_disability = serializers.CharField(allow_blank=True, required=False)
    country_origin = serializers.CharField(allow_blank=True, required=False)
    marital_status = serializers.CharField(allow_blank=True, required=False)
    documents = DocumentSerializer(many=True, required=False)
    birth_date = serializers.DateField(validators=[BirthDateValidator()])
    accounts = AccountSerializer(many=True, required=False)
    photo = serializers.CharField(allow_blank=True, required=False)

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
        ]

    def validate_role(self, value: str) -> str | None:
        if value in (ROLE_NO_ROLE, ROLE_PRIMARY, ROLE_ALTERNATE):
            return value
        if not value:
            return ROLE_NO_ROLE
        if value.upper()[0] == "P":
            return ROLE_PRIMARY
        if value.upper()[0] == "A":
            return ROLE_ALTERNATE
        raise ValidationError("Invalid value %s. Check values at %s" % (value, reverse("api:role-list")))


class HouseholdSerializer(serializers.ModelSerializer):
    first_registration_date = serializers.DateTimeField(default=timezone.now)
    last_registration_date = serializers.DateTimeField(default=timezone.now)
    members = IndividualSerializer(many=True, required=True)
    country = serializers.ChoiceField(choices=Countries())
    country_origin = serializers.ChoiceField(choices=Countries(), required=False)
    size = serializers.IntegerField(required=False, allow_null=True)
    consent_sharing = serializers.MultipleChoiceField(choices=DATA_SHARING_CHOICES, required=False)
    village = serializers.CharField(allow_blank=True, allow_null=True, required=False)

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
            "head_of_household",
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
        validators = [HouseholdValidator()]

    def to_representation(self, instance: PendingHousehold) -> dict:
        ret = super().to_representation(instance)
        ret.pop("members", None)
        return ret

    def validate(self, attrs: dict) -> dict:
        return attrs


class RDINestedSerializer(HouseholdUploadMixin, serializers.ModelSerializer):
    name = serializers.CharField(required=True)
    households = HouseholdSerializer(many=True, required=True)
    program = serializers.SlugRelatedField(
        slug_field="id", required=True, queryset=Program.objects.all(), write_only=True
    )

    class Meta:
        model = RegistrationDataImport
        fields = ("name", "households", "program")

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.business_area = kwargs.pop("business_area", None)
        super().__init__(*args, **kwargs)

    def validate_households(self, value: Any) -> Any:
        if not value:
            raise ValidationError("This field is required.")
        return value

    @atomic()
    def create(self, validated_data: dict) -> dict:
        created_by = validated_data.pop("user")
        households = validated_data.pop("households")
        program = validated_data.pop("program")

        rdi = RegistrationDataImport.objects.create(
            **validated_data,
            imported_by=created_by,
            data_source=RegistrationDataImport.API,
            number_of_individuals=0,
            number_of_households=0,
            business_area=self.business_area,
            program=program,
        )
        if program.biometric_deduplication_enabled:
            rdi.deduplication_engine_status = RegistrationDataImport.DEDUP_ENGINE_PENDING

        info = self.save_households(rdi, households)
        rdi.number_of_households = info.households
        rdi.number_of_individuals = info.individuals
        rdi.save()

        return dict(id=rdi.pk, name=rdi.name, **asdict(info))


class UploadRDIView(HOPEAPIBusinessAreaView):
    permission = Grant.API_RDI_UPLOAD

    @extend_schema(request=RDINestedSerializer)
    @atomic()
    def post(self, request: "Request", business_area: "BusinessArea") -> Response:
        serializer = RDINestedSerializer(data=request.data, business_area=self.selected_business_area)
        if serializer.is_valid():
            info = serializer.save(user=request.user)
            return Response(info, status=status.HTTP_201_CREATED)
        errors = humanize_errors(serializer.errors)
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)
