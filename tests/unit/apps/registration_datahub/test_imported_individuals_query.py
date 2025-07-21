from typing import Any, List

from django.conf import settings

from parameterized import parameterized

from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.program.models import ProgramPartnerThrough
from hct_mis_api.apps.utils.models import MergeStatusModel
from tests.extras.test_utils.factories.account import PartnerFactory, UserFactory
from tests.extras.test_utils.factories.core import create_afghanistan
from tests.extras.test_utils.factories.household import IndividualFactory
from tests.extras.test_utils.factories.program import ProgramFactory

ALL_IMPORTED_INDIVIDUALS_QUERY = """
query AllIndividuals {
  allIndividuals(orderBy: "full_name", businessArea: "afghanistan", rdiMergeStatus: "PENDING") {
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
query AllIndividuals {
  allIndividuals(orderBy: "birth_date", businessArea: "afghanistan", rdiMergeStatus: "PENDING") {
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
query AllIndividuals {
  allIndividuals(orderBy: "-birth_date", businessArea: "afghanistan", rdiMergeStatus: "PENDING") {
    edges {
      node {
        birthDate
        familyName
        fullName
        givenName
        phoneNo
        email
      }
    }
  }
}
"""
IMPORTED_INDIVIDUAL_QUERY = """
query individual($id: ID!) {
  individual(id: $id) {
    birthDate
        familyName
        fullName
        givenName
        phoneNo
        email
  }
}
"""


class TestImportedIndividualQuery(APITestCase):
    databases = "__all__"
    fixtures = (f"{settings.PROJECT_ROOT}/apps/geo/fixtures/data.json",)

    # IMPORTANT!
    # FREEZGUN doesn't work this snapshot have to be updated once a year
    MAX_AGE = 51
    MIN_AGE = 37

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        create_afghanistan()
        cls.partner = PartnerFactory(name="Test1")
        cls.user = UserFactory.create(partner=cls.partner)
        cls.program = ProgramFactory(name="Program_1", status="ACTIVE")
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")
        ProgramPartnerThrough.objects.create(
            program=cls.program,
            partner=cls.partner,
            full_area_access=True,
        )
        cls.individuals_to_create = [
            {
                "full_name": "Benjamin Butler",
                "given_name": "Benjamin",
                "family_name": "Butler",
                "phone_no": "(953)682-4596",
                "email": "myemail111@mail.com",
                "birth_date": "1943-07-30",
                "sex": "MALE",
                "id": "47dd625a-e64e-48a9-bfcd-e970ca356bf7",
                "program": cls.program,
            },
            {
                "full_name": "Robin Ford",
                "given_name": "Robin",
                "family_name": "Ford",
                "phone_no": "+18663567905",
                "email": "myemail222@mail.com",
                "birth_date": "1946-02-15",
                "sex": "MALE",
                "id": "f91eb18b-175a-495c-a49d-92af4ad554ba",
                "program": cls.program,
            },
            {
                "full_name": "Timothy Perry",
                "given_name": "Timothy",
                "family_name": "Perry",
                "phone_no": "(548)313-1700-902",
                "email": "myemail333@mail.com",
                "birth_date": "1983-12-21",
                "sex": "MALE",
                "id": "4174aa63-4d3d-416a-bf39-09bc0e14e7c6",
                "program": cls.program,
            },
            {
                "full_name": "Eric Torres",
                "given_name": "Eric",
                "family_name": "Torres",
                "phone_no": "(228)231-5473",
                "email": "myemail444@mail.com",
                "birth_date": "1973-03-23",
                "sex": "MALE",
                "id": "6aada701-4639-4142-92ca-7cbf82411534",
                "program": cls.program,
            },
            {
                "full_name": "Jenna Franklin",
                "given_name": "Jenna",
                "family_name": "Franklin",
                "phone_no": "001-296-358-5428-607",
                "email": "myemail555@mail.com",
                "birth_date": "1969-11-29",
                "sex": "FEMALE",
                "id": "c38fa2a5-e518-495c-988f-c308c94dcc53",
                "program": cls.program,
            },
        ]

        cls.individuals = [
            IndividualFactory(**individual, rdi_merge_status=MergeStatusModel.PENDING)
            for individual in cls.individuals_to_create
        ]
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
    def test_imported_individual_query(self, _: Any, permissions: List[Permissions], query: str) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=query,
            context={
                "user": self.user,
                "headers": {
                    "Business-Area": self.business_area.slug,
                    "Program": self.id_to_base64(self.program.id, "ProgramNode"),
                },
            },
        )

    @parameterized.expand(
        [
            ("with_permission", [Permissions.RDI_VIEW_DETAILS]),
            ("without_permission", []),
        ]
    )
    def test_imported_individual_query_single(self, _: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=IMPORTED_INDIVIDUAL_QUERY,
            context={
                "user": self.user,
                "headers": {
                    "Business-Area": self.business_area.slug,
                    "Program": self.id_to_base64(self.program.id, "ProgramNode"),
                },
            },
            variables={
                "id": self.id_to_base64(
                    self.individuals[0].id,
                    "IndividualNode",
                )
            },
        )
