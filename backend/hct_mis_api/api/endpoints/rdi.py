from django.utils.functional import cached_property

from rest_framework import serializers, status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response

from hct_mis_api.apps.registration_datahub.models import RegistrationDataImportDatahub

from .base import HOPEAPIView, SelectedBusinessAreaMixin
from .upload import HouseholdSerializer

HOPEAPIView
from ...apps.account.permissions import Permissions


class RDISerializer(serializers.ModelSerializer):
    class Meta:
        model = RegistrationDataImportDatahub
        exclude = ("business_area_slug", "import_data", "hct_id")

    def create(self, validated_data):
        return super().create(validated_data)


class CreateRDIView(HOPEAPIView, CreateAPIView):
    permission = Permissions.API_CREATE_RDI
    serializer_class = RDISerializer

    def get_queryset(self):
        return RegistrationDataImportDatahub.objects.filter(business_area=self.selected_business_area)

    def perform_create(self, serializer):
        serializer.save(
            business_area_slug=self.selected_business_area.slug, import_done=RegistrationDataImportDatahub.LOADING
        )


class PushToRDIView(HOPEAPIView):
    permission = Permissions.API_CREATE_RDI

    @cached_property
    def selected_rdi(self):
        return RegistrationDataImportDatahub.objects.get(
            id=self.kwargs["rdi"], business_area_slug=self.kwargs["business_area"]
        )

    def post(self, request, business_area, rdi):
        serializer = HouseholdSerializer(data=request.data, many=True)
        if serializer.is_valid():
            serializer.save(rdi=self.selected_rdi)
            return Response({}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
