from typing import Dict

from rest_framework import serializers

from hct_mis_api.apps.account.api.fields import Base64ModelField
from hct_mis_api.apps.core.api.mixins import AdminUrlSerializerMixin
from hct_mis_api.apps.core.utils import resolve_flex_fields_choices_to_string
from hct_mis_api.apps.household.api.serializers.registration_data_import import (
    RegistrationDataImportSerializer,
)
from hct_mis_api.apps.household.models import DUPLICATE, Household


class HouseholdListSerializer(serializers.ModelSerializer):
    id = Base64ModelField(model_name="Household")
    head_of_household = serializers.CharField(source="head_of_household.full_name")
    admin1 = serializers.CharField(source="admin1.name", default="")
    admin2 = serializers.CharField(source="admin2.name", default="")
    program = serializers.CharField(source="program.name", default="")
    total_cash_received = serializers.DecimalField(max_digits=64, decimal_places=2)
    total_cash_received_usd = serializers.DecimalField(max_digits=64, decimal_places=2)

    class Meta:
        model = Household
        fields = [
            "id",
            "unicef_id",
            "head_of_household",
            "admin1",
            "admin2",
            "program",
            "status",
            "size",
            "residence_status",
            "total_cash_received",
            "total_cash_received_usd",
            "last_registration_date",
        ]


class HouseholdDetailSerializer(AdminUrlSerializerMixin, serializers.ModelSerializer):
    id = Base64ModelField(model_name="Household")
    head_of_household = serializers.CharField(source="head_of_household.full_name")
    admin1 = serializers.CharField(source="admin1.name", default="")
    admin2 = serializers.CharField(source="admin2.name", default="")
    admin3 = serializers.CharField(source="admin3.name", default="")
    admin4 = serializers.CharField(source="admin4.name", default="")
    program = serializers.CharField(source="program.name", default="")
    country = serializers.CharField(source="country.name", default="")
    country_origin = serializers.CharField(source="country_origin.name", default="")
    total_cash_received = serializers.DecimalField(max_digits=64, decimal_places=2)
    total_cash_received_usd = serializers.DecimalField(max_digits=64, decimal_places=2)
    has_duplicates = serializers.SerializerMethodField()
    registration_data_import = RegistrationDataImportSerializer()
    flex_fields = serializers.SerializerMethodField()
    admin_area_title = serializers.SerializerMethodField()
    active_individuals_count = serializers.SerializerMethodField()
    geopoint = serializers.SerializerMethodField()
    import_id = serializers.SerializerMethodField()

    class Meta:
        model = Household
        fields = (
            "id",
            "unicef_id",
            "head_of_household",
            "admin1",
            "admin2",
            "admin3",
            "admin4",
            "program",
            "country",
            "country_origin",
            "status",
            "total_cash_received",
            "total_cash_received_usd",
            "sanction_list_possible_match",
            "sanction_list_confirmed_match",
            "has_duplicates",
            "registration_data_import",
            "flex_fields",
            "admin_area_title",
            "active_individuals_count",
            "geopoint",
            "import_id",
            "admin_url",
            "male_children_count",
            "female_children_count",
            "children_disabled_count",
            "currency",
            "first_registration_date",
            "last_registration_date",
            "unhcr_id",
            "village",
            "address",
            "zip_code",
            "female_age_group_0_5_count",
            "female_age_group_6_11_count",
            "female_age_group_12_17_count",
            "female_age_group_18_59_count",
            "female_age_group_60_count",
            "pregnant_count",
            "male_age_group_0_5_count",
            "male_age_group_6_11_count",
            "male_age_group_12_17_count",
            "male_age_group_18_59_count",
            "male_age_group_60_count",
            "female_age_group_0_5_disabled_count",
            "female_age_group_6_11_disabled_count",
            "female_age_group_12_17_disabled_count",
            "female_age_group_18_59_disabled_count",
            "female_age_group_60_disabled_count",
            "male_age_group_0_5_disabled_count",
            "male_age_group_6_11_disabled_count",
            "male_age_group_12_17_disabled_count",
            "male_age_group_18_59_disabled_count",
            "male_age_group_60_disabled_count",
            "start",
            "deviceid",
            "fchild_hoh",
            "child_hoh",
            "returnee",
            "size",
            "residence_status",
        )

    def get_has_duplicates(self, obj: Household) -> bool:
        return obj.individuals.filter(deduplication_golden_record_status=DUPLICATE).exists()

    def get_flex_fields(self, obj: Household) -> Dict:
        return resolve_flex_fields_choices_to_string(obj)

    def get_admin_area_title(self, obj: Household) -> str:
        if obj.admin_area:
            return f"{obj.admin_area.name} - {obj.admin_area.p_code}"
        return ""

    def get_active_individuals_count(self, obj: Household) -> int:
        return obj.active_individuals.count()

    def get_geopoint(self, obj: Household) -> tuple[float, float]:
        return obj.geopoint.x, obj.geopoint.y

    def get_import_id(self, obj: Household) -> str:
        if obj.detail_id:
            return f"{obj.unicef_id} (Detail id {obj.detail_id})"
        if obj.enumerator_rec_id:
            return f"{obj.unicef_id} (Enumerator ID {obj.enumerator_rec_id})"
        return obj.unicef_id
