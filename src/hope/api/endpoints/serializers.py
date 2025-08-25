from django.db import models
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from models.geo import Country
from models.payment import FinancialInstitution


class RejectPolicy(models.TextChoices):
    STRICT = "STRICT", _("STRICT")
    LAX = "LAX", _("Lax")


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = (
            "id",
            "name",
            "short_name",
            "iso_code2",
            "iso_code3",
            "iso_num",
            "valid_from",
            "valid_until",
            "updated_at",
        )


class FinancialInstitutionListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    type = serializers.CharField(allow_null=True, allow_blank=True)
    swift_code = serializers.CharField(allow_null=True, allow_blank=True)
    country_iso_code3 = serializers.SerializerMethodField()
    updated_at = serializers.DateTimeField(allow_null=True)

    def get_country_iso_code3(self, obj: FinancialInstitution) -> str:
        return obj.country.iso_code3
