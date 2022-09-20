from rest_framework import serializers
from rest_framework.generics import CreateAPIView

from hct_mis_api.apps.registration_data.models import RegistrationDataImport

from .base import SelectedBusinessAreaMixin


class RDISerializer(serializers.ModelSerializer):
    class Meta:
        model = RegistrationDataImport
        exclude = ("business_area", "data_source")


class CreateRDIView(SelectedBusinessAreaMixin, CreateAPIView):
    def get_queryset(self):
        return RegistrationDataImport.objects.filter(business_area=self.selected_business_area)
