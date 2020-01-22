from account.fixtures import UserFactory
from core.base_test_case import APITestCase


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

    def setUp(self):
        super().setUp()
        self.user = UserFactory()

    def test_status_choices_query(self):
        self.snapshot_graphql_request(
            request_string=self.QUERY_PROGRAM_STATUS_CHOICES,
            context={"user": self.user},
        )

    def test_program_frequency_of_payments_choices(self):
        self.snapshot_graphql_request(
            request_string=self.QUERY_PROGRAM_FREQUENCY_OF_PAYMENTS_CHOICES,
            context={"user": self.user},
        )

    def test_program_sector_choices(self):
        self.snapshot_graphql_request(
            request_string=self.QUERY_PROGRAM_SECTOR_CHOICES,
            context={"user": self.user},
        )

    def test_program_scope_choices(self):
        self.snapshot_graphql_request(
            request_string=self.QUERY_PROGRAM_SCOPE_CHOICES,
            context={"user": self.user},
        )
