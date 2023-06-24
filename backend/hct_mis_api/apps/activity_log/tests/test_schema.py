from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.activity_log.models import LogEntry
from hct_mis_api.apps.activity_log.utils import create_diff
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program

ALL_LOGS_ENTRIES = """
query AllLogEntries($businessArea: String!, $objectId: UUID, $after: String, $before: String, $first: Int, $last: Int, $search: String, $module: String, $userId: String, $programId: String) {
  allLogEntries(after: $after, before: $before, first: $first, last: $last, objectId: $objectId, businessArea: $businessArea, search: $search, module: $module, userId: $userId, programId: $programId) {
    pageInfo {
      hasNextPage
      hasPreviousPage
      startCursor
      endCursor
      __typename
    }
    totalCount
    edges {
      cursor
      node {
        action
        objectId
        contentType {
          appLabel
          model
          name
          __typename
        }
        user {
          firstName
          lastName
          __typename
        }
        __typename
      }
      __typename
    }
    __typename
  }
}
"""


LOG_ENTRY_ACTION_CHOICES = """
query logEntryActionChoices{
  logEntryActionChoices{
    value
    name
  }
}
"""


class TestLogEntriesQueries(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        create_afghanistan()
        business_area = BusinessArea.objects.get(slug="afghanistan")
        cls.user = UserFactory(first_name="First", last_name="Last")
        cls.user_without_perms = UserFactory()
        cls.create_user_role_with_permissions(cls.user, [Permissions.ACTIVITY_LOG_VIEW], business_area)

        cls.program_1 = ProgramFactory(business_area=business_area, pk="ad17c53d-11b0-4e9b-8407-2e034f03fd31")
        program_2 = ProgramFactory(business_area=business_area, pk="c74612a1-212c-4148-be5b-4b41d20e623c")

        LogEntry.objects.create(
            action=LogEntry.CREATE,
            content_object=cls.program_1,
            user=cls.user,
            program=cls.program_1,
            business_area=business_area,
            object_repr=str(cls.program_1),
            changes=create_diff(None, cls.program_1, Program.ACTIVITY_LOG_MAPPING),
        )
        LogEntry.objects.create(
            action=LogEntry.CREATE,
            content_object=program_2,
            user=cls.user,
            program=program_2,
            business_area=business_area,
            object_repr=str(program_2),
            changes=create_diff(None, program_2, Program.ACTIVITY_LOG_MAPPING),
        )
        LogEntry.objects.create(
            action=LogEntry.CREATE,
            content_object=program_2,
            user=cls.user_without_perms,
            program=program_2,
            business_area=None,
            object_repr=str(program_2),
            changes=create_diff(None, program_2, Program.ACTIVITY_LOG_MAPPING),
        )

    def test_all_logs_queries_without_perms(self) -> None:
        self.snapshot_graphql_request(
            request_string=ALL_LOGS_ENTRIES,
            variables={"businessArea": "afghanistan", "objectId": str(self.program_1.pk), "first": 5},
            context={"user": self.user_without_perms},
        )

    def test_all_logs_queries(self) -> None:
        self.snapshot_graphql_request(
            request_string=ALL_LOGS_ENTRIES,
            variables={"businessArea": "afghanistan", "first": 5},
            context={"user": self.user},
        )

    def test_filter_by_object_id(self) -> None:
        self.snapshot_graphql_request(
            request_string=ALL_LOGS_ENTRIES,
            variables={"businessArea": "afghanistan", "objectId": str(self.program_1.pk), "first": 5},
            context={"user": self.user},
        )

    def test_filter_by_program_id(self) -> None:
        self.snapshot_graphql_request(
            request_string=ALL_LOGS_ENTRIES,
            variables={
                "businessArea": "afghanistan",
                "programId": self.id_to_base64(str(self.program_1.pk), "ProgramNode"),
                "first": 5,
            },
            context={"user": self.user},
        )

    def test_filter_by_user_id(self) -> None:
        self.snapshot_graphql_request(
            request_string=ALL_LOGS_ENTRIES,
            variables={
                "businessArea": "afghanistan",
                "userId": self.id_to_base64(str(self.user.pk), "UserNode"),
                "first": 5,
            },
            context={"user": self.user},
        )

    def test_log_entry_action_choices(self) -> None:
        self.snapshot_graphql_request(
            request_string=LOG_ENTRY_ACTION_CHOICES,
            context={"user": self.user},
        )
