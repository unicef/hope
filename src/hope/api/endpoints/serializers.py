from rest_framework import serializers

from hope.models import Country, Currency, FinancialInstitution


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


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = (
            "id",
            "code",
            "vision_code",
            "name",
            "is_crypto",
        )


class FinancialInstitutionListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    type = serializers.CharField(allow_null=True, allow_blank=True)
    swift_code = serializers.CharField(allow_null=True, allow_blank=True)
    country_iso_code3 = serializers.SerializerMethodField()
    updated_at = serializers.DateTimeField(allow_null=True)

    def get_country_iso_code3(self, obj: FinancialInstitution) -> str | None:
        if country := obj.country:
            return country.iso_code3

        return None
