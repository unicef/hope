from typing import List, Dict, Union, Any

from rest_framework import serializers

from hct_mis_api.api.utils import EncodedIdSerializerMixin
from hct_mis_api.apps.core.utils import get_count_and_percentage
from hct_mis_api.apps.registration_data.models import RegistrationDataImport


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

class RegistrationDataImportDetailSerializer(serializers.ModelSerializer):
    status = serializers.CharField(source="get_status_display")
    data_source = serializers.CharField(source="get_data_source_display")
    imported_by = serializers.CharField(source="imported_by.get_full_name", default="")
    batch_duplicates_count_and_percentage = serializers.SerializerMethodField(method_name="resolve_batch_duplicates_count_and_percentage")
    batch_unique_count_and_percentage = serializers.SerializerMethodField(method_name="resolve_batch_unique_count_and_percentage")
    golden_record_unique_count_and_percentage = serializers.SerializerMethodField(method_name="resolve_golden_record_unique_count_and_percentage")
    golden_record_duplicates_count_and_percentage = serializers.SerializerMethodField(method_name="resolve_golden_record_duplicates_count_and_percentage")
    golden_record_possible_duplicates_count_and_percentage = serializers.SerializerMethodField(method_name="resolve_golden_record_possible_duplicates_count_and_percentage")

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
            "error_message",
            "can_merge",
            "biometric_deduplication_enabled",
            "deduplication_engine_status",
            "batch_duplicates_count_and_percentage",
            "batch_unique_count_and_percentage",
            "golden_record_duplicates_count_and_percentage",
            "golden_record_possible_duplicates_count_and_percentage",
            "golden_record_unique_count_and_percentage",
        )


    def resolve_batch_duplicates_count_and_percentage(
        self,obj: RegistrationDataImport
    ) -> List[Dict[str, Union[int, float]]]:
        result = [
            get_count_and_percentage(obj.batch_duplicates, obj.number_of_individuals),  # biographical
        ]
        if obj.biometric_deduplication_enabled:
            result.append(get_count_and_percentage(obj.dedup_engine_batch_duplicates, obj.number_of_individuals))
        return result


    def resolve_batch_unique_count_and_percentage(
        self,obj:RegistrationDataImport
    ) -> List[Dict[str, Union[int, float]]]:
        result = [
            get_count_and_percentage(obj.batch_unique, obj.number_of_individuals),  # biographical
        ]
        if obj.biometric_deduplication_enabled:
            biometric_unique = obj.number_of_individuals - obj.dedup_engine_batch_duplicates
            result.append(get_count_and_percentage(biometric_unique, obj.number_of_individuals))
        return result

    def resolve_golden_record_duplicates_count_and_percentage(

        self,obj:RegistrationDataImport
    ) -> List[Dict[str, Union[int, float]]]:
        return [
            get_count_and_percentage(obj.golden_record_duplicates, obj.number_of_individuals),  # biographical
        ]

    def resolve_golden_record_possible_duplicates_count_and_percentage(

        self,obj:RegistrationDataImport
    ) -> List[Dict[str, Union[int, float]]]:
        result = [
            get_count_and_percentage(
                obj.golden_record_possible_duplicates, obj.number_of_individuals
            ),  # biographical
        ]
        if obj.biometric_deduplication_enabled:
            result.append(
                get_count_and_percentage(obj.dedup_engine_golden_record_duplicates, obj.number_of_individuals)
            )
        return result

    def resolve_golden_record_unique_count_and_percentage(
        self,obj:RegistrationDataImport
    ) -> List[Dict[str, Union[int, float]]]:
        result = [
            get_count_and_percentage(obj.golden_record_unique, obj.number_of_individuals),  # biographical
        ]
        if obj.biometric_deduplication_enabled:
            biometric_unique = obj.number_of_individuals - obj.dedup_engine_golden_record_duplicates
            result.append(get_count_and_percentage(biometric_unique, obj.number_of_individuals))
        return result


