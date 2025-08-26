from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import serializers
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import ListAPIView

from hope.api.filters import AreaFilter, AreaTypeFilter
from hope.models.geo import Area, AreaType


class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = "__all__"


class AreaList(ListAPIView):
    queryset = Area.objects.all().order_by("name")
    serializer_class = AreaSerializer
    filter_backends = (OrderingFilter, DjangoFilterBackend, SearchFilter)
    filterset_class = AreaFilter
    search_fields = ("name", "p_code")


class AreaTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AreaType
        fields = "__all__"


class AreaTypeList(ListAPIView):
    queryset = AreaType.objects.all().order_by("name")
    serializer_class = AreaTypeSerializer
    filter_backends = (OrderingFilter, DjangoFilterBackend, SearchFilter)
    filterset_class = AreaTypeFilter
    search_fields = ("name",)
