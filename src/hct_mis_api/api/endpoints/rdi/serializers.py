from django.urls import reverse
from django.utils import timezone
from django_countries import Countries
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from hct_mis_api.api.endpoints.rdi.validators import BirthDateValidator
from hct_mis_api.apps.core.utils import IDENTIFICATION_TYPE_TO_KEY_MAPPING
from hct_mis_api.apps.geo.models import Area
from hct_mis_api.apps.household.models import (
    PendingDocument,
    PendingIndividual,
    ROLE_NO_ROLE,
    ROLE_PRIMARY,
    ROLE_ALTERNATE,
    IDENTIFICATION_TYPE_CHOICE,
    DATA_SHARING_CHOICES,
    PendingHousehold,
)
from hct_mis_api.apps.household.validators import HouseholdValidator
from hct_mis_api.apps.payment.models import FinancialInstitution, PendingAccount, AccountType


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
