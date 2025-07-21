from tests.extras.test_utils.factories.account import PartnerFactory
from hct_mis_api.apps.core.base_test_case import APITestCase
from tests.extras.test_utils.factories.core import create_afghanistan
from tests.extras.test_utils.factories.geo import AreaFactory, CountryFactory
from tests.extras.test_utils.factories.household import (
    DocumentFactory,
    DocumentTypeFactory,
    HouseholdCollectionFactory,
    IndividualCollectionFactory,
    IndividualFactory,
    IndividualIdentityFactory,
    IndividualRoleInHouseholdFactory,
    create_household_and_individuals,
)
from hct_mis_api.apps.household.models import (
    HEAD,
    MALE,
    ROLE_ALTERNATE,
    ROLE_PRIMARY,
    Document,
    Household,
    Individual,
    IndividualIdentity,
    IndividualRoleInHousehold,
)
from tests.extras.test_utils.factories.payment import generate_delivery_mechanisms
from hct_mis_api.apps.payment.models import Account, AccountType, DeliveryMechanism
from tests.extras.test_utils.factories.fixtures import ProgramFactory
from hct_mis_api.apps.registration_data.fixtures import RegistrationDataImportFactory
from hct_mis_api.apps.registration_datahub.tasks.import_program_population import (
    import_program_population,
)
from hct_mis_api.apps.utils.models import MergeStatusModel

HOUSEHOLD_FIELDS = (
    "consent_sign",
    "consent",
    "consent_sharing",
    "residence_status",
    "country_origin",
    "zip_code",
    "size",
    "address",
    "country",
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
    "flex_fields",
    "start",
    "deviceid",
    "name_enumerator",
    "org_enumerator",
    "org_name_enumerator",
    "village",
    "registration_method",
    "currency",
    "unhcr_id",
    "geopoint",
    "returnee",
    "fchild_hoh",
    "child_hoh",
    "detail_id",
    "collect_type",
    "unicef_id",
)

INDIVIDUAL_FIELDS = (
    "photo",
    "full_name",
    "given_name",
    "middle_name",
    "family_name",
    "relationship",
    "sex",
    "birth_date",
    "estimated_birth_date",
    "marital_status",
    "phone_no",
    "phone_no_alternative",
    "email",
    "disability",
    "flex_fields",
    "deduplication_batch_status",
    "deduplication_batch_results",
    "observed_disability",
    "seeing_disability",
    "hearing_disability",
    "physical_disability",
    "memory_disability",
    "selfcare_disability",
    "comms_disability",
    "who_answers_phone",
    "who_answers_alt_phone",
    "pregnant",
    "work_status",
    "detail_id",
    "disability_certificate_picture",
    "preferred_language",
    "age_at_registration",
    "payment_delivery_phone_no",
    "wallet_name",
    "blockchain_name",
    "wallet_address",
    "unicef_id",
)


