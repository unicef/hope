from rest_framework import serializers

from hope.models import NOT_DISABLED, RegistrationDataImport


class NullableChoiceField(serializers.ChoiceField):
    def to_internal_value(self, data):
        if data == "":
            return None
        return super().to_internal_value(data)


class DisabilityChoiceField(serializers.ChoiceField):
    def to_internal_value(self, data):
        if data == "":
            return NOT_DISABLED
        return super().to_internal_value(data)


def mark_by_biometric_deduplication(rdi: RegistrationDataImport):
    if rdi.program.biometric_deduplication_enabled:
        rdi.deduplication_engine_status = RegistrationDataImport.DEDUP_ENGINE_PENDING
        rdi.save()
