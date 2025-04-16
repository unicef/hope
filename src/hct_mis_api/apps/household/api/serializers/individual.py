from typing import Dict

from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.utils import resolve_flex_fields_choices_to_string
from hct_mis_api.apps.geo.models import Country
from hct_mis_api.apps.grievance.models import GrievanceTicket
from hct_mis_api.apps.household.api.serializers.registration_data_import import (
    RegistrationDataImportSerializer,
)
from hct_mis_api.apps.household.models import (
    ROLE_NO_ROLE,
    BankAccountInfo,
    Document,
    DocumentType,
    Household,
    Individual,
    IndividualIdentity,
    IndividualRoleInHousehold,
)
from hct_mis_api.apps.payment.models import DeliveryMechanismData


class DocumentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentType
        fields = (
            "id",
            "label",
            "key",
        )


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = (
            "id",
            "name",
            "iso_code3",
        )


class DocumentSerializer(serializers.ModelSerializer):
    type = DocumentTypeSerializer()
    country = CountrySerializer()

    class Meta:
        model = Document
        fields = (
            "id",
            "type",
            "country",
            "document_number",
        )


class IndividualIdentitySerializer(serializers.ModelSerializer):
    country = CountrySerializer()

    class Meta:
        model = IndividualIdentity
        fields = (
            "id",
            "country",
            "number",
        )


class BankAccountInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankAccountInfo
        fields = (
            "id",
            "bank_name",
            "bank_account_number",
            "account_holder_name",
            "bank_branch_name",
        )


class DeliveryMechanismDataSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    individual_tab_data = serializers.SerializerMethodField()

    class Meta:
        model = DeliveryMechanismData
        fields = (
            "id",
            "name",
            "individual_tab_data",
        )

    def get_name(self, obj: DeliveryMechanismData) -> str:
        return obj.account_type.label

    def get_individual_tab_data(self, obj: DeliveryMechanismData) -> Dict:
        return dict(sorted(obj.data.items()))


class HouseholdSimpleSerializer(serializers.ModelSerializer):
    admin2 = serializers.CharField(source="admin2.name", default="")

    class Meta:
        model = Household
        fields = (
            "id",
            "unicef_id",
            "admin2",
        )


class IndividualRoleInHouseholdSerializer(serializers.ModelSerializer):
    household = HouseholdSimpleSerializer()

    class Meta:
        model = IndividualRoleInHousehold
        fields = (
            "id",
            "household",
            "role",
        )


class LinkedGrievanceTicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = GrievanceTicket
        fields = (
            "id",
            "category",
            "status",
        )


class DeduplicationEngineSimilarityPairIndividualSerializer(serializers.Serializer):
    id = serializers.CharField()
    photo = serializers.SerializerMethodField()
    full_name = serializers.CharField()
    unicef_id = serializers.CharField()
    similarity_score = serializers.FloatField(required=False, allow_null=True)
    age = serializers.IntegerField(required=False, allow_null=True)
    location = serializers.CharField(required=False, allow_blank=True)

    def get_photo(self, obj):
        """
        Retrieve the photo URL from the Individual instance.
        Assumes `obj` is a dict-like object with an 'id' key.
        """
        individual = Individual.all_objects.filter(id=obj.get("id")).first()
        return individual.photo.url if individual and individual.photo else None


class IndividualListSerializer(serializers.ModelSerializer):
    household = HouseholdSimpleSerializer()
    relationship_display = serializers.CharField(source="get_relationship_display")
    role = serializers.SerializerMethodField()
    deduplication_batch_status_display = serializers.CharField(source="get_deduplication_batch_status_display")
    biometric_deduplication_batch_status_display = serializers.CharField(
        source="get_biometric_deduplication_batch_status_display"
    )

    deduplication_batch_results = serializers.SerializerMethodField()
    biometric_deduplication_batch_results = serializers.SerializerMethodField()

    deduplication_golden_record_status_display = serializers.CharField(
        source="get_deduplication_golden_record_status_display"
    )
    biometric_deduplication_golden_record_status_display = serializers.CharField(
        source="get_biometric_deduplication_golden_record_status_display"
    )

    deduplication_golden_record_results = serializers.SerializerMethodField()
    biometric_deduplication_golden_record_results = serializers.SerializerMethodField()

    class Meta:
        model = Individual
        fields = (
            "id",
            "unicef_id",
            "full_name",
            "household",
            "status",
            "relationship",
            "age",
            "sex",
            "role",
            "relationship_display",
            "birth_date",
            "deduplication_batch_status",
            "deduplication_batch_status_display",
            "biometric_deduplication_batch_status",
            "biometric_deduplication_batch_status_display",
            "deduplication_batch_results",
            "biometric_deduplication_batch_results",
            "deduplication_golden_record_status",
            "deduplication_golden_record_status_display",
            "biometric_deduplication_golden_record_status",
            "biometric_deduplication_golden_record_status_display",
            "deduplication_golden_record_results",
            "biometric_deduplication_golden_record_results",
        )

    def get_role(self, obj: Individual) -> str:
        role = obj.households_and_roles(manager="all_objects").filter(household=obj.household).first()
        if role:
            return role.get_role_display()
        return "-"

    @extend_schema_field(DeduplicationEngineSimilarityPairIndividualSerializer(many=True))
    def get_deduplication_batch_results(self, obj: Individual):
        results = obj.deduplication_batch_results
        serializer = DeduplicationEngineSimilarityPairIndividualSerializer(results, many=True, context=self.context)
        return serializer.data

    @extend_schema_field(DeduplicationEngineSimilarityPairIndividualSerializer(many=True))
    def get_biometric_deduplication_batch_results(self, obj: Individual):
        results = obj.biometric_deduplication_batch_results
        serializer = DeduplicationEngineSimilarityPairIndividualSerializer(results, many=True, context=self.context)
        return serializer.data

    @extend_schema_field(DeduplicationEngineSimilarityPairIndividualSerializer(many=True))
    def get_deduplication_golden_record_results(self, obj: Individual):
        results = obj.deduplication_golden_record_results
        serializer = DeduplicationEngineSimilarityPairIndividualSerializer(results, many=True, context=self.context)
        return serializer.data

    @extend_schema_field(DeduplicationEngineSimilarityPairIndividualSerializer(many=True))
    def get_biometric_deduplication_golden_record_results(self, obj: Individual):
        results = obj.biometric_deduplication_golden_record_results
        serializer = DeduplicationEngineSimilarityPairIndividualSerializer(results, many=True, context=self.context)
        return serializer.data


