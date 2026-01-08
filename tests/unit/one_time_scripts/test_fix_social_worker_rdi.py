from django.test import TestCase
import pytest

from extras.test_utils.factories.core import DataCollectingTypeFactory, create_afghanistan
from extras.test_utils.factories.geo import AreaFactory
from extras.test_utils.factories.household import (
    IndividualRoleInHouseholdFactory,
    create_household_and_individuals,
)
from extras.test_utils.factories.program import ProgramFactory
from extras.test_utils.factories.registration_data import RegistrationDataImportFactory
from hope.apps.household.const import ROLE_PRIMARY
from hope.apps.program.utils import CopyProgramPopulation
from hope.models import DataCollectingType, Household, Individual, IndividualRoleInHousehold, RegistrationDataImport
from hope.models.utils import MergeStatusModel
from hope.one_time_scripts.fix_social_worker_rdi_missing_households import fix_social_worker_rdi_missing_households

pytestmark = pytest.mark.usefixtures("django_elasticsearch_setup")


@pytest.mark.elasticsearch
class TestFixSocialWorkerRdiMissingHouseholds(TestCase):
    """
    Test the script that fixes RDIs for social worker programs
    where households were not imported when using household IDs.

    This tests the logic that would be used in:
    src/hope/one_time_scripts/fix_social_worker_rdi_missing_households.py
    """

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.afghanistan = create_afghanistan()

        # Create social worker DCT
        cls.social_dct = DataCollectingTypeFactory(
            label="Social",
            code="social",
            type=DataCollectingType.Type.SOCIAL,
        )

        # Create source and target programs
        cls.program_from = ProgramFactory(
            business_area=cls.afghanistan,
            data_collecting_type=cls.social_dct,
        )
        cls.program_to = ProgramFactory(
            business_area=cls.afghanistan,
            data_collecting_type=cls.social_dct,
        )

        # Create households in source program
        cls.household1, cls.individuals1 = create_household_and_individuals(
            household_data={
                "program": cls.program_from,
                "admin1": AreaFactory(),
                "admin2": AreaFactory(),
            },
            individuals_data=[
                {
                    "given_name": "John",
                    "family_name": "Doe",
                    "program": cls.program_from,
                },
            ],
        )
        IndividualRoleInHouseholdFactory(
            household=cls.household1,
            individual=cls.individuals1[0],
            role=ROLE_PRIMARY,
        )

        cls.household2, cls.individuals2 = create_household_and_individuals(
            household_data={
                "program": cls.program_from,
                "admin1": AreaFactory(),
                "admin2": AreaFactory(),
            },
            individuals_data=[
                {
                    "given_name": "Bob",
                    "family_name": "Smith",
                    "program": cls.program_from,
                },
            ],
        )
        IndividualRoleInHouseholdFactory(
            household=cls.household2,
            individual=cls.individuals2[0],
            role=ROLE_PRIMARY,
        )

    def test_fix_missing_households_scenario_in_review(self) -> None:
        """
        Test the scenario where individuals were imported but households were not,
        and verify that the fix logic works correctly.

        This tests the actual fix_social_worker_rdi_missing_households() function.
        """
        # Create RDI with household IDs
        rdi = RegistrationDataImportFactory(
            business_area=self.afghanistan,
            program=self.program_to,
            data_source=RegistrationDataImport.PROGRAM_POPULATION,
            import_from_ids=f"{self.household1.unicef_id}, {self.household2.unicef_id}",
            status=RegistrationDataImport.IN_REVIEW,
        )

        # Simulate the bug: copy only individuals (not households)
        individuals_to_copy = Individual.objects.filter(
            program=self.program_from,
            household__unicef_id__in=[self.household1.unicef_id, self.household2.unicef_id],
        )

        CopyProgramPopulation(
            copy_from_individuals=individuals_to_copy,
            copy_from_households=Household.objects.none(),  # Bug: no households copied
            program=self.program_to,
            rdi_merge_status=MergeStatusModel.PENDING,
            create_collection=False,
            rdi=rdi,
        ).copy_program_population()

        # Verify the bug: individuals imported but households missing
        imported_individuals = Individual.all_merge_status_objects.filter(
            program=self.program_to,
            registration_data_import=rdi,
        )
        imported_households = Household.all_merge_status_objects.filter(
            program=self.program_to,
            registration_data_import=rdi,
        )

        assert imported_individuals.count() == 2  # 1 from household1, 1 from household2
        assert imported_households.count() == 0  # BUG: No households

        # Run the fix script
        fix_social_worker_rdi_missing_households()
        # Verify the fix: households now imported
        imported_households_after_fix = Household.all_merge_status_objects.filter(
            program=self.program_to,
            registration_data_import=rdi,
        )
        assert imported_households_after_fix.count() == 2  # FIXED: Both households now present

        # Verify that the households have the correct unicef_ids
        household_ids_copied = list(imported_households_after_fix.values_list("copied_from__unicef_id", flat=True))
        assert self.household1.unicef_id in household_ids_copied
        assert self.household2.unicef_id in household_ids_copied

        # Verify roles were also copied
        imported_roles = IndividualRoleInHousehold.all_merge_status_objects.filter(
            household__program=self.program_to,
            household__registration_data_import=rdi,
        )
        assert imported_roles.count() == 2  # 1 role for household1 + 1 role for household2

        # Verify households have the same merge status as individuals

        assert imported_households_after_fix[0].rdi_merge_status == MergeStatusModel.PENDING
        assert imported_households_after_fix[1].rdi_merge_status == MergeStatusModel.PENDING
        assert imported_individuals[0].rdi_merge_status == MergeStatusModel.PENDING

        # Verify individuals are linked to the correct households
        for individual in imported_individuals:
            assert individual.household is not None
            assert individual.household in imported_households_after_fix
            assert individual.household.unicef_id == individual.copied_from.household.unicef_id

    def test_fix_missing_households_scenario_merged(self) -> None:
        # Create RDI with household IDs
        rdi = RegistrationDataImportFactory(
            business_area=self.afghanistan,
            program=self.program_to,
            data_source=RegistrationDataImport.PROGRAM_POPULATION,
            import_from_ids=f"{self.household1.unicef_id}, {self.household2.unicef_id}",
            status=RegistrationDataImport.MERGED,
        )

        # Simulate the bug: copy only individuals (not households)
        individuals_to_copy = Individual.objects.filter(
            program=self.program_from,
            household__unicef_id__in=[self.household1.unicef_id, self.household2.unicef_id],
        )

        CopyProgramPopulation(
            copy_from_individuals=individuals_to_copy,
            copy_from_households=Household.objects.none(),  # Bug: no households copied
            program=self.program_to,
            rdi_merge_status=MergeStatusModel.MERGED,
            create_collection=False,
            rdi=rdi,
        ).copy_program_population()

        # Verify the bug: individuals imported but households missing
        imported_individuals = Individual.all_merge_status_objects.filter(
            program=self.program_to,
            registration_data_import=rdi,
        )
        imported_households = Household.all_merge_status_objects.filter(
            program=self.program_to,
            registration_data_import=rdi,
        )

        assert imported_individuals.count() == 2  # 1 from household1, 1 from household2
        assert imported_households.count() == 0  # BUG: No households

        # Run the fix script
        fix_social_worker_rdi_missing_households()
        # Verify the fix: households now imported
        imported_households_after_fix = Household.all_merge_status_objects.filter(
            program=self.program_to,
            registration_data_import=rdi,
        )
        assert imported_households_after_fix.count() == 2  # FIXED: Both households now present

        # Verify that the households have the correct unicef_ids
        household_ids_copied = list(imported_households_after_fix.values_list("copied_from__unicef_id", flat=True))
        assert self.household1.unicef_id in household_ids_copied
        assert self.household2.unicef_id in household_ids_copied

        # Verify roles were also copied
        imported_roles = IndividualRoleInHousehold.all_merge_status_objects.filter(
            household__program=self.program_to,
            household__registration_data_import=rdi,
        )
        assert imported_roles.count() == 2  # 1 role for household1 + 1 role for household2

        # Verify households have the same merge status as individuals

        assert imported_households_after_fix[0].rdi_merge_status == MergeStatusModel.MERGED
        assert imported_households_after_fix[1].rdi_merge_status == MergeStatusModel.MERGED
        assert imported_individuals[0].rdi_merge_status == MergeStatusModel.MERGED

        # Verify individuals are linked to the correct households
        for individual in imported_individuals:
            assert individual.household is not None
            assert individual.household in imported_households_after_fix
            assert individual.household.unicef_id == individual.copied_from.household.unicef_id

    def test_scenario_already_fixed_no_change(self) -> None:
        """
        Test that if households are already present, the fix script doesn't create duplicates.
        """
        # Create RDI with household IDs
        rdi = RegistrationDataImportFactory(
            business_area=self.afghanistan,
            program=self.program_to,
            data_source=RegistrationDataImport.PROGRAM_POPULATION,
            import_from_ids=f"{self.household1.unicef_id}",
            status=RegistrationDataImport.IN_REVIEW,
        )

        # Correctly import both households and individuals
        households_to_copy = Household.objects.filter(
            program=self.program_from,
            unicef_id__in=[self.household1.unicef_id],
        )
        individuals_to_copy = Individual.objects.filter(
            program=self.program_from,
            household__unicef_id__in=[self.household1.unicef_id],
        )

        CopyProgramPopulation(
            copy_from_individuals=individuals_to_copy,
            copy_from_households=households_to_copy,
            program=self.program_to,
            rdi_merge_status=MergeStatusModel.PENDING,
            create_collection=False,
            rdi=rdi,
        ).copy_program_population()

        imported_individuals = Individual.all_merge_status_objects.filter(
            program=self.program_to,
            registration_data_import=rdi,
        )
        imported_households = Household.all_merge_status_objects.filter(
            program=self.program_to,
            registration_data_import=rdi,
        )

        assert imported_individuals.count() == 1
        assert imported_households.count() == 1

        # Run the fix script - it should skip this RDI since households are present
        fix_social_worker_rdi_missing_households()

        # Verify no duplicates were created
        imported_households_after = Household.all_merge_status_objects.filter(
            program=self.program_to,
            registration_data_import=rdi,
        )

        # Should still be 1, no duplicates
        assert imported_households_after.count() == 1
