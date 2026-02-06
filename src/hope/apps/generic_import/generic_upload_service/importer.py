from enum import StrEnum

from django.forms import modelform_factory

from hope.models import (
    Account,
    AccountType,
    Country,
    Document,
    DocumentType,
    FinancialInstitution,
    Household,
    Individual,
    IndividualIdentity,
    RegistrationDataImport,
)


class RecordType(StrEnum):
    HOUSEHOLD = "household"
    INDIVIDUAL = "individual"
    ACCOUNT = "account"
    DOCUMENT = "document"
    IDENTITY = "identity"


def format_validation_errors(errors: list) -> str:
    """Format validation errors in a human-readable way."""
    if not errors:
        return "No errors"

    formatted_lines = []

    for idx, error_item in enumerate(errors, 1):
        if not isinstance(error_item, dict):
            formatted_lines.append(f"{idx}. {str(error_item)}")
            continue

        error_type = error_item.get("type", "Unknown")
        data = error_item.get("data", {})
        field_errors = error_item.get("errors", {})

        # Get identifier for the record
        if error_type == RecordType.HOUSEHOLD:
            identifier = data.get("id", "Unknown")[:8]
            header = f"{idx}. Household (ID: {identifier}...)"
        elif error_type == RecordType.INDIVIDUAL:
            full_name = data.get("full_name", data.get("given_name", "Unknown"))
            header = f"{idx}. Individual ({full_name})"
        elif error_type == RecordType.ACCOUNT:
            number = data.get("number", "Unknown")
            header = f"{idx}. Account ({number})"
        else:
            header = f"{idx}. {error_type.title()}"

        formatted_lines.append(header)

        # Format field errors
        for field_name, error_messages in field_errors.items():
            if isinstance(error_messages, list):
                formatted_lines.extend([f"   • {field_name}: {msg}" for msg in error_messages])
            else:
                formatted_lines.append(f"   • {field_name}: {error_messages}")

    return "\n".join(formatted_lines)


