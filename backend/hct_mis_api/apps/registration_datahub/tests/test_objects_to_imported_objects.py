from hct_mis_api.apps.account.fixtures import PartnerFactory
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.geo.fixtures import AreaFactory, CountryFactory
from hct_mis_api.apps.household.fixtures import (
    BankAccountInfoFactory,
    DocumentFactory,
    DocumentTypeFactory,
    HouseholdCollectionFactory,
    IndividualCollectionFactory,
    IndividualIdentityFactory,
    IndividualRoleInHouseholdFactory,
    create_household_and_individuals,
)
from hct_mis_api.apps.household.models import HEAD, MALE, ROLE_PRIMARY
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.registration_data.fixtures import RegistrationDataImportFactory
from hct_mis_api.apps.registration_datahub.fixtures import (
    ImportedDocumentTypeFactory,
    RegistrationDataImportDatahubFactory,
)
from hct_mis_api.apps.registration_datahub.models import (
    ImportedBankAccountInfo,
    ImportedDocument,
    ImportedHousehold,
    ImportedIndividual,
    ImportedIndividualIdentity,
    ImportedIndividualRoleInHousehold,
)
from hct_mis_api.apps.registration_datahub.tasks.objects_to_imported_objects import (
    CreateImportedObjectsFromObjectsTask,
)


