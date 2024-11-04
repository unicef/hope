from django.db import models
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from hct_mis_api.apps.geo.models import Country


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
