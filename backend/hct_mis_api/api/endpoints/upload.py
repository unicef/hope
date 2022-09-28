import logging
from dataclasses import asdict
from datetime import datetime

from django.db.transaction import atomic
from django.urls import reverse
from django.utils import timezone

from django_countries import Countries
from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from hct_mis_api.api.endpoints.base import HOPEAPIBusinessAreaView
from hct_mis_api.api.endpoints.mixin import HouseholdUploadMixin
from hct_mis_api.api.models import Grant
from hct_mis_api.api.utils import humanize_errors
from hct_mis_api.apps.household.models import (
    COLLECT_TYPE_FULL,
    COLLECT_TYPE_NONE,
    COLLECT_TYPE_PARTIAL,
    HEAD,
    IDENTIFICATION_TYPE_CHOICE,
    ROLE_ALTERNATE,
    ROLE_NO_ROLE,
    ROLE_PRIMARY,
)
from hct_mis_api.apps.registration_data.models import RegistrationDataImport
from hct_mis_api.apps.registration_datahub.models import (
    ImportedDocument,
    ImportedHousehold,
    ImportedIndividual,
    RegistrationDataImportDatahub,
)

logger = logging.getLogger(__name__)


class BirthDateValidator:
    def __call__(self, value):
        if value >= datetime.today().date():
            raise ValidationError("Birth date must be in the past")


class HouseholdValidator:
    def __call__(self, value):
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
    type = serializers.ChoiceField(choices=IDENTIFICATION_TYPE_CHOICE, allow_blank=True, required=False)
    country = serializers.ChoiceField(choices=Countries())
    image = serializers.CharField(allow_blank=True, required=False)

    class Meta:
        model = ImportedDocument
        exclude = [
            "individual",
            "photo",
        ]


class CollectDataMixin(serializers.Serializer):
    def validate_collect_individual_data(self, value):
        if value in [COLLECT_TYPE_FULL, "FULL", "full"]:
            return COLLECT_TYPE_FULL
        if value in [COLLECT_TYPE_PARTIAL, "PARTIAL", "partial"]:
            return COLLECT_TYPE_PARTIAL
        if value in [COLLECT_TYPE_NONE, "NO", "N", "no"]:
            return COLLECT_TYPE_NONE
        raise ValidationError(
            "Invalid value %s. " "Check values at %s" % (value, reverse("api:datacollectingpolicy-list"))
        )


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
            "kobo_asset_id",
            "mis_unicef_id",
        ]

    def validate_role(self, value):
        if value in (ROLE_NO_ROLE, ROLE_PRIMARY, ROLE_ALTERNATE):
            return value
        if not value:
            return ROLE_NO_ROLE
        elif value.upper()[0] == "P":
            return ROLE_PRIMARY
        elif value.upper()[0] == "A":
            return ROLE_ALTERNATE
        raise ValidationError("Invalid value %s. " "Check values at %s" % (value, reverse("api:role-list")))


class HouseholdSerializer(CollectDataMixin, serializers.ModelSerializer):
    first_registration_date = serializers.DateTimeField(default=timezone.now)
    last_registration_date = serializers.DateTimeField(default=timezone.now)
    members = IndividualSerializer(many=True, required=True)
    country_origin = serializers.CharField(allow_blank=True, required=False)

    class Meta:
        model = ImportedHousehold
        exclude = [
            "id",
            "head_of_household",
            "registration_data_import",
            "mis_unicef_id",
            "diia_rec_id",
            "flex_registrations_record",
            "kobo_submission_uuid",
            "kobo_asset_id",
            "kobo_submission_time",
            "geopoint",
        ]
        validators = [HouseholdValidator()]

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret.pop("members", None)
        return ret


class RDINestedSerializer(CollectDataMixin, HouseholdUploadMixin, serializers.ModelSerializer):
    name = serializers.CharField(required=True)
    households = HouseholdSerializer(many=True, required=True)
    collect_individual_data = serializers.CharField()

    class Meta:
        model = RegistrationDataImportDatahub
        exclude = ("business_area_slug", "import_data", "hct_id")

    def __init__(self, *args, **kwargs):
        self.business_area = kwargs.pop("business_area", None)
        super().__init__(*args, **kwargs)

    def validate_households(self, value):
        if not value:
            raise ValidationError("This field is required.")
        return value

    @atomic()
    def create(self, validated_data):
        created_by = validated_data.pop("user")
        households = validated_data.pop("households")
        collect_individual_data = validated_data.pop("collect_individual_data")

        rdi_datahub = RegistrationDataImportDatahub.objects.create(
            **validated_data, business_area_slug=self.business_area.slug
        )
        info = self.save_households(rdi_datahub, households, collect_individual_data)
        rdi_mis = RegistrationDataImport.objects.create(
            **validated_data,
            imported_by=created_by,
            data_source=RegistrationDataImport.API,
            number_of_individuals=info.individuals,
            number_of_households=info.households,
            datahub_id=str(rdi_datahub.pk),
            business_area=self.business_area,
        )
        rdi_datahub.hct_id = rdi_mis.id
        rdi_datahub.save()

        return dict(id=rdi_datahub.pk, name=rdi_mis.name, public_id=rdi_mis.pk, **asdict(info))


class UploadRDIView(HOPEAPIBusinessAreaView):
    permission = Grant.API_RDI_UPLOAD

    @swagger_auto_schema(request_body=RDINestedSerializer)
    @atomic()
    @atomic(using="registration_datahub")
    def post(self, request, business_area):
        serializer = RDINestedSerializer(data=request.data, business_area=self.selected_business_area)
        if serializer.is_valid():
            info = serializer.save(user=request.user)
            return Response(info, status=status.HTTP_201_CREATED)
        errors = humanize_errors(serializer.errors)
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)
