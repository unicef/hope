from rest_framework import serializers

from hct_mis_api.apps.account.api.serializers import UserSerializer
from hct_mis_api.apps.registration_data.models import RegistrationDataImport


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
