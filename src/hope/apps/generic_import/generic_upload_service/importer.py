from django.forms import modelform_factory

from hope.apps.household.models import Document, Household, Individual, IndividualIdentity
from hope.apps.payment.models import Account
from hope.apps.registration_data.models import RegistrationDataImport


class Importer:
    def __init__(
        self,
        registration_data_import: RegistrationDataImport,
        households_data,
        individuals_data,
        documents_data,
        accounts_data,
        identities_data,
    ):
        self.registration_data_import = registration_data_import
        self.households_data = households_data
        self.individuals_data = individuals_data
        self.documents_data = documents_data
        self.accounts_data = accounts_data
        self.identities_data = identities_data
        self.households_to_create = []
        self.individuals_to_create = []
        self.documents_to_create = []
        self.accounts_to_create = []
        self.identities_to_create = []
        self.errors = []

    def import_data(self):
        """Import all data types in sequence."""
        self._import_households()
        self._import_individuals()
        self._import_documents()
        self._import_accounts()
        self._import_identities()
        self._save_objects()
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
            self.errors.append({"type": "individual", "data": individual_data, "errors": errors})
        else:
            # Use UUID from parser as real DB ID
            if "id" in individual_data:
                individual_instance.id = individual_data["id"]
            # household_id will be used directly from parser data in _save_individuals
            if "household_id" in individual_data:
                individual_instance.household_id = individual_data["household_id"]
            self.individuals_to_create.append(individual_instance)

    def _import_household(self, household_data):
        exclude = [
            "household_collection",
            "head_of_household",
            "consent_sharing",
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
            self.errors.append({"type": "household", "data": household_data, "errors": errors})
        else:
            # Use UUID from parser as real DB ID
            if "id" in household_data:
                household_instance.id = household_data["id"]
            self.households_to_create.append(household_instance)

    def _import_document(self, document_data):
        exclude = ["individual"]

        document_instance, errors = self._build_unsaved_instance(
            model_cls=Document, data=document_data, exclude=exclude
        )
        if errors:
            self.errors.append({"type": "document", "data": document_data, "errors": errors})
        else:
            # individual_id will be used directly from parser data in _save_documents
            if "individual_id" in document_data:
                document_instance.individual_id = document_data["individual_id"]
            self.documents_to_create.append(document_instance)

    def _import_account(self, account_data):
        exclude = ["individual"]

        account_instance, errors = self._build_unsaved_instance(model_cls=Account, data=account_data, exclude=exclude)
        if errors:
            self.errors.append({"type": "account", "data": account_data, "errors": errors})
        else:
            # individual_id will be used directly from parser data in _save_accounts
            if "individual_id" in account_data:
                account_instance.individual_id = account_data["individual_id"]
            self.accounts_to_create.append(account_instance)

    def _import_identity(self, identity_data):
        exclude = ["individual", "partner"]

        identity_instance, errors = self._build_unsaved_instance(
            model_cls=IndividualIdentity, data=identity_data, exclude=exclude
        )
        if errors:
            self.errors.append({"type": "identity", "data": identity_data, "errors": errors})
        else:
            if "individual_id" in identity_data:
                identity_instance.individual_id = identity_data["individual_id"]
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
            if not hasattr(household, "first_registration_date") or not household.first_registration_date:
                household.first_registration_date = timezone.now()
            if not hasattr(household, "last_registration_date") or not household.last_registration_date:
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
            if not hasattr(individual, "first_registration_date") or not individual.first_registration_date:
                individual.first_registration_date = timezone.now()
            if not hasattr(individual, "last_registration_date") or not individual.last_registration_date:
                individual.last_registration_date = timezone.now()
        Individual.objects.bulk_create(self.individuals_to_create)

    def _save_documents(self):
        """Save documents with UUIDs from parser."""
        if not self.documents_to_create:
            return

        for document in self.documents_to_create:
            document.rdi_merge_status = Document.PENDING

        Document.objects.bulk_create(self.documents_to_create)

    def _save_accounts(self):
        if not self.accounts_to_create:
            return
        Account.objects.bulk_create(self.accounts_to_create)

    def _save_identities(self):
        if not self.identities_to_create:
            return

        for identity in self.identities_to_create:
            identity.rdi_merge_status = IndividualIdentity.PENDING

        IndividualIdentity.objects.bulk_create(self.identities_to_create)

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

        Form = modelform_factory(model_cls, exclude=list(set(exclude + common_exclude)))
        form = Form(data=data, files=files)
        try:
            if not form.is_valid():
                return None, form.errors
            return form.save(commit=False), None
        except (DjangoValidationError, AttributeError) as e:
            return None, {"non_field_errors": [str(e)]}
