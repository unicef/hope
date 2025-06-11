from typing import Dict, List, Union

from django.db.models import Q

from rest_framework import serializers

from hct_mis_api.apps.core.api.mixins import AdminUrlSerializerMixin
from hct_mis_api.apps.core.utils import get_count_and_percentage
from hct_mis_api.apps.registration_data.models import RegistrationDataImport
from hct_mis_api.apps.registration_datahub.utils import get_rdi_program_population


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
    ) -> List[Dict[str, Union[int, float]]]:
        result = [
            get_count_and_percentage(obj.batch_duplicates, obj.number_of_individuals),  # biographical
        ]
        if obj.biometric_deduplication_enabled:
            result.append(get_count_and_percentage(obj.dedup_engine_batch_duplicates, obj.number_of_individuals))
        return result

    def resolve_batch_unique_count_and_percentage(
        self, obj: RegistrationDataImport
    ) -> List[Dict[str, Union[int, float]]]:
        result = [
            get_count_and_percentage(obj.batch_unique, obj.number_of_individuals),  # biographical
        ]
        if obj.biometric_deduplication_enabled:
            biometric_unique = obj.number_of_individuals - obj.dedup_engine_batch_duplicates
            result.append(get_count_and_percentage(biometric_unique, obj.number_of_individuals))
        return result

    def resolve_golden_record_duplicates_count_and_percentage(
        self, obj: RegistrationDataImport
    ) -> List[Dict[str, Union[int, float]]]:
        return [
            get_count_and_percentage(obj.golden_record_duplicates, obj.number_of_individuals),  # biographical
        ]

    def resolve_golden_record_possible_duplicates_count_and_percentage(
        self, obj: RegistrationDataImport
    ) -> List[Dict[str, Union[int, float]]]:
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
    ) -> List[Dict[str, Union[int, float]]]:
        result = [
            get_count_and_percentage(obj.golden_record_unique, obj.number_of_individuals),  # biographical
        ]
        if obj.biometric_deduplication_enabled:
            biometric_unique = obj.number_of_individuals - obj.dedup_engine_golden_record_duplicates
            result.append(get_count_and_percentage(biometric_unique, obj.number_of_individuals))
        return result

    def get_total_households_count_with_valid_phone_no(self, obj: RegistrationDataImport) -> int:
        count = (
            obj.households.filter(
                Q(head_of_household__phone_no_valid=True) | Q(head_of_household__phone_no_alternative_valid=True)
            )
            .distinct()
            .count()
        )
        return count


class RefuseRdiSerializer(serializers.Serializer):
    reason = serializers.CharField(required=True)


class RegistrationDataImportCreateSerializer(serializers.Serializer):
    import_from_program_id = serializers.CharField(required=True)
    import_from_ids = serializers.CharField(
        required=True, allow_blank=True, help_text="String of Ind or HH ids separated by comma"
    )
    name = serializers.CharField(required=True)
    screen_beneficiary = serializers.BooleanField(required=True)

    def get_object(self, validated_data: dict) -> RegistrationDataImport:
        request = self.context["request"]
        program = self.context["program"]
        business_area = self.context["business_area"]
        user = request.user
        screen_beneficiary = validated_data.get("screen_beneficiary", False)
        import_from_program_id: str = validated_data["import_from_program_id"]
        import_from_ids = validated_data.get("import_from_ids")
        households, individuals = get_rdi_program_population(import_from_program_id, program.id, import_from_ids)
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
        )
