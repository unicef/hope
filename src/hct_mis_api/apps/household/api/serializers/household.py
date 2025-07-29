from typing import Any

from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from hct_mis_api.apps.core.api.mixins import AdminUrlSerializerMixin
from hct_mis_api.apps.core.utils import (
    resolve_flex_fields_choices_to_string,
    to_choice_object,
)
from hct_mis_api.apps.geo.api.serializers import AreaSimpleSerializer
from hct_mis_api.apps.grievance.models import GrievanceTicket
from hct_mis_api.apps.household.api.serializers.registration_data_import import (
    RegistrationDataImportSerializer,
)
from hct_mis_api.apps.household.models import (
    AGENCY_TYPE_CHOICES,
    DEDUPLICATION_BATCH_STATUS_CHOICE,
    DEDUPLICATION_GOLDEN_RECORD_STATUS_CHOICE,
    DUPLICATE,
    INDIVIDUAL_FLAGS_CHOICES,
    INDIVIDUAL_STATUS_CHOICES,
    MARITAL_STATUS_CHOICE,
    OBSERVED_DISABILITY_CHOICE,
    RELATIONSHIP_CHOICE,
    RESIDENCE_STATUS_CHOICE,
    ROLE_CHOICE,
    ROLE_NO_ROLE,
    SEVERITY_OF_DISABILITY_CHOICES,
    SEX_CHOICE,
    WORK_STATUS_CHOICE,
    DocumentType,
    Household,
    Individual,
)
from hct_mis_api.apps.household.services.household_programs_with_delivered_quantity import (
    delivered_quantity_service,
)
from hct_mis_api.apps.payment.models import AccountType, FinancialInstitution
from hct_mis_api.apps.program.api.serializers import ProgramSmallSerializer


class DeliveredQuantitySerializer(serializers.Serializer):
    currency = serializers.CharField()
    total_delivered_quantity = serializers.DecimalField(max_digits=64, decimal_places=2)


class HouseholdListSerializer(serializers.ModelSerializer):
    head_of_household = serializers.CharField(source="head_of_household.full_name")
    admin1 = AreaSimpleSerializer()
    admin2 = AreaSimpleSerializer()
    total_cash_received = serializers.DecimalField(max_digits=64, decimal_places=2)
    total_cash_received_usd = serializers.DecimalField(max_digits=64, decimal_places=2)
    has_duplicates = serializers.SerializerMethodField()
    program = ProgramSmallSerializer()

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
            "first_registration_date",
            "currency",
            "has_duplicates",
            "sanction_list_possible_match",
            "sanction_list_confirmed_match",
        ]

    def get_has_duplicates(self, obj: Household) -> bool:
        return obj.individuals.filter(deduplication_golden_record_status=DUPLICATE).exists()


class HeadOfHouseholdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Individual
        fields = (
            "id",
            "full_name",
        )


class HouseholdSimpleSerializer(serializers.ModelSerializer):
    admin1 = AreaSimpleSerializer()
    admin2 = AreaSimpleSerializer()
    admin3 = AreaSimpleSerializer()
    admin4 = AreaSimpleSerializer()
    country = serializers.CharField(source="country.name", default="")
    country_origin = serializers.CharField(source="country_origin.name", default="")
    total_cash_received = serializers.DecimalField(max_digits=64, decimal_places=2)
    total_cash_received_usd = serializers.DecimalField(max_digits=64, decimal_places=2)
    delivered_quantities = serializers.SerializerMethodField()
    import_id = serializers.SerializerMethodField()

    class Meta:
        model = Household
        fields = (
            "id",
            "unicef_id",
            "admin1",
            "admin2",
            "admin3",
            "admin4",
            "first_registration_date",
            "last_registration_date",
            "total_cash_received",
            "total_cash_received_usd",
            "delivered_quantities",
            "start",
            "zip_code",
            "residence_status",
            "country_origin",
            "country",
            "address",
            "village",
            "geopoint",
            "import_id",
        )

    @extend_schema_field(DeliveredQuantitySerializer(many=True))
    def get_delivered_quantities(self, obj: Household) -> dict:
        return DeliveredQuantitySerializer(delivered_quantity_service(obj), many=True).data

    def get_import_id(self, obj: Household) -> str:
        if obj.detail_id:
            return f"{obj.unicef_id} (Detail id {obj.detail_id})"
        if obj.enumerator_rec_id:
            return f"{obj.unicef_id} (Enumerator ID {obj.enumerator_rec_id})"
        return obj.unicef_id


class HouseholdMemberSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    household = HouseholdSimpleSerializer()

    class Meta:
        model = Individual
        fields = (
            "id",
            "unicef_id",
            "full_name",
            "role",
            "relationship",
            "status",
            "birth_date",
            "sex",
            "household",
        )

    def get_role(self, obj: Individual) -> str:
        role = obj.households_and_roles(manager="all_merge_status_objects").first()
        if role:
            return role.role
        return ROLE_NO_ROLE


class RecipientSerializer(serializers.ModelSerializer):
    head_of_household = HeadOfHouseholdSerializer()
    admin2 = AreaSimpleSerializer()
    residence_status = serializers.CharField(source="get_residence_status_display")


    class Meta:
        model = Household
        fields = (
            "id",
            "unicef_id",
            "size",
            "head_of_household",
            "admin2",
            "status",
            "residence_status",
            "last_registration_date",
        )


class LinkedGrievanceTicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = GrievanceTicket
        fields = (
            "id",
            "category",
            "status",
        )


class HouseholdDetailSerializer(AdminUrlSerializerMixin, serializers.ModelSerializer):
    head_of_household = HeadOfHouseholdSerializer()
    admin1 = AreaSimpleSerializer()
    admin2 = AreaSimpleSerializer()
    admin3 = AreaSimpleSerializer()
    admin4 = AreaSimpleSerializer()
    program = serializers.CharField(source="program.name")
    country = serializers.CharField(source="country.name", default="")
    country_origin = serializers.CharField(source="country_origin.name", default="")
    total_cash_received = serializers.DecimalField(max_digits=64, decimal_places=2)
    total_cash_received_usd = serializers.DecimalField(max_digits=64, decimal_places=2)
    has_duplicates = serializers.SerializerMethodField()
    registration_data_import = RegistrationDataImportSerializer()
    flex_fields = serializers.SerializerMethodField()
    linked_grievances = serializers.SerializerMethodField()
    admin_area_title = serializers.SerializerMethodField()
    active_individuals_count = serializers.SerializerMethodField()
    import_id = serializers.SerializerMethodField()
    delivered_quantities = serializers.SerializerMethodField()

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
            "linked_grievances",
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
            "other_sex_group_count",
            "start",
            "deviceid",
            "fchild_hoh",
            "child_hoh",
            "returnee",
            "size",
            "residence_status",
            "program_registration_id",
            "delivered_quantities",
            # for grievance table
            "consent",
            "name_enumerator",
            "org_enumerator",
            "org_name_enumerator",
            "registration_method",
            "consent_sharing",
        )

    def get_has_duplicates(self, obj: Household) -> bool:
        return obj.individuals.filter(deduplication_golden_record_status=DUPLICATE).exists()

    def get_flex_fields(self, obj: Household) -> dict:
        return resolve_flex_fields_choices_to_string(obj)

    def get_linked_grievances(self, obj: Individual) -> dict:
        return LinkedGrievanceTicketSerializer(
            GrievanceTicket.objects.filter(household_unicef_id=obj.unicef_id), many=True
        ).data

    def get_admin_area_title(self, obj: Household) -> str:
        if obj.admin_area:
            return f"{obj.admin_area.name} - {obj.admin_area.p_code}"
        return ""

    def get_active_individuals_count(self, obj: Household) -> int:
        return obj.active_individuals.count()

    def get_import_id(self, obj: Household) -> str:
        if obj.detail_id:
            return f"{obj.unicef_id} (Detail id {obj.detail_id})"
        if obj.enumerator_rec_id:
            return f"{obj.unicef_id} (Enumerator ID {obj.enumerator_rec_id})"
        return obj.unicef_id

    def get_delivered_quantities(self, obj: Household) -> dict:
        return DeliveredQuantitySerializer(delivered_quantity_service(obj), many=True).data


class HouseholdForTicketSerializer(serializers.ModelSerializer):
    admin1 = AreaSimpleSerializer()
    admin2 = AreaSimpleSerializer()
    country = serializers.CharField(source="country.name", default="")
    country_origin = serializers.CharField(source="country_origin.name", default="")
    head_of_household = HeadOfHouseholdSerializer()
    active_individuals_count = serializers.SerializerMethodField()

    class Meta:
        model = Household
        fields = (
            "id",
            "unicef_id",
            "unhcr_id",
            "village",
            "address",
            "admin1",
            "admin2",
            "country",
            "country_origin",
            "geopoint",
            "head_of_household",
            "residence_status",
            "size",
            "active_individuals_count",
        )

    def get_active_individuals_count(self, obj: Household) -> int:
        return obj.active_individuals.count()


