from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.utils import cached_business_areas_slug_id_dict
from hct_mis_api.apps.household.fixtures import create_household_and_individuals
from hct_mis_api.apps.household.models import (
    DUPLICATE,
    NEEDS_ADJUDICATION,
    SANCTION_LIST_CONFIRMED_MATCH,
    SANCTION_LIST_POSSIBLE_MATCH,
)


class TestIndividualFlagQuery(APITestCase):
    QUERY = """
    query AllIndividuals($flags: [String]) {
      allIndividuals(flags: $flags, businessArea: "afghanistan", orderBy: "id") {
        edges {
          node {
            givenName
            familyName
            phoneNo
            birthDate
          }
        }
      }
    }
    """

    @classmethod
    def setUpTestData(cls):
        cached_business_areas_slug_id_dict.cache_clear()
        cls.maxDiff = None
        create_afghanistan()
        cls.user = UserFactory()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")

        individuals_to_create = [
            {
                "full_name": "Benjamin Butler",
                "given_name": "Benjamin",
                "family_name": "Butler",
                "phone_no": "(953)682-4596",
                "birth_date": "1943-07-30",
                "id": "ffb2576b-126f-42de-b0f5-ef889b7bc1fe",
                "deduplication_golden_record_status": NEEDS_ADJUDICATION,
            },
            {
                "full_name": "Robin Ford",
                "given_name": "Robin",
                "family_name": "Ford",
                "phone_no": "+18663567905",
                "birth_date": "1946-02-15",
                "id": "8ef39244-2884-459b-ad14-8d63a6fe4a4a",
                "duplicate": True,
            },
            {
                "full_name": "Timothy Perry",
                "given_name": "Timothy",
                "family_name": "Perry",
                "phone_no": "(548)313-1700-902",
                "birth_date": "1983-12-21",
                "id": "badd2d2d-7ea0-46f1-bb7a-69f385bacdcd",
                "sanction_list_possible_match": True,
            },
            {
                "full_name": "Eric Torres",
                "given_name": "Eric",
                "family_name": "Torres",
                "phone_no": "(228)231-5473",
                "birth_date": "1973-03-23",
                "id": "2c1a26a3-2827-4a99-9000-a88091bf017c",
                "sanction_list_confirmed_match": True,
            },
            {
                "full_name": "Kailan Shan",
                "given_name": "Kailan",
                "family_name": "Shan",
                "phone_no": "(228)271-5373",
                "birth_date": "1943-11-03",
                "id": "9893c103-7e20-4a62-804c-bfcc014a2b2f",
                "deduplication_golden_record_status": NEEDS_ADJUDICATION,
                "sanction_list_possible_match": True,
                "sanction_list_confirmed_match": True,
            },
            {
                "full_name": "Jenna Franklin",
                "given_name": "Jenna",
                "family_name": "Franklin",
                "phone_no": "001-296-358-5428-607",
                "birth_date": "1969-11-29",
                "id": "0fc995cc-ea72-4319-9bfe-9c9fda3ec191",
            },
        ]
        create_household_and_individuals(None, individuals_to_create)
        cls.create_user_role_with_permissions(
            cls.user, [Permissions.POPULATION_VIEW_INDIVIDUALS_LIST], cls.business_area
        )

    @parameterized.expand(
        [
            ([NEEDS_ADJUDICATION],),
            ([DUPLICATE],),
            ([SANCTION_LIST_POSSIBLE_MATCH],),
            ([SANCTION_LIST_CONFIRMED_MATCH],),
            (
                [
                    NEEDS_ADJUDICATION,
                    DUPLICATE,
                    SANCTION_LIST_POSSIBLE_MATCH,
                    SANCTION_LIST_CONFIRMED_MATCH,
                ],
            ),
            ([],),
            (None,),
        ]
    )
    def test_individual_programme_filter(self, flags):
        self.snapshot_graphql_request(
            request_string=self.QUERY,
            context={"user": self.user},
            variables={"flags": flags},
        )
