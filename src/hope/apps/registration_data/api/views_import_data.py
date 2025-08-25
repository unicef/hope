from rest_framework.mixins import RetrieveModelMixin

from hope.apps.account.permissions import Permissions
from hope.apps.core.api.mixins import BaseViewSet, BusinessAreaMixin
from hope.apps.registration_data.api.serializers import (
    ImportDataSerializer,
    KoboImportDataSerializer,
)
from models.registration_data import ImportData, KoboImportData


class ImportDataViewSet(
    BusinessAreaMixin,
    RetrieveModelMixin,
    BaseViewSet,
):
    """ViewSet for accessing ImportData objects (XLSX file uploads).

    Provides read-only access to import data objects.
    """

    queryset = ImportData.objects.all()
    serializer_class = ImportDataSerializer
    permissions_by_action = {
        "retrieve": [Permissions.RDI_VIEW_DETAILS],
    }

    # ImportData has business_area_slug field, not business_area FK
    business_area_model_field = None

    def get_queryset(self):
        """Filter ImportData by business area."""
        return self.queryset.filter(business_area_slug=self.business_area_slug)


class KoboImportDataViewSet(
    BusinessAreaMixin,
    RetrieveModelMixin,
    BaseViewSet,
):
    """ViewSet for accessing KoboImportData objects (Kobo submissions).

    Provides read-only access to kobo import data objects.
    """

    queryset = KoboImportData.objects.all()
    serializer_class = KoboImportDataSerializer
    permissions_by_action = {
        "retrieve": [Permissions.RDI_VIEW_DETAILS],
    }

    # KoboImportData has business_area_slug field, not business_area FK
    business_area_model_field = None

    def get_queryset(self):
        """Filter KoboImportData by business area."""
        return self.queryset.filter(business_area_slug=self.business_area_slug)