class TestCreateImportedObjectsFromObjectsTask(APITestCase):
    databases = {"default", "registration_datahub"}

    @classmethod
    def setUpTestData(cls) -> None:
        cls.afghanistan = create_afghanistan()
        country = CountryFactory()
        country_origin = CountryFactory(
            name="Poland",
            short_name="Poland",
            iso_code2="PL",
            iso_code3="POL",
            iso_num="0616",
        )
        cls.program_from = ProgramFactory(business_area=cls.afghanistan)
        cls.program_to = ProgramFactory(business_area=cls.afghanistan)
        cls.registration_data_import = RegistrationDataImportFactory(
            business_area=cls.afghanistan,
            program=cls.program_to,
        )
        cls.rdi_other = RegistrationDataImportFactory(
            business_area=cls.afghanistan,
            program=cls.program_from,
        )
        cls.registration_data_import_datahub = RegistrationDataImportDatahubFactory(
            business_area_slug=cls.afghanistan.slug,
            hct_id=cls.registration_data_import.id,
        )
        cls.registration_data_import.datahub_id = cls.registration_data_import_datahub.id
        cls.registration_data_import.save()

        cls.household, cls.individuals = create_household_and_individuals(
            household_data={
                "registration_data_import": cls.rdi_other,
                "program": cls.program_from,
                "admin_area": AreaFactory(),
                "admin1": AreaFactory(),
                "admin2": AreaFactory(),
                "admin3": AreaFactory(),
                "admin4": AreaFactory(),
                "registration_id": "1234567890",
                "flex_fields": {"enumerator_id": "123", "some": "thing"},
                "country": country,
                "country_origin": country_origin,
            },
            individuals_data=[
                {
                    "registration_data_import": cls.rdi_other,
                    "given_name": "Test",
                    "full_name": "Test Testowski",
                    "middle_name": "",
                    "family_name": "Testowski",
                    "phone_no": "123-123-123",
                    "phone_no_alternative": "",
                    "relationship": HEAD,
                    "sex": MALE,
                    "birth_date": "1955-09-07",
                },
                {},
            ],
        )
        cls.ind_role_in_hh = IndividualRoleInHouseholdFactory(
            household=cls.household,
            individual=cls.individuals[1],
            role=ROLE_PRIMARY,
        )
        document_type = DocumentTypeFactory(key="birth_certificate")
        ImportedDocumentTypeFactory(
            key=document_type.key,
        )
        cls.document = DocumentFactory(
            individual=cls.individuals[0],
            program=cls.program_from,
            type=document_type,
            country=country,
        )
        cls.identity = IndividualIdentityFactory(
            individual=cls.individuals[0],
            country=country,
            partner=PartnerFactory(),
        )

        cls.bank_account_info = BankAccountInfoFactory(
            individual=cls.individuals[0],
        )

    def _object_count_before_after(self) -> None:
        self.assertEqual(
            ImportedHousehold.objects.count(),
            0,
        )
        self.assertEqual(
            ImportedIndividual.objects.count(),
            0,
        )
        self.assertEqual(
            ImportedIndividualIdentity.objects.count(),
            0,
        )
        self.assertEqual(
            ImportedDocument.objects.count(),
            0,
        )
        self.assertEqual(
            ImportedBankAccountInfo.objects.count(),
            0,
        )
        self.assertEqual(
            ImportedIndividualRoleInHousehold.objects.count(),
            0,
        )

        CreateImportedObjectsFromObjectsTask().execute(
            self.registration_data_import.id,
            self.program_from.id,
        )

        self.assertEqual(
            ImportedHousehold.objects.count(),
            1,
        )
        self.assertEqual(
            ImportedIndividual.objects.count(),
            2,
        )
        self.assertEqual(
            ImportedIndividualIdentity.objects.count(),
            1,
        )
        self.assertEqual(
            ImportedDocument.objects.count(),
            1,
        )
        self.assertEqual(
            ImportedBankAccountInfo.objects.count(),
            1,
        )
        self.assertEqual(
            ImportedIndividualRoleInHousehold.objects.count(),
            1,
        )

    def test_create_imported_objects_from_objects(self) -> None:
        self._object_count_before_after()

        imported_household = ImportedHousehold.objects.first()
        for field in CreateImportedObjectsFromObjectsTask.HOUSEHOLD_FIELDS:
            imported_household_field = getattr(imported_household, field)
            household_field = getattr(self.household, field)
            if field == "consent_sharing":
                continue
            if field in ("country", "country_origin"):
                household_field = household_field.iso_code2
            self.assertEqual(
                imported_household_field,
                household_field,
            )
        for admin in ("admin_area", "admin1", "admin2", "admin3", "admin4"):
            self.assertEqual(
                getattr(imported_household, admin),
                getattr(self.household, admin).p_code,
            )

        self.assertEqual(
            self.household.registration_id,
            str(imported_household.flex_registrations_record.registration),
        )

        self.assertEqual(
            self.household.flex_fields["enumerator_id"],
            str(imported_household.enumerator_rec_id),
        )
        self.assertEqual(
            self.household.unicef_id,
            str(imported_household.mis_unicef_id),
        )

        imported_individuals = ImportedIndividual.objects.all()
        head_of_household_imported_individual = imported_individuals.get(relationship=HEAD)

        self.individuals[0].refresh_from_db()

        for field in CreateImportedObjectsFromObjectsTask.INDIVIDUAL_FIELDS:
            if field == "id":
                continue
            imported_individual_field = getattr(head_of_household_imported_individual, field)
            individual_field = getattr(self.individuals[0], field)
            self.assertEqual(
                imported_individual_field,
                individual_field,
            )

        self.assertEqual(
            head_of_household_imported_individual.phone_no_valid,
            self.individuals[0].phone_no_valid,
        )

        self.assertEqual(
            head_of_household_imported_individual.phone_no_alternative_valid,
            self.individuals[0].phone_no_alternative_valid,
        )

        self.assertEqual(
            head_of_household_imported_individual.mis_unicef_id,
            self.individuals[0].unicef_id,
        )

        self.assertEqual(
            head_of_household_imported_individual.relationship,
            HEAD,
        )

        self.assertEqual(
            imported_household.head_of_household,
            head_of_household_imported_individual,
        )

        imported_document = ImportedDocument.objects.first()
        for field in (
            "document_number",
            "photo",
            "expiry_date",
            "issuance_date",
        ):
            imported_document_field = getattr(imported_document, field)
            document_field = getattr(self.document, field)
            self.assertEqual(
                imported_document_field,
                document_field,
            )
        self.assertEqual(
            imported_document.type.key,
            self.document.type.key,
        )

        imported_identity = ImportedIndividualIdentity.objects.first()
        self.assertEqual(
            imported_identity.document_number,
            self.identity.number,
        )

        self.assertEqual(
            imported_identity.country,
            self.identity.country.iso_code2,
        )

        self.assertEqual(
            imported_identity.partner,
            self.identity.partner.name,
        )

        imported_bank_account_info = ImportedBankAccountInfo.objects.first()
        for field in (
            "bank_name",
            "bank_account_number",
            "debit_card_number",
            "bank_branch_name",
            "account_holder_name",
        ):
            imported_bank_account_info_field = getattr(imported_bank_account_info, field)
            bank_account_info_field = getattr(self.bank_account_info, field)
            self.assertEqual(
                imported_bank_account_info_field,
                bank_account_info_field,
            )

        imported_individual_role_in_household = ImportedIndividualRoleInHousehold.objects.first()
        self.assertEqual(
            imported_individual_role_in_household.household.mis_unicef_id,
            self.household.unicef_id,
        )
        self.assertEqual(
            imported_individual_role_in_household.individual.mis_unicef_id,
            self.individuals[1].unicef_id,
        )
        self.assertEqual(
            imported_individual_role_in_household.role,
            ROLE_PRIMARY,
        )

    def test_not_import_excluded_objects(self) -> None:
        household_withdrawn, individuals = create_household_and_individuals(
            household_data={
                "registration_data_import": self.rdi_other,
                "program": self.program_from,
                "withdrawn": True,
            },
            individuals_data=[
                {
                    "registration_data_import": self.rdi_other,
                    "withdrawn": True,
                },
                {
                    "registration_data_import": self.rdi_other,
                    "duplicate": True,
                },
            ],
        )
        household_already_in_program, individuals_already_in_program = create_household_and_individuals(
            household_data={
                "registration_data_import": self.rdi_other,
                "program": self.program_from,
            },
            individuals_data=[{}],
        )
        household_already_in_program_repr, individuals_already_in_program_repr = create_household_and_individuals(
            household_data={
                "registration_data_import": self.rdi_other,
                "program": self.program_to,
            },
            individuals_data=[{}],
        )
        household_collection = HouseholdCollectionFactory()
        individual_collection = IndividualCollectionFactory()
        household_already_in_program.household_collection = household_collection
        household_already_in_program.save()
        household_already_in_program_repr.household_collection = household_collection
        household_already_in_program_repr.save()
        individuals_already_in_program[0].individual_collection = individual_collection
        individuals_already_in_program[0].save()
        individuals_already_in_program_repr[0].individual_collection = individual_collection
        individuals_already_in_program_repr[0].save()

        self._object_count_before_after()
        self.assertFalse(
            ImportedHousehold.objects.filter(mis_unicef_id=household_withdrawn.unicef_id).exists(),
        )
        self.assertFalse(
            ImportedIndividual.objects.filter(mis_unicef_id=individuals[0].unicef_id).exists(),
        )
        self.assertFalse(
            ImportedIndividual.objects.filter(mis_unicef_id=individuals[1].unicef_id).exists(),
        )
        self.assertFalse(
            ImportedHousehold.objects.filter(mis_unicef_id=household_already_in_program.unicef_id).exists(),
        )
        self.assertFalse(
            ImportedIndividual.objects.filter(mis_unicef_id=individuals_already_in_program[0].unicef_id).exists(),
        )
