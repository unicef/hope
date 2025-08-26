from typing import Any
from unittest.mock import patch

from django.test import TestCase
from extras.test_utils.factories.account import UserFactory
from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.household import HouseholdFactory, IndividualFactory
from extras.test_utils.factories.program import ProgramFactory
from extras.test_utils.factories.sanction_list import SanctionListFactory

from hope.models.core import BusinessArea
from hope.apps.grievance.tasks.deduplicate_and_check_sanctions import (
    deduplicate_and_check_against_sanctions_list_task_single_individual,
)


class TestDeduplicateAndCheckAgainstSanctionsListTask(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.user = UserFactory.create()
        create_afghanistan()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")

        program_one = ProgramFactory(
            name="Test program ONE",
            business_area=BusinessArea.objects.first(),
        )

        cls.individual_data = {
            "full_name": "Benjamin Butler",
            "given_name": "Benjamin",
            "family_name": "Butler",
            "phone_no": "(953)682-4596",
            "birth_date": "1943-07-30",
        }
        cls.individual = IndividualFactory(
            household=None, program=program_one, business_area=cls.business_area, **cls.individual_data
        )
        household_one = HouseholdFactory(
            program=program_one,
            head_of_household=cls.individual,
        )
        household_one.individuals.add(cls.individual)

    @patch("hope.apps.grievance.tasks.deduplicate_and_check_sanctions.populate_index")
    @patch("hope.apps.grievance.tasks.deduplicate_and_check_sanctions.HardDocumentDeduplication.deduplicate")
    @patch(
        "hope.apps.grievance.tasks.deduplicate_and_check_sanctions.DeduplicateTask.deduplicate_individuals_from_other_source"
    )
    @patch("hope.apps.grievance.tasks.deduplicate_and_check_sanctions.create_needs_adjudication_tickets")
    @patch("hope.apps.grievance.tasks.deduplicate_and_check_sanctions.check_against_sanction_list_pre_merge")
    def test_execute(
        self,
        sanction_execute_mock: Any,
        create_needs_adjudication_tickets_mock: Any,
        deduplicate_individuals_mock: Any,
        deduplicate_mock: Any,
        populate_index_mock: Any,
    ) -> None:
        self.business_area.postpone_deduplication = True
        self.business_area.save()

        deduplicate_and_check_against_sanctions_list_task_single_individual(
            should_populate_index=True,
            individual=self.individual,
        )
        assert populate_index_mock.call_count == 1
        assert deduplicate_mock.call_count == 1
        assert deduplicate_individuals_mock.call_count == 0

        populate_index_mock.reset_mock()
        deduplicate_mock.reset_mock()

        self.business_area.postpone_deduplication = False
        self.business_area.save()

        deduplicate_and_check_against_sanctions_list_task_single_individual(
            should_populate_index=False,
            individual=self.individual,
        )

        assert populate_index_mock.call_count == 0
        assert deduplicate_mock.call_count == 1
        assert deduplicate_individuals_mock.call_count == 1
        assert create_needs_adjudication_tickets_mock.call_count == 2
        assert sanction_execute_mock.call_count == 0

    @patch("hope.apps.grievance.tasks.deduplicate_and_check_sanctions.populate_index")
    @patch("hope.apps.grievance.tasks.deduplicate_and_check_sanctions.HardDocumentDeduplication.deduplicate")
    @patch(
        "hope.apps.grievance.tasks.deduplicate_and_check_sanctions.DeduplicateTask.deduplicate_individuals_from_other_source"
    )
    @patch("hope.apps.grievance.tasks.deduplicate_and_check_sanctions.create_needs_adjudication_tickets")
    @patch("hope.apps.grievance.tasks.deduplicate_and_check_sanctions.check_against_sanction_list_pre_merge")
    def test_execute_enabled_screening(
        self,
        sanction_execute_mock: Any,
        create_needs_adjudication_tickets_mock: Any,
        deduplicate_individuals_mock: Any,
        deduplicate_mock: Any,
        populate_index_mock: Any,
    ) -> None:
        self.business_area.postpone_deduplication = False
        sanction_list = SanctionListFactory()
        sanction_list.save()
        self.individual.program.sanction_lists.add(sanction_list)
        self.business_area.save()

        deduplicate_and_check_against_sanctions_list_task_single_individual(
            should_populate_index=False,
            individual=self.individual,
        )

        assert populate_index_mock.call_count == 0
        assert deduplicate_mock.call_count == 1
        assert deduplicate_individuals_mock.call_count == 1
        assert create_needs_adjudication_tickets_mock.call_count == 2
        assert sanction_execute_mock.call_count == 1
