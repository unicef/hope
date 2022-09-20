from rest_framework import serializers
from rest_framework.generics import ListAPIView

from hct_mis_api.apps.geo.models import Country


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country


class CountryList(ListAPIView):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
