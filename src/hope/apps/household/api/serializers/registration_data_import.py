from rest_framework import serializers

from hope.apps.account.api.serializers import UserSerializer
from hope.models.registration_data_import import RegistrationDataImport


class RegistrationDataImportSerializer(serializers.ModelSerializer):
    imported_by = UserSerializer()

    class Meta:
        model = RegistrationDataImport
        fields = (
            "id",
            "name",
            "status",
            "import_date",
            "number_of_individuals",
            "number_of_households",
            "imported_by",
            "data_source",
        )
