from datetime import date

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.core.base_test_case import (
    BaseElasticSearchTestCase,
    DefaultTestCase,
)
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.grievance.fixtures import TicketAddIndividualDetailsFactory
from hct_mis_api.apps.grievance.services.data_change.add_individual_service import (
    AddIndividualService,
)
from hct_mis_api.apps.household.fixtures import create_household
from hct_mis_api.apps.household.models import SINGLE, Individual


class TestAddIndividualService(BaseElasticSearchTestCase, TestCase):
    databases = {"default", "registration_datahub"}

    @classmethod
    def setUpTestData(cls) -> None:
        create_afghanistan()
        household, _ = create_household()
        ticket_details = TicketAddIndividualDetailsFactory(
            household=household,
            individual_data={
                "given_name": "Test",
                "full_name": "Test Example",
                "family_name": "Example",
                "sex": "MALE",
                "birth_date": date(year=1980, month=2, day=1).isoformat(),
                "marital_status": SINGLE,
                "documents": [],
            },
            approve_status=True,
        )
        ticket = ticket_details.ticket
        ticket.save()

        cls.household = household
        cls.ticket = ticket

        super().setUpTestData()

    def test_increase_household_size_on_close_ticket(self) -> None:
        self.household.size = 3
        self.household.save(update_fields=("size",))

        service = AddIndividualService(self.ticket, {})
        service.close(UserFactory())

        self.household.refresh_from_db()
        self.assertEqual(self.household.size, 4)

    def test_increase_household_size_when_size_is_none_on_close_ticket(self) -> None:
        self.household.size = None
        self.household.save(update_fields=("size",))

        service = AddIndividualService(self.ticket, {})
        service.close(UserFactory())

        self.household.refresh_from_db()
        household_size = Individual.objects.filter(household=self.household).count()
        self.assertEqual(self.household.size, household_size)
