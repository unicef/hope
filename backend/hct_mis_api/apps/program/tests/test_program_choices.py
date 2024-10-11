from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.core.base_test_case import APITestCase


class TestProgramChoices(APITestCase):
    QUERY_PROGRAM_STATUS_CHOICES = """
    query ProgramStatusChoices {
        programStatusChoices{
            name
            value
        }
    }
    """

    QUERY_PROGRAM_FREQUENCY_OF_PAYMENTS_CHOICES = """
    query ProgramFrequencyOfPaymentsChoices {
        programFrequencyOfPaymentsChoices{
            name
            value
        }
    }
    """

    QUERY_PROGRAM_SECTOR_CHOICES = """
    query ProgramSectorChoices {
        programSectorChoices{
            name
            value
        }
    }
    """

    QUERY_PROGRAM_SCOPE_CHOICES = """
    query ProgramScopeChoices {
        programScopeChoices{
            name
            value
        }
    }
    """

    QUERY_PROGRAM_CYCLE_STATUS_CHOICES = """
        query ProgramCycleStatusChoices {
            programCycleStatusChoices{
                name
                value
            }
        }
        """

    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = UserFactory()

    def test_status_choices_query(self) -> None:
        self.snapshot_graphql_request(
            request_string=self.QUERY_PROGRAM_STATUS_CHOICES,
            context={"user": self.user},
        )

    def test_program_frequency_of_payments_choices(self) -> None:
        self.snapshot_graphql_request(
            request_string=self.QUERY_PROGRAM_FREQUENCY_OF_PAYMENTS_CHOICES,
            context={"user": self.user},
        )

    def test_program_sector_choices(self) -> None:
        self.snapshot_graphql_request(
            request_string=self.QUERY_PROGRAM_SECTOR_CHOICES,
            context={"user": self.user},
        )

    def test_program_scope_choices(self) -> None:
        self.snapshot_graphql_request(
            request_string=self.QUERY_PROGRAM_SCOPE_CHOICES,
            context={"user": self.user},
        )

    def test_program_cycle_status_choices(self) -> None:
        self.snapshot_graphql_request(
            request_string=self.QUERY_PROGRAM_CYCLE_STATUS_CHOICES,
            context={"user": self.user},
        )
