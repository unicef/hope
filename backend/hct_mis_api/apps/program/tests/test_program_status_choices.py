from account.fixtures import UserFactory
from core.tests import APITestCase


class TestProgramStatusChoices(APITestCase):

    QUERY_PROGRAM_STATUS_CHOICES = """
    query ProgramStatusChoices {
        programStatusChoices
    }
    """

    def setUp(self):
        super().setUp()
        self.user = UserFactory()

    def test_status_choices_query(self):
        self.snapshot_graphql_request(
            request_string=self.QUERY_PROGRAM_STATUS_CHOICES,
            context={'user': self.user}
        )
