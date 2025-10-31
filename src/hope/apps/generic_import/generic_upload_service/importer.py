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
        individual_instance, errors = self._build_unsaved_instance(model_cls=Individual, data=individual_data)
        if errors:
            self.errors.append({"type": "individual", "data": individual_data, "errors": errors})
        else:
            self.individuals_to_create.append(individual_instance)

    def _import_household(self, household_data):
        household_instance, errors = self._build_unsaved_instance(model_cls=Household, data=household_data)
        if errors:
            self.errors.append({"type": "household", "data": household_data, "errors": errors})
        else:
            self.households_to_create.append(household_instance)

    def _import_document(self, document_data):
        document_instance, errors = self._build_unsaved_instance(model_cls=Document, data=document_data)
        if errors:
            self.errors.append({"type": "document", "data": document_data, "errors": errors})
        else:
            self.documents_to_create.append(document_instance)

    def _import_account(self, account_data):
        account_instance, errors = self._build_unsaved_instance(model_cls=Account, data=account_data)
        if errors:
            self.errors.append({"type": "account", "data": account_data, "errors": errors})
        else:
            self.accounts_to_create.append(account_instance)

    def _import_identity(self, identity_data):
        identity_instance, errors = self._build_unsaved_instance(model_cls=IndividualIdentity, data=identity_data)
        if errors:
            self.errors.append({"type": "identity", "data": identity_data, "errors": errors})
        else:
            self.identities_to_create.append(identity_instance)

    def _build_unsaved_instance(self, model_cls, data, files=None):
        from django.core.exceptions import ValidationError as DjangoValidationError

        # Use exclude=[] to include all fields; fields with default + blank=True won't be required
        Form = modelform_factory(model_cls, exclude=[])
        form = Form(data=data, files=files)
        try:
            if not form.is_valid():
                return None, form.errors
            return form.save(commit=False), None
        except (DjangoValidationError, AttributeError) as e:
            return None, {"non_field_errors": [str(e)]}
