from rest_framework import serializers
from rest_framework.generics import ListAPIView

from hct_mis_api.apps.geo.models import Area, AreaType


class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area


class AreaList(ListAPIView):
    queryset = Area.objects.all()
    serializer_class = AreaSerializer


class AreaTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AreaType


class AreaTypeList(ListAPIView):
    queryset = AreaType.objects.all()
    serializer_class = AreaTypeSerializer
