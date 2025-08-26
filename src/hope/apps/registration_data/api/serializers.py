import contextlib
import json
from typing import Any

from django.db.models import Q
from rest_framework import serializers

from hope.apps.core.api.mixins import AdminUrlSerializerMixin
from hope.apps.core.utils import get_count_and_percentage
from hope.models.registration_data import (
    ImportData,
    KoboImportData,
    RegistrationDataImport,
)
from hope.apps.registration_datahub.utils import get_rdi_program_population


class RegistrationDataImportListSerializer(serializers.ModelSerializer):
    status = serializers.CharField(source="get_status_display")
    data_source = serializers.CharField(source="get_data_source_display")
    imported_by = serializers.CharField(source="imported_by.get_full_name", default="")

    class Meta:
        model = RegistrationDataImport
        fields = (
            "id",
            "name",
            "status",
            "data_source",
            "imported_by",
            "created_at",
            "erased",
            "import_date",
            "number_of_households",
            "number_of_individuals",
            "biometric_deduplicated",
        )


class DeduplicationResultSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    percentage = serializers.FloatField()


class RegistrationDataImportDetailSerializer(serializers.ModelSerializer, AdminUrlSerializerMixin):
    status = serializers.CharField()
    status_display = serializers.CharField(source="get_status_display")
    data_source = serializers.CharField(source="get_data_source_display")
    imported_by = serializers.CharField(source="imported_by.get_full_name", default="")
    batch_duplicates_count_and_percentage = serializers.SerializerMethodField(
        method_name="resolve_batch_duplicates_count_and_percentage"
    )
    batch_unique_count_and_percentage = serializers.SerializerMethodField(
        method_name="resolve_batch_unique_count_and_percentage"
    )
    golden_record_unique_count_and_percentage = serializers.SerializerMethodField(
        method_name="resolve_golden_record_unique_count_and_percentage"
    )
    golden_record_duplicates_count_and_percentage = serializers.SerializerMethodField(
        method_name="resolve_golden_record_duplicates_count_and_percentage"
    )
    golden_record_possible_duplicates_count_and_percentage = serializers.SerializerMethodField(
        method_name="resolve_golden_record_possible_duplicates_count_and_percentage"
    )
    total_households_count_with_valid_phone_no = serializers.SerializerMethodField()

    class Meta:
        model = RegistrationDataImport
        fields = (
            "id",
            "name",
            "status",
            "status_display",
            "data_source",
            "imported_by",
            "created_at",
            "erased",
            "import_date",
            "number_of_households",
            "number_of_individuals",
            "biometric_deduplicated",
            "error_message",
            "can_merge",
            "biometric_deduplication_enabled",
            "deduplication_engine_status",
            "batch_duplicates_count_and_percentage",
            "batch_unique_count_and_percentage",
            "golden_record_duplicates_count_and_percentage",
            "golden_record_possible_duplicates_count_and_percentage",
            "golden_record_unique_count_and_percentage",
            "total_households_count_with_valid_phone_no",
            "admin_url",
        )

    def resolve_batch_duplicates_count_and_percentage(
        self, obj: RegistrationDataImport
    ) -> list[dict[str, int | float]]:
        result = [
            get_count_and_percentage(obj.batch_duplicates, obj.number_of_individuals),  # biographical
        ]
        if obj.biometric_deduplication_enabled:
            result.append(get_count_and_percentage(obj.dedup_engine_batch_duplicates, obj.number_of_individuals))
        return result

    def resolve_batch_unique_count_and_percentage(self, obj: RegistrationDataImport) -> list[dict[str, int | float]]:
        result = [
            get_count_and_percentage(obj.batch_unique, obj.number_of_individuals),  # biographical
        ]
        if obj.biometric_deduplication_enabled:
            biometric_unique = obj.number_of_individuals - obj.dedup_engine_batch_duplicates
            result.append(get_count_and_percentage(biometric_unique, obj.number_of_individuals))
        return result

    def resolve_golden_record_duplicates_count_and_percentage(
        self, obj: RegistrationDataImport
    ) -> list[dict[str, int | float]]:
        return [
            get_count_and_percentage(obj.golden_record_duplicates, obj.number_of_individuals),  # biographical
        ]

    def resolve_golden_record_possible_duplicates_count_and_percentage(
        self, obj: RegistrationDataImport
    ) -> list[dict[str, int | float]]:
        result = [
            get_count_and_percentage(obj.golden_record_possible_duplicates, obj.number_of_individuals),  # biographical
        ]
        if obj.biometric_deduplication_enabled:
            result.append(
                get_count_and_percentage(obj.dedup_engine_golden_record_duplicates, obj.number_of_individuals)
            )
        return result

    def resolve_golden_record_unique_count_and_percentage(
        self, obj: RegistrationDataImport
    ) -> list[dict[str, int | float]]:
        result = [
            get_count_and_percentage(obj.golden_record_unique, obj.number_of_individuals),  # biographical
        ]
        if obj.biometric_deduplication_enabled:
            biometric_unique = obj.number_of_individuals - obj.dedup_engine_golden_record_duplicates
            result.append(get_count_and_percentage(biometric_unique, obj.number_of_individuals))
        return result

    def get_total_households_count_with_valid_phone_no(self, obj: RegistrationDataImport) -> int:
        return (
            obj.households.filter(
                Q(head_of_household__phone_no_valid=True) | Q(head_of_household__phone_no_alternative_valid=True)
            )
            .distinct()
            .count()
        )


