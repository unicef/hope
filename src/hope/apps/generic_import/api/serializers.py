from rest_framework import serializers


class GenericImportUploadSerializer(serializers.Serializer):
    """Walidacja pliku Excel dla generic import."""

    file = serializers.FileField(required=True)

    def validate_file(self, value):
        """Walidacja typu i rozmiaru pliku."""
        # Sprawdź rozszerzenie
        if not value.name.endswith((".xlsx", ".xls")):
            raise serializers.ValidationError("Only Excel files (.xlsx, .xls) are allowed.")

        # Sprawdź rozmiar (max 50MB)
        max_size = 50 * 1024 * 1024
        if value.size > max_size:
            raise serializers.ValidationError(
                f"File size must not exceed 50 MB. Current size: {value.size / (1024 * 1024):.2f} MB"
            )

        return value


class GenericImportResponseSerializer(serializers.Serializer):
    """Response z informacjami o ImportData i RDI."""

    import_data_id = serializers.UUIDField(source="import_data.id")
    import_data_status = serializers.CharField(source="import_data.status")
    rdi_id = serializers.UUIDField(source="id")
    rdi_name = serializers.CharField(source="name")
    rdi_status = serializers.CharField(source="status")
    created_at = serializers.DateTimeField(source="import_data.created_at")
    business_area_slug = serializers.CharField(source="business_area.slug")
    program_name = serializers.CharField(source="program.name")
