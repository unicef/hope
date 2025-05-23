import uuid
from datetime import date
from typing import Dict, Optional

from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from rest_framework.utils.serializer_helpers import ReturnDict

from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.utils import (
    decode_id_string,
    resolve_flex_fields_choices_to_string,
)
from hct_mis_api.apps.geo.api.serializers import AreaSimpleSerializer
from hct_mis_api.apps.geo.models import Country
from hct_mis_api.apps.grievance.models import GrievanceTicket
from hct_mis_api.apps.household.api.serializers.registration_data_import import (
    RegistrationDataImportSerializer,
)
from hct_mis_api.apps.household.models import (
    DUPLICATE,
    DUPLICATE_IN_BATCH,
    ROLE_NO_ROLE,
    BankAccountInfo,
    Document,
    DocumentType,
    Household,
    Individual,
    IndividualIdentity,
    IndividualRoleInHousehold,
)
from hct_mis_api.apps.payment.models import Account


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


class IndividualSmallSerializer(serializers.ModelSerializer):
    class Meta:
        model = Individual
        fields = (
            "id",
            "unicef_id",
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


class AccountSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    individual_tab_data = serializers.SerializerMethodField()

    class Meta:
        model = Account
        fields = (
            "id",
            "name",
            "individual_tab_data",
        )

    def get_name(self, obj: Account) -> str:
        return obj.account_type.label

    def get_individual_tab_data(self, obj: Account) -> Dict:
        return dict(sorted(obj.data.items()))


class HouseholdSimpleSerializer(serializers.ModelSerializer):
    admin2 = AreaSimpleSerializer()

    class Meta:
        model = Household
        fields = (
            "id",
            "unicef_id",
            "admin2",
        )


class IndividualSimpleSerializer(serializers.ModelSerializer):
    household = HouseholdSimpleSerializer()
    roles_in_households = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()
    documents = serializers.SerializerMethodField()

    class Meta:
        model = Individual
        fields = (
            "id",
            "unicef_id",
            "full_name",
            "household",
            "roles_in_households",
            "relationship",
            "role",
            "documents",
        )

    def get_roles_in_households(self, obj: Individual) -> Dict:
        return IndividualRoleInHouseholdSerializer(
            obj.households_and_roles(manager="all_merge_status_objects"), many=True
        ).data

    def get_role(self, obj: Individual) -> str:
        role = obj.households_and_roles(manager="all_objects").filter(household=obj.household).first()
        if role:
            return role.get_role_display()
        return "-"

    def get_documents(self, obj: Individual) -> Dict:
        return DocumentSerializer(obj.documents(manager="all_merge_status_objects").all(), many=True).data


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


class DeduplicationResultSerializer(serializers.Serializer):
    unicef_id = serializers.SerializerMethodField()
    hit_id = serializers.CharField(required=False)
    full_name = serializers.CharField(required=False)
    score = serializers.FloatField(required=False)
    proximity_to_score = serializers.FloatField(required=False)
    location = serializers.SerializerMethodField()
    age = serializers.SerializerMethodField()
    duplicate = serializers.SerializerMethodField()
    distinct = serializers.SerializerMethodField()

    def get_unicef_id(self, obj: dict) -> str:
        hit_id = obj.get("hit_id")
        # If hit_id is a valid UUID string, use it directly as the PK
        try:
            uuid.UUID(hit_id)
            pk = hit_id
        except (ValueError, TypeError):
            # otherwise decode the opaque ID
            pk = decode_id_string(hit_id)
        individual = Individual.all_objects.get(id=pk)
        return str(individual.unicef_id)

    def get_location(self, obj: dict) -> str:
        return obj.get("location", "Not provided")

    def get_age(self, obj: dict) -> Optional[int]:
        dob = obj.get("dob")
        if not dob:
            return None
        birth = parse(dob)
        return relativedelta(date.today(), birth).years

    def get_duplicate(self, obj: dict) -> bool:
        return bool(obj.get("duplicate", False))

    def get_distinct(self, obj: dict) -> bool:
        return bool(obj.get("distinct", False))


class DeduplicationEngineSimilarityPairIndividualSerializer(serializers.Serializer):
    id = serializers.CharField()
    photo = serializers.SerializerMethodField()
    full_name = serializers.CharField()
    unicef_id = serializers.CharField()
    similarity_score = serializers.FloatField()
    age = serializers.IntegerField()
    location = serializers.CharField()

    def get_photo(self, obj: dict) -> str:
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

    @extend_schema_field(DeduplicationResultSerializer(many=True))
    def get_deduplication_batch_results(self, obj: Individual) -> ReturnDict:
        key = "duplicates" if obj.deduplication_batch_status == DUPLICATE_IN_BATCH else "possible_duplicates"
        results = obj.deduplication_batch_results.get(key, {})
        serializer = DeduplicationResultSerializer(results, many=True, context=self.context)
        return serializer.data

    @extend_schema_field(DeduplicationEngineSimilarityPairIndividualSerializer(many=True))
    def get_biometric_deduplication_batch_results(self, obj: Individual) -> ReturnDict:
        results = obj.biometric_deduplication_batch_results
        serializer = DeduplicationEngineSimilarityPairIndividualSerializer(results, many=True, context=self.context)
        return serializer.data

    @extend_schema_field(DeduplicationResultSerializer(many=True))
    def get_deduplication_golden_record_results(self, obj: Individual) -> ReturnDict:
        key = "duplicates" if obj.deduplication_golden_record_status == DUPLICATE else "possible_duplicates"
        results = obj.deduplication_golden_record_results.get(key, {})
        serializer = DeduplicationResultSerializer(results, many=True, context=self.context)
        return serializer.data

    @extend_schema_field(DeduplicationEngineSimilarityPairIndividualSerializer(many=True))
    def get_biometric_deduplication_golden_record_results(self, obj: Individual) -> ReturnDict:
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
    accounts = serializers.SerializerMethodField()
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
            "accounts",
            "email",
            "phone_no",
            "phone_no_valid",
            "phone_no_alternative",
            "phone_no_alternative_valid",
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

    def get_accounts(self, obj: Individual) -> Dict:
        if self.context["request"].user.has_perm(
            Permissions.POPULATION_VIEW_INDIVIDUAL_DELIVERY_MECHANISMS_SECTION.value, obj.program
        ):
            queryset = obj.accounts(manager="all_objects").all()
        else:
            queryset = obj.accounts.none()
        return AccountSerializer(queryset, many=True).data

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


class IndividualForTicketSerializer(serializers.ModelSerializer):
    household = HouseholdSimpleSerializer()
    deduplication_golden_record_results = serializers.SerializerMethodField()
    documents = serializers.SerializerMethodField()

    class Meta:
        model = Individual
        fields = (
            "id",
            "unicef_id",
            "household",
            "full_name",
            "birth_date",
            "last_registration_date",
            "sex",
            "deduplication_golden_record_results",
            "duplicate",
            "documents",
        )

    @extend_schema_field(DeduplicationResultSerializer(many=True))
    def get_deduplication_golden_record_results(self, obj: Individual) -> ReturnDict:
        key = "duplicates" if obj.deduplication_golden_record_status == DUPLICATE else "possible_duplicates"
        results = obj.deduplication_golden_record_results.get(key, {})
        serializer = DeduplicationResultSerializer(results, many=True, context=self.context)
        return serializer.data

    @extend_schema_field(DocumentSerializer(many=True))
    def get_documents(self, obj: Individual) -> Dict:
        return DocumentSerializer(obj.documents(manager="all_merge_status_objects").all(), many=True).data