class RefuseRdiSerializer(serializers.Serializer):
    reason = serializers.CharField(required=True)


class RegistrationDataImportCreateSerializer(serializers.Serializer):
    import_from_program_id = serializers.CharField(required=True)
    import_from_ids = serializers.CharField(
        required=True,
        allow_blank=True,
        help_text="String of Ind or HH ids separated by comma",
    )
    name = serializers.CharField(required=True)
    screen_beneficiary = serializers.BooleanField(required=True)
    exclude_external_collectors = serializers.BooleanField(required=False, default=False)

    def get_object(self, validated_data: dict) -> RegistrationDataImport:
        request = self.context["request"]
        program = self.context["program"]
        business_area = self.context["business_area"]
        user = request.user
        screen_beneficiary = validated_data.get("screen_beneficiary", False)
        import_from_program_id: str = validated_data["import_from_program_id"]
        import_from_ids = validated_data.get("import_from_ids")
        exclude_external_collectors = validated_data["exclude_external_collectors"]
        households, individuals = get_rdi_program_population(
            import_from_program_id,
            program.id,
            import_from_ids,
            exclude_external_collectors,
        )
        return RegistrationDataImport(
            name=validated_data["name"],
            status=RegistrationDataImport.IMPORTING,
            imported_by=user,
            data_source=RegistrationDataImport.PROGRAM_POPULATION,
            number_of_individuals=individuals.count(),
            number_of_households=households.count(),
            business_area=business_area,
            pull_pictures=True,
            screen_beneficiary=screen_beneficiary,
            program=program,
            import_from_ids=import_from_ids,
            exclude_external_collectors=exclude_external_collectors,
        )


# New serializers for the GraphQL mutations conversion


class XlsxRowErrorSerializer(serializers.Serializer):
    """Serializer for XLSX validation errors."""

    row_number = serializers.IntegerField()
    header = serializers.CharField()
    message = serializers.CharField()


class ImportDataSerializer(serializers.ModelSerializer):
    xlsx_validation_errors = serializers.SerializerMethodField()

    class Meta:
        model = ImportData
        fields = (
            "id",
            "status",
            "data_type",
            "number_of_households",
            "number_of_individuals",
            "error",
            "validation_errors",
            "xlsx_validation_errors",
            "created_at",
            "business_area_slug",
        )
        read_only_fields = fields

    def get_xlsx_validation_errors(self, obj: ImportData) -> list[dict[str, Any]]:
        """Parse validation errors JSON into structured format."""
        errors = []
        if obj.validation_errors:
            with contextlib.suppress(json.JSONDecodeError, TypeError):
                errors.extend(json.loads(obj.validation_errors))
        return errors


class KoboErrorSerializer(serializers.Serializer):
    """Serializer for Kobo validation errors."""

    header = serializers.CharField()
    message = serializers.CharField()


class KoboImportDataSerializer(serializers.ModelSerializer):
    kobo_validation_errors = serializers.SerializerMethodField()

    class Meta:
        model = KoboImportData
        fields = (
            "id",
            "status",
            "data_type",
            "number_of_households",
            "number_of_individuals",
            "error",
            "validation_errors",
            "kobo_validation_errors",
            "created_at",
            "kobo_asset_id",
            "only_active_submissions",
            "pull_pictures",
            "business_area_slug",
        )
        read_only_fields = fields

    def get_kobo_validation_errors(self, obj: KoboImportData) -> list[dict[str, Any]]:
        """Parse kobo validation errors JSON into structured format."""
        if not obj.validation_errors:
            return []
        try:
            return json.loads(obj.validation_errors)
        except (json.JSONDecodeError, TypeError):
            return []


class UploadXlsxFileSerializer(serializers.Serializer):
    file = serializers.FileField(required=True)


class SaveKoboImportDataSerializer(serializers.Serializer):
    uid = serializers.CharField(required=True, help_text="Kobo asset ID")
    only_active_submissions = serializers.BooleanField(required=True)
    pull_pictures = serializers.BooleanField(required=True)


class RegistrationXlsxImportSerializer(serializers.Serializer):
    import_data_id = serializers.CharField(required=True)
    name = serializers.CharField(required=True)
    screen_beneficiary = serializers.BooleanField(required=True)


class RegistrationKoboImportSerializer(serializers.Serializer):
    import_data_id = serializers.CharField(required=True)
    name = serializers.CharField(required=True)
    pull_pictures = serializers.BooleanField(required=True)
    screen_beneficiary = serializers.BooleanField(required=True)