class HouseholdChoicesSerializer(serializers.Serializer):
    document_type_choices = serializers.SerializerMethodField()
    residence_status_choices = serializers.SerializerMethodField()

    def get_document_type_choices(self, *args: Any, **kwargs: Any) -> list[dict[str, Any]]:
        return [{"name": x.label, "value": x.key} for x in DocumentType.objects.order_by("key")]

    def get_residence_status_choices(self, *args: Any, **kwargs: Any) -> list[dict[str, Any]]:
        return to_choice_object(RESIDENCE_STATUS_CHOICE)


class IndividualChoicesSerializer(serializers.Serializer):
    document_type_choices = serializers.SerializerMethodField()
    sex_choices = serializers.SerializerMethodField()
    flag_choices = serializers.SerializerMethodField()
    status_choices = serializers.SerializerMethodField()
    deduplication_batch_status_choices = serializers.SerializerMethodField()
    deduplication_golden_record_status_choices = serializers.SerializerMethodField()
    # choices for grievance tickets
    relationship_choices = serializers.SerializerMethodField()
    role_choices = serializers.SerializerMethodField()
    marital_status_choices = serializers.SerializerMethodField()
    identity_type_choices = serializers.SerializerMethodField()
    observed_disability_choices = serializers.SerializerMethodField()
    severity_of_disability_choices = serializers.SerializerMethodField()
    work_status_choices = serializers.SerializerMethodField()
    account_type_choices = serializers.SerializerMethodField()
    account_financial_institution_choices = serializers.SerializerMethodField()

    def get_document_type_choices(self, *args: Any, **kwargs: Any) -> list[dict[str, Any]]:
        return [{"name": x.label, "value": x.key} for x in DocumentType.objects.order_by("key")]

    def get_sex_choices(self, *args: Any, **kwargs: Any) -> list[dict[str, Any]]:
        return to_choice_object(SEX_CHOICE)

    def get_flag_choices(self, *args: Any, **kwargs: Any) -> list[dict[str, Any]]:
        return to_choice_object(INDIVIDUAL_FLAGS_CHOICES)

    def get_status_choices(self, *args: Any, **kwargs: Any) -> list[dict[str, Any]]:
        return to_choice_object(INDIVIDUAL_STATUS_CHOICES)

    def get_deduplication_batch_status_choices(self, *args: Any, **kwargs: Any) -> list[dict[str, Any]]:
        return to_choice_object(DEDUPLICATION_BATCH_STATUS_CHOICE)

    def get_deduplication_golden_record_status_choices(self, *args: Any, **kwargs: Any) -> list[dict[str, Any]]:
        return to_choice_object(DEDUPLICATION_GOLDEN_RECORD_STATUS_CHOICE)

    def get_relationship_choices(self, *args: Any, **kwargs: Any) -> list[dict[str, Any]]:
        return to_choice_object(RELATIONSHIP_CHOICE)

    def get_role_choices(self, *args: Any, **kwargs: Any) -> list[dict[str, Any]]:
        return to_choice_object(ROLE_CHOICE)

    def get_marital_status_choices(self, *args: Any, **kwargs: Any) -> list[dict[str, Any]]:
        return to_choice_object(MARITAL_STATUS_CHOICE)

    def get_identity_type_choices(self, *args: Any, **kwargs: Any) -> list[dict[str, Any]]:
        return to_choice_object(AGENCY_TYPE_CHOICES)

    def get_observed_disability_choices(self, *args: Any, **kwargs: Any) -> list[dict[str, Any]]:
        return to_choice_object(OBSERVED_DISABILITY_CHOICE)

    def get_severity_of_disability_choices(self, *args: Any, **kwargs: Any) -> list[dict[str, Any]]:
        return to_choice_object(SEVERITY_OF_DISABILITY_CHOICES)

    def get_work_status_choices(self, *args: Any, **kwargs: Any) -> list[dict[str, Any]]:
        return to_choice_object(WORK_STATUS_CHOICE)

    def get_account_type_choices(self, *args: Any, **kwargs: Any) -> list[dict[str, Any]]:
        return [{"name": x.label, "value": x.key} for x in AccountType.objects.all()]

    def get_account_financial_institution_choices(self, *args: Any, **kwargs: Any) -> list[dict[str, Any]]:
        return [{"name": x.name, "value": x.id} for x in FinancialInstitution.objects.all()]


class HouseholdSmallSerializer(serializers.ModelSerializer):
    class Meta:
        model = Household
        fields = (
            "id",
            "unicef_id",
        )