class IndividualDetailSerializer(serializers.ModelSerializer):
    household = HouseholdSimpleSerializer()
    role = serializers.SerializerMethodField()
    registration_data_import = RegistrationDataImportSerializer()
    import_id = serializers.SerializerMethodField()
    documents = serializers.SerializerMethodField()
    identities = serializers.SerializerMethodField()
    bank_account_info = serializers.SerializerMethodField()
    delivery_mechanisms_data = serializers.SerializerMethodField()
    roles_in_households = serializers.SerializerMethodField()
    flex_fields = serializers.SerializerMethodField()
    linked_grievances = serializers.SerializerMethodField()

    class Meta:
        model = Individual
        fields = (
            "id",
            "unicef_id",
            "full_name",
            "given_name",
            "middle_name",
            "family_name",
            "sex",
            "age",
            "birth_date",
            "estimated_birth_date",
            "marital_status",
            "work_status",
            "pregnant",
            "household",
            "role",
            "relationship",
            "registration_data_import",
            "import_id",
            "preferred_language",
            "roles_in_households",
            "observed_disability",
            "seeing_disability",
            "hearing_disability",
            "physical_disability",
            "memory_disability",
            "selfcare_disability",
            "comms_disability",
            "disability",
            "documents",
            "identities",
            "bank_account_info",
            "delivery_mechanisms_data",
            "email",
            "phone_no",
            "phone_no_alternative",
            "sanction_list_last_check",
            "wallet_name",
            "blockchain_name",
            "wallet_address",
            "status",
            "flex_fields",
            "linked_grievances",
        )

    def get_role(self, obj: Individual) -> str:
        role = obj.households_and_roles(manager="all_merge_status_objects").order_by("created_at").first()
        if role:
            return role.role
        return ROLE_NO_ROLE

    def get_documents(self, obj: Individual) -> Dict:
        return DocumentSerializer(obj.documents(manager="all_merge_status_objects").all(), many=True).data

    def get_identities(self, obj: Individual) -> Dict:
        return IndividualIdentitySerializer(obj.identities(manager="all_merge_status_objects").all(), many=True).data

    def get_bank_account_info(self, obj: Individual) -> Dict:
        return BankAccountInfoSerializer(
            obj.bank_account_info(manager="all_merge_status_objects").all(), many=True
        ).data

    def get_delivery_mechanisms_data(self, obj: Individual) -> Dict:
        if self.context["request"].user.has_perm(
            Permissions.POPULATION_VIEW_INDIVIDUAL_DELIVERY_MECHANISMS_SECTION.value, obj.program
        ):
            queryset = obj.delivery_mechanisms_data(manager="all_objects").all()
        else:
            queryset = obj.delivery_mechanisms_data.none()
        return DeliveryMechanismDataSerializer(queryset, many=True).data

    def get_flex_fields(self, obj: Individual) -> Dict:
        return resolve_flex_fields_choices_to_string(obj)

    def get_roles_in_households(self, obj: Individual) -> Dict:
        return IndividualRoleInHouseholdSerializer(
            obj.households_and_roles(manager="all_merge_status_objects"), many=True
        ).data

    def get_linked_grievances(self, obj: Individual) -> Dict:
        if obj.household:
            queryset = GrievanceTicket.objects.filter(household_unicef_id=obj.household.unicef_id)
        else:
            queryset = GrievanceTicket.objects.none()
        return LinkedGrievanceTicketSerializer(queryset, many=True).data

    def get_import_id(self, obj: Individual) -> str:
        return f"{obj.unicef_id} (Detail ID {obj.detail_id})" if obj.detail_id else obj.unicef_id