class Importer:
    def __init__(
        self,
        registration_data_import: RegistrationDataImport,
        **kwargs,
    ):
        self.registration_data_import = registration_data_import
        self.households_data = kwargs.get("households_data", [])
        self.individuals_data = kwargs.get("individuals_data", [])
        self.documents_data = kwargs.get("documents_data", [])
        self.accounts_data = kwargs.get("accounts_data", [])
        self.identities_data = kwargs.get("identities_data", [])
        self.households_to_create = []
        self.individuals_to_create = []
        self.documents_to_create = []
        self.accounts_to_create = []
        self.identities_to_create = []
        self.errors = []

        # Cache AccountType lookups (key -> id mapping)
        self._account_types = {at.key: at.id for at in AccountType.objects.all()}

        # Cache DocumentType lookups (key -> id mapping)
        self._document_types = {dt.key: dt.id for dt in DocumentType.objects.all()}

        # Cache Country lookups (iso_code3 -> id mapping)
        self._countries = {c.iso_code3: c.id for c in Country.objects.all()}

        # Dictionary to store household instances by their parser ID (for FK linking)
        self._household_instances = {}

        # Dictionary to store individual instances by their parser ID (for FK linking)
        self._individual_instances = {}

    def import_data(self):
        """Import all data types in sequence."""
        self._import_households()
        self._import_individuals()
        self._import_documents()
        self._import_accounts()
        self._import_identities()
        self._save_objects()
        self._update_household_heads()
        return self.errors

    def _import_households(self):
        for household_data in self.households_data:
            self._import_household(household_data)

    def _import_individuals(self):
        for individual_data in self.individuals_data:
            self._import_individual(individual_data)

    def _import_documents(self):
        for document_data in self.documents_data:
            self._import_document(document_data)

    def _import_accounts(self):
        for account_data in self.accounts_data:
            self._import_account(account_data)

    def _import_identities(self):
        for identity_data in self.identities_data:
            self._import_identity(identity_data)

    def _import_individual(self, individual_data):
        exclude = [
            "individual_collection",
            "household",
            "first_registration_date",
            "last_registration_date",
            "deduplication_golden_record_status",
            "deduplication_batch_status",
            "biometric_deduplication_golden_record_status",
            "biometric_deduplication_batch_status",
            "vector_column",
            "marital_status",
            "disability",
            "observed_disability",
        ]

        individual_instance, errors = self._build_unsaved_instance(
            model_cls=Individual, data=individual_data, exclude=exclude
        )
        if errors:
            self.errors.append({"type": RecordType.INDIVIDUAL, "data": individual_data, "errors": errors})
        else:
            # Use UUID from parser as real DB ID
            if "id" in individual_data:
                individual_instance.id = individual_data["id"]
                # Store in dictionary for account/document/identity FK linking
                self._individual_instances[individual_data["id"]] = individual_instance
            # Link individual to household via object reference (not UUID)
            if household_id := individual_data.get("household_id"):
                if household_obj := self._household_instances.get(household_id):
                    individual_instance.household = household_obj
                else:
                    # Household not found - add error
                    self.errors.append(
                        {
                            "type": RecordType.INDIVIDUAL,
                            "data": individual_data,
                            "errors": {"household_id": [f"Household with id {household_id} not found"]},
                        }
                    )
                    return
            self.individuals_to_create.append(individual_instance)

    def _import_household(self, household_data):
        exclude = [
            "household_collection",
            "consent_sharing",
            "head_of_household",
            "first_registration_date",
            "last_registration_date",
            "kobo_submission_uuid",
            "org_enumerator",
            "collect_type",
            "registration_method",
            "currency",
            "representatives",
        ]

        household_instance, errors = self._build_unsaved_instance(
            model_cls=Household, data=household_data, exclude=exclude
        )
        if errors:
            self.errors.append({"type": RecordType.HOUSEHOLD, "data": household_data, "errors": errors})
        else:
            # Use UUID from parser as real DB ID
            if "id" in household_data:
                household_instance.id = household_data["id"]
                # Store in dictionary for individual FK linking
                self._household_instances[household_data["id"]] = household_instance
            self.households_to_create.append(household_instance)

    def _import_document(self, document_data):
        exclude = ["individual"]

        # Resolve type_key string to DocumentType ID if needed
        if (type_key := document_data.get("type_key")) and isinstance(type_key, str):
            if document_type_id := self._document_types.get(type_key):
                # Create a copy with resolved ID and remove type_key
                document_data = {**document_data, "type": document_type_id}
                document_data.pop("type_key", None)
            else:
                # Invalid document type key
                self.errors.append(
                    {
                        "type": RecordType.DOCUMENT,
                        "data": document_data,
                        "errors": {"type_key": [f"Unknown document type: {type_key}"]},
                    }
                )
                return

        # Resolve country ISO code to Country ID if needed
        if (country_code := document_data.get("country")) and isinstance(country_code, str):
            if country_id := self._countries.get(country_code):
                # Create a copy with resolved ID
                document_data = {**document_data, "country": country_id}
            else:
                # Invalid country code - set to None or add error
                self.errors.append(
                    {
                        "type": RecordType.DOCUMENT,
                        "data": document_data,
                        "errors": {"country": [f"Unknown country code: {country_code}"]},
                    }
                )
                return

        document_instance, errors = self._build_unsaved_instance(
            model_cls=Document, data=document_data, exclude=exclude
        )
        if errors:
            self.errors.append({"type": RecordType.DOCUMENT, "data": document_data, "errors": errors})
        else:
            # Link document to individual via object reference (not UUID)
            if individual_id := document_data.get("individual_id"):
                if individual_obj := self._individual_instances.get(individual_id):
                    document_instance.individual = individual_obj
                else:
                    self.errors.append(
                        {
                            "type": RecordType.DOCUMENT,
                            "data": document_data,
                            "errors": {"individual_id": [f"Individual with id {individual_id} not found"]},
                        }
                    )
                    return
            self.documents_to_create.append(document_instance)

    def _import_account(self, account_data):
        exclude = ["individual", "financial_institution"]
        account_type_key = None

        # Resolve account_type string key to database ID if needed
        if (account_type_val := account_data.get("account_type")) and isinstance(account_type_val, str):
            account_type_key = account_type_val
            if account_type_id := self._account_types.get(account_type_key):
                # Create a copy with resolved ID
                account_data = {**account_data, "account_type": account_type_id}
            else:
                # Invalid account_type key
                self.errors.append(
                    {
                        "type": RecordType.ACCOUNT,
                        "data": account_data,
                        "errors": {"account_type": [f"Unknown account type: {account_type_key}"]},
                    }
                )
                return

        account_instance, errors = self._build_unsaved_instance(model_cls=Account, data=account_data, exclude=exclude)
        if errors:
            self.errors.append({"type": RecordType.ACCOUNT, "data": account_data, "errors": errors})
        else:
            # Link account to individual via object reference (not UUID)
            if individual_id := account_data.get("individual_id"):
                if individual_obj := self._individual_instances.get(individual_id):
                    account_instance.individual = individual_obj
                else:
                    self.errors.append(
                        {
                            "type": RecordType.ACCOUNT,
                            "data": account_data,
                            "errors": {"individual_id": [f"Individual with id {individual_id} not found"]},
                        }
                    )
                    return

            # Assign generic Financial Institution if not provided
            if not account_data.get("financial_institution"):
                if account_type_key is None:
                    # account_type was passed as ID, get the key from AccountType
                    account_type_obj = AccountType.objects.filter(id=account_data.get("account_type")).first()
                    account_type_key = account_type_obj.key if account_type_obj else "mobile"
                account_instance.financial_institution = FinancialInstitution.get_generic_one(
                    account_type_key, is_valid_iban=False
                )

            self.accounts_to_create.append(account_instance)

    def _import_identity(self, identity_data):
        exclude = ["individual", "partner"]

        identity_instance, errors = self._build_unsaved_instance(
            model_cls=IndividualIdentity, data=identity_data, exclude=exclude
        )
        if errors:
            self.errors.append({"type": RecordType.IDENTITY, "data": identity_data, "errors": errors})
        else:
            # Link identity to individual via object reference (not UUID)
            if individual_id := identity_data.get("individual_id"):
                if individual_obj := self._individual_instances.get(individual_id):
                    identity_instance.individual = individual_obj
                else:
                    self.errors.append(
                        {
                            "type": RecordType.IDENTITY,
                            "data": identity_data,
                            "errors": {"individual_id": [f"Individual with id {individual_id} not found"]},
                        }
                    )
                    return
            self.identities_to_create.append(identity_instance)

    def _save_objects(self):
        """Save all objects to database in correct order with proper relationships."""
        self._save_households()
        self._save_individuals()
        self._save_documents()
        self._save_accounts()
        self._save_identities()

    def _save_households(self):
        """Save households with UUIDs from parser as DB IDs."""
        from django.utils import timezone

        if not self.households_to_create:
            return

        for household in self.households_to_create:
            household.business_area = self.registration_data_import.business_area
            household.program = self.registration_data_import.program
            household.registration_data_import = self.registration_data_import
            household.rdi_merge_status = Household.PENDING
            household.is_removed = False
            if not getattr(household, "first_registration_date", None):
                household.first_registration_date = timezone.now()
            if not getattr(household, "last_registration_date", None):
                household.last_registration_date = timezone.now()

        # Bulk create - UUID from parser will be used as DB ID
        Household.objects.bulk_create(self.households_to_create)

    def _save_individuals(self):
        """Save individuals with UUIDs from parser as DB IDs."""
        from django.utils import timezone

        if not self.individuals_to_create:
            return
        for individual in self.individuals_to_create:
            individual.business_area = self.registration_data_import.business_area
            individual.program = self.registration_data_import.program
            individual.registration_data_import = self.registration_data_import
            individual.rdi_merge_status = Individual.PENDING
            individual.is_removed = False
            if not getattr(individual, "first_registration_date", None):
                individual.first_registration_date = timezone.now()
            if not getattr(individual, "last_registration_date", None):
                individual.last_registration_date = timezone.now()
        Individual.objects.bulk_create(self.individuals_to_create)

    def _save_documents(self):
        """Save documents with UUIDs from parser."""
        if not self.documents_to_create:
            return

        for document in self.documents_to_create:
            document.rdi_merge_status = Document.PENDING
            document.is_removed = False

        Document.objects.bulk_create(self.documents_to_create)

    def _save_accounts(self):
        if not self.accounts_to_create:
            return
        for acc in self.accounts_to_create:
            # Set merge status and is_removed like we do for other models
            acc.rdi_merge_status = Account.PENDING
            acc.is_removed = False
        Account.objects.bulk_create(self.accounts_to_create)

    def _save_identities(self):
        if not self.identities_to_create:
            return

        for identity in self.identities_to_create:
            identity.rdi_merge_status = IndividualIdentity.PENDING
            identity.is_removed = False

        IndividualIdentity.objects.bulk_create(self.identities_to_create)

    def _update_household_heads(self):
        """Update household head_of_household FKs after individuals are saved."""
        for household_data in self.households_data:
            if "head_of_household_id" in household_data and "id" in household_data:
                household_id = household_data["id"]
                head_id = household_data["head_of_household_id"]

                # Use all_merge_status_objects to include PENDING households (not just MERGED)
                Household.all_merge_status_objects.filter(id=household_id).update(head_of_household_id=head_id)

    def _build_unsaved_instance(self, model_cls, data, files=None, exclude=None):
        from django.core.exceptions import ValidationError as DjangoValidationError

        if exclude is None:
            exclude = []

        # Exclude fields that will be set later in _save_* methods
        common_exclude = [
            "business_area",
            "program",
            "registration_data_import",
            "rdi_merge_status",
            "created_at",
            "updated_at",
            "is_removed",
            "removed_date",
        ]

        form_class = modelform_factory(model_cls, exclude=list(set(exclude + common_exclude)))
        form = form_class(data=data, files=files)
        try:
            if not form.is_valid():
                return None, form.errors
            return form.save(commit=False), None
        except (DjangoValidationError, AttributeError) as e:
            return None, {"non_field_errors": [str(e)]}
