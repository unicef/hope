from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.registration_datahub.fixtures import ImportedIndividualFactory

ALL_IMPORTED_INDIVIDUALS_QUERY = """
query AllImportedIndividuals {
  allImportedIndividuals(orderBy: "full_name", businessArea: "afghanistan") {
    edges {
      node {
        birthDate
        familyName
        fullName
        givenName
        phoneNo
      }
    }
  }
}
"""
ALL_IMPORTED_INDIVIDUALS_ORDER_BY_BIRTH_DATE_A_QUERY = """
query AllImportedIndividuals {
  allImportedIndividuals(orderBy: "birth_date", businessArea: "afghanistan") {
    edges {
      node {
        birthDate
        familyName
        fullName
        givenName
        phoneNo
      }
    }
  }
}
"""
ALL_IMPORTED_INDIVIDUALS_ORDER_BY_BIRTH_DATE_D_QUERY = """
query AllImportedIndividuals {
  allImportedIndividuals(orderBy: "-birth_date", businessArea: "afghanistan") {
    edges {
      node {
        birthDate
        familyName
        fullName
        givenName
        phoneNo
      }
    }
  }
}
"""
IMPORTED_INDIVIDUAL_QUERY = """
query ImportedIndividual($id: ID!) {
  importedIndividual(id: $id) {
    birthDate
        familyName
        fullName
        givenName
        phoneNo
  }
}
"""


class TestImportedIndividualQuery(APITestCase):
    databases = "__all__"

    # IMPORTANT!
    # FREEZGUN doesn't work this snapshot have to be updated once a year
    MAX_AGE = 51
    MIN_AGE = 37

    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory.create()
        create_afghanistan()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")
        cls.individuals_to_create = [
            {
                "full_name": "Benjamin Butler",
                "given_name": "Benjamin",
                "family_name": "Butler",
                "phone_no": "(953)682-4596",
                "birth_date": "1943-07-30",
                "sex": "MALE",
                "id": "47dd625a-e64e-48a9-bfcd-e970ca356bf7",
            },
            {
                "full_name": "Robin Ford",
                "given_name": "Robin",
                "family_name": "Ford",
                "phone_no": "+18663567905",
                "birth_date": "1946-02-15",
                "sex": "MALE",
                "id": "f91eb18b-175a-495c-a49d-92af4ad554ba",
            },
            {
                "full_name": "Timothy Perry",
                "given_name": "Timothy",
                "family_name": "Perry",
                "phone_no": "(548)313-1700-902",
                "birth_date": "1983-12-21",
                "sex": "MALE",
                "id": "4174aa63-4d3d-416a-bf39-09bc0e14e7c6",
            },
            {
                "full_name": "Eric Torres",
                "given_name": "Eric",
                "family_name": "Torres",
                "phone_no": "(228)231-5473",
                "birth_date": "1973-03-23",
                "sex": "MALE",
                "id": "6aada701-4639-4142-92ca-7cbf82411534",
            },
            {
                "full_name": "Jenna Franklin",
                "given_name": "Jenna",
                "family_name": "Franklin",
                "phone_no": "001-296-358-5428-607",
                "birth_date": "1969-11-29",
                "sex": "FEMALE",
                "id": "c38fa2a5-e518-495c-988f-c308c94dcc53",
            },
        ]

        cls.individuals = [ImportedIndividualFactory(**individual) for individual in cls.individuals_to_create]
        for individual in cls.individuals:
            individual.registration_data_import.business_area_slug = "afghanistan"
            individual.registration_data_import.save()

    @parameterized.expand(
        [
            ("all_with_permission", [Permissions.RDI_VIEW_DETAILS], ALL_IMPORTED_INDIVIDUALS_QUERY),
            ("all_without_permission", [], ALL_IMPORTED_INDIVIDUALS_QUERY),
            (
                "order_by_dob_all_with_permission",
                [Permissions.RDI_VIEW_DETAILS],
                ALL_IMPORTED_INDIVIDUALS_ORDER_BY_BIRTH_DATE_A_QUERY,
            ),
            (
                "order_by_dob_d_all_with_permission",
                [Permissions.RDI_VIEW_DETAILS],
                ALL_IMPORTED_INDIVIDUALS_ORDER_BY_BIRTH_DATE_D_QUERY,
            ),
        ]
    )
    def test_imported_individual_query(self, _, permissions, query):
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=query,
            context={"user": self.user},
        )

    @parameterized.expand(
        [
            ("with_permission", [Permissions.RDI_VIEW_DETAILS]),
            ("without_permission", []),
        ]
    )
    def test_imported_individual_query_single(self, _, permissions):
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=IMPORTED_INDIVIDUAL_QUERY,
            context={"user": self.user},
            variables={
                "id": self.id_to_base64(
                    self.individuals[0].id,
                    "ImportedIndividualNode",
                )
            },
        )