class TestProgramPopulationToPendingObjects(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        generate_delivery_mechanisms()
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
        cls.household, cls.individuals = create_household_and_individuals(
            household_data={
                "registration_data_import": cls.rdi_other,
                "first_registration_date": "2021-01-01",
                "last_registration_date": "2021-01-01",
                "program": cls.program_from,
                "admin_area": AreaFactory(),
                "admin1": AreaFactory(),
                "admin2": AreaFactory(),
                "admin3": AreaFactory(),
                "admin4": AreaFactory(),
                "detail_id": "1234567890",
                "flex_fields": {"enumerator_id": "123", "some": "thing"},
                "country": country,
                "country_origin": country_origin,
            },
            individuals_data=[
                {
                    "registration_data_import": cls.rdi_other,
                    "first_registration_date": "2021-01-01",
                    "last_registration_date": "2021-01-01",
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
                {
                    "first_registration_date": "2024-02-21",
                    "last_registration_date": "2024-02-24",
                },
            ],
        )
        cls.ind_role_in_hh = IndividualRoleInHouseholdFactory(
            household=cls.household,
            individual=cls.individuals[1],
            role=ROLE_PRIMARY,
        )
        document_type = DocumentTypeFactory(key="birth_certificate")
        DocumentTypeFactory(
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

        cls.delivery_mechanism = DeliveryMechanism.objects.get(code="mobile_money")
        cls.delivery_mechanism_data = Account(
            individual=cls.individuals[0],
            data={"phone_number_test": "1234567890"},
            rdi_merge_status=MergeStatusModel.MERGED,
            account_type=AccountType.objects.get(key="mobile"),
        )
        cls.delivery_mechanism_data.save()

    def _object_count_before_after(self) -> None:
        self.assertEqual(
            Household.pending_objects.count(),
            0,
        )
        self.assertEqual(
            Individual.pending_objects.count(),
            0,
        )
        self.assertEqual(
            IndividualIdentity.pending_objects.count(),
            0,
        )
        self.assertEqual(
            Document.pending_objects.count(),
            0,
        )
        self.assertEqual(
            IndividualRoleInHousehold.pending_objects.count(),
            0,
        )
        self.assertEqual(Account.all_objects.filter(rdi_merge_status=MergeStatusModel.PENDING).count(), 0)

        import_program_population(
            import_from_program_id=str(self.program_from.id),
            import_to_program_id=str(self.program_to.id),
            rdi=self.registration_data_import,
        )

        self.assertEqual(
            Household.pending_objects.count(),
            1,
        )
        self.assertEqual(
            Individual.pending_objects.count(),
            2,
        )
        self.assertEqual(
            IndividualIdentity.pending_objects.count(),
            1,
        )
        self.assertEqual(
            Document.pending_objects.count(),
            1,
        )
        self.assertEqual(
            IndividualRoleInHousehold.pending_objects.count(),
            1,
        )
        self.assertEqual(Account.all_objects.filter(rdi_merge_status=MergeStatusModel.PENDING).count(), 1)

    def test_create_pending_objects_from_objects(self) -> None:
        self._object_count_before_after()
        pending_household = Household.pending_objects.first()
        self.assertIsNotNone(pending_household)

        self.household.refresh_from_db()
        self.individuals[0].refresh_from_db()
        self.individuals[1].refresh_from_db()

        for field in HOUSEHOLD_FIELDS:
            pending_household_field = getattr(pending_household, field)
            household_field = getattr(self.household, field)
            self.assertEqual(
                pending_household_field,
                household_field,
            )
        self.assertNotEqual(pending_household.first_registration_date, self.household.first_registration_date)
        self.assertNotEqual(pending_household.last_registration_date, self.household.last_registration_date)
        self.assertEqual(
            pending_household.program_id,
            self.program_to.id,
        )
        self.assertEqual(
            pending_household.registration_data_import_id,
            self.registration_data_import.id,
        )
        self.assertEqual(
            pending_household.rdi_merge_status,
            MergeStatusModel.PENDING,
        )
        self.assertIsNone(
            pending_household.household_collection,
        )

        pending_individuals = Individual.pending_objects.all()
        head_of_household_pending_individual = pending_individuals.get(relationship=HEAD)

        self.assertEqual(
            pending_household.head_of_household,
            head_of_household_pending_individual,
        )

        self.assertEqual(
            self.household.head_of_household,
            self.individuals[0],
        )
        self.assertEqual(
            self.individuals[0].household,
            self.household,
        )
        self.assertEqual(
            self.individuals[1].household,
            self.household,
        )

        for field in INDIVIDUAL_FIELDS:
            imported_individual_field = getattr(head_of_household_pending_individual, field)
            individual_field = getattr(self.individuals[0], field)
            self.assertEqual(imported_individual_field, individual_field, field)
        self.assertNotEqual(
            head_of_household_pending_individual.first_registration_date,
            self.individuals[0].first_registration_date,
        )
        self.assertNotEqual(
            head_of_household_pending_individual.last_registration_date,
            self.individuals[0].last_registration_date,
        )
        for pending_individual in pending_individuals:
            self.assertEqual(
                pending_individual.program_id,
                self.program_to.id,
            )
            self.assertEqual(
                pending_individual.registration_data_import_id,
                self.registration_data_import.id,
            )
            self.assertEqual(
                pending_individual.rdi_merge_status,
                MergeStatusModel.PENDING,
            )
            self.assertIsNone(
                pending_individual.individual_collection,
            )
            self.assertEqual(
                pending_individual.household,
                pending_household,
            )

        self.assertEqual(
            head_of_household_pending_individual.relationship,
            HEAD,
        )

        pending_document = Document.pending_objects.first()
        for field in (
            "document_number",
            "photo",
            "expiry_date",
            "issuance_date",
        ):
            pending_document_field = getattr(pending_document, field)
            document_field = getattr(self.document, field)
            self.assertEqual(
                pending_document_field,
                document_field,
            )

        self.assertEqual(
            pending_document.program_id,
            self.program_to.id,
        )
        self.assertEqual(
            pending_document.rdi_merge_status,
            MergeStatusModel.PENDING,
        )
        self.assertEqual(
            pending_document.individual,
            head_of_household_pending_individual,
        )
        self.assertEqual(
            pending_document.status,
            Document.STATUS_PENDING,
        )

        pending_identity = IndividualIdentity.pending_objects.first()
        self.assertEqual(
            pending_identity.number,
            self.identity.number,
        )

        self.assertEqual(
            pending_identity.country.iso_code2,
            self.identity.country.iso_code2,
        )

        self.assertEqual(
            pending_identity.partner,
            self.identity.partner,
        )

        self.assertEqual(
            pending_identity.rdi_merge_status,
            MergeStatusModel.PENDING,
        )

        self.assertEqual(
            pending_identity.individual,
            head_of_household_pending_individual,
        )
        pending_individual_role_in_household = IndividualRoleInHousehold.pending_objects.first()
        self.assertEqual(
            pending_individual_role_in_household.household.unicef_id,
            self.household.unicef_id,
        )
        self.assertEqual(
            pending_individual_role_in_household.individual.unicef_id,
            self.individuals[1].unicef_id,
        )
        self.assertEqual(
            pending_individual_role_in_household.role,
            ROLE_PRIMARY,
        )
        self.assertEqual(
            pending_individual_role_in_household.rdi_merge_status,
            MergeStatusModel.PENDING,
        )
        self.assertEqual(
            pending_individual_role_in_household.household,
            pending_household,
        )
        self.assertEqual(
            pending_individual_role_in_household.individual,
            pending_individuals.exclude(relationship=HEAD).first(),
        )
        registration_data_import = RegistrationDataImportFactory(
            business_area=self.afghanistan,
            program=self.program_to,
        )
        import_program_population(
            import_from_program_id=str(self.program_from.id),
            import_to_program_id=str(self.program_to.id),
            rdi=registration_data_import,
        )
        pending_household_count = (
            Household.pending_objects.filter(registration_data_import=registration_data_import)
            .order_by("created_at")
            .count()
        )
        pending_individual_count = (
            Individual.pending_objects.filter(registration_data_import=registration_data_import)
            .order_by("-created_at")
            .count()
        )
        self.assertEqual(pending_household_count, 0)
        self.assertEqual(pending_individual_count, 0)

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
                    "first_registration_date": "2024-02-21",
                    "last_registration_date": "2024-02-24",
                },
                {
                    "registration_data_import": self.rdi_other,
                    "duplicate": True,
                    "first_registration_date": "2024-02-21",
                    "last_registration_date": "2024-02-24",
                },
            ],
        )
        household_already_in_program, individuals_already_in_program = create_household_and_individuals(
            household_data={
                "registration_data_import": self.rdi_other,
                "program": self.program_from,
            },
            individuals_data=[
                {
                    "first_registration_date": "2024-02-21",
                    "last_registration_date": "2024-02-24",
                }
            ],
        )
        household_already_in_program_repr, individuals_already_in_program_repr = create_household_and_individuals(
            household_data={
                "registration_data_import": self.rdi_other,
                "program": self.program_to,
            },
            individuals_data=[
                {
                    "first_registration_date": "2024-02-21",
                    "last_registration_date": "2024-02-24",
                }
            ],
        )
        household_collection = HouseholdCollectionFactory()
        individual_collection = IndividualCollectionFactory()
        household_already_in_program.household_collection = household_collection
        household_already_in_program.save()
        household_already_in_program_repr.household_collection = household_collection
        household_already_in_program_repr.unicef_id = household_already_in_program.unicef_id
        household_already_in_program_repr.save()
        individuals_already_in_program[0].individual_collection = individual_collection
        individuals_already_in_program[0].save()
        individuals_already_in_program_repr[0].individual_collection = individual_collection
        individuals_already_in_program_repr[0].unicef_id = individuals_already_in_program[0].unicef_id
        individuals_already_in_program_repr[0].save()

        self._object_count_before_after()
        self.assertFalse(
            Household.pending_objects.filter(unicef_id=household_withdrawn.unicef_id).exists(),
        )
        self.assertFalse(
            Individual.pending_objects.filter(unicef_id=individuals[0].unicef_id).exists(),
        )
        self.assertFalse(
            Individual.pending_objects.filter(unicef_id=individuals[1].unicef_id).exists(),
        )
        self.assertFalse(
            Household.pending_objects.filter(unicef_id=household_already_in_program.unicef_id).exists(),
        )
        self.assertFalse(
            Individual.pending_objects.filter(unicef_id=individuals_already_in_program[0].unicef_id).exists(),
        )

    def test_import_program_population_with_excluded_individuals(self) -> None:
        individual_already_in_program_to = IndividualFactory(
            registration_data_import=self.rdi_other,
            program=self.program_to,
        )
        household, individuals = create_household_and_individuals(
            household_data={
                "registration_data_import": self.registration_data_import,
                "program": self.program_from,
            },
            individuals_data=[
                {
                    "registration_data_import": self.registration_data_import,
                    "program": self.program_from,
                },
            ],
        )
        individual_already_in_program_from = individuals[0]
        IndividualRoleInHouseholdFactory(
            household=household,
            individual=individual_already_in_program_from,
            role=ROLE_PRIMARY,
        )
        individual_collection = IndividualCollectionFactory()
        individual_already_in_program_to.individual_collection = individual_collection
        individual_already_in_program_to.save()
        individual_already_in_program_from.individual_collection = individual_collection
        individual_already_in_program_from.unicef_id = individual_already_in_program_to.unicef_id
        individual_already_in_program_from.save()

        self.assertFalse(
            Individual.pending_objects.filter(unicef_id=individuals[0].unicef_id).exists(),
        )
        import_program_population(
            import_from_program_id=str(self.program_from.id),
            import_to_program_id=str(self.program_to.id),
            rdi=self.registration_data_import,
        )

        # still no pending individual as it is excluded from the import (representation already in the program)
        self.assertFalse(
            Individual.pending_objects.filter(unicef_id=individual_already_in_program_from.unicef_id).exists(),
        )

        new_hh_repr = Household.pending_objects.filter(
            unicef_id=household.unicef_id,
            program=self.program_to,
        ).first()
        self.assertEqual(
            new_hh_repr.representatives.count(),
            1,
        )
        self.assertEqual(
            new_hh_repr.representatives.first(),
            individual_already_in_program_to,
        )

        self.assertEqual(
            new_hh_repr.head_of_household,
            individual_already_in_program_to,
        )

        # role in original program
        self.assertIsNotNone(
            IndividualRoleInHousehold.objects.filter(
                household=household,
                individual=individual_already_in_program_from,
            ).first(),
        )
        # role in new program
        self.assertIsNotNone(
            IndividualRoleInHousehold.original_and_repr_objects.filter(
                household=new_hh_repr,
                individual=individual_already_in_program_to,
            ).first(),
        )

    def test_import_program_population_individual_without_household(self) -> None:
        program_from_1 = ProgramFactory(business_area=self.afghanistan)

        create_household_and_individuals(
            household_data={
                "registration_data_import": self.registration_data_import,
                "program": program_from_1,
            },
            individuals_data=[
                {
                    "registration_data_import": self.registration_data_import,
                    "program": program_from_1,
                },
            ],
        )
        individual_without_hh = IndividualFactory(
            registration_data_import=self.registration_data_import,
            program=program_from_1,
        )

        import_program_population(
            import_from_program_id=str(program_from_1.id),
            import_to_program_id=str(self.program_to.id),
            rdi=self.registration_data_import,
        )

        self.assertEqual(Individual.pending_objects.filter(program=self.program_to).count(), 2)

        individual_without_hh_repr = Individual.pending_objects.filter(
            program=self.program_to,
            unicef_id=individual_without_hh.unicef_id,
        ).first()

        self.assertIsNotNone(individual_without_hh_repr)
        self.assertEqual(individual_without_hh_repr.household, None)

    def test_import_program_population_withdrawn_individual_with_role(self) -> None:
        program_from_1 = ProgramFactory(business_area=self.afghanistan)

        household, individuals = create_household_and_individuals(
            household_data={
                "registration_data_import": self.registration_data_import,
                "program": program_from_1,
            },
            individuals_data=[
                {
                    "registration_data_import": self.registration_data_import,
                    "program": program_from_1,
                },
                {
                    "registration_data_import": self.registration_data_import,
                    "program": program_from_1,
                },
            ],
        )

        individual = individuals[1]
        # alternate role held by withdrawn individual
        IndividualRoleInHouseholdFactory(
            household=household,
            individual=individual,
            role=ROLE_ALTERNATE,
        )
        individual.withdrawn = True
        individual.save()

        import_program_population(
            import_from_program_id=str(program_from_1.id),
            import_to_program_id=str(self.program_to.id),
            rdi=self.registration_data_import,
        )

        # withdrawn individual not imported
        self.assertEqual(Individual.pending_objects.filter(program=self.program_to).count(), 1)

        self.assertFalse(
            IndividualRoleInHousehold.pending_objects.filter(
                role=ROLE_ALTERNATE,
            ).exists(),
        )
