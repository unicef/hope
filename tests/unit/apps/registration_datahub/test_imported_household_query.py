from typing import Any, List

from django.conf import settings
from django.core.management import call_command

from parameterized import parameterized

from tests.extras.test_utils.factories.account import PartnerFactory, UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.models import BusinessArea
from tests.extras.test_utils.factories.geo import CountryFactory
from hct_mis_api.apps.geo.models import Country
from tests.extras.test_utils.factories.household import (
    HouseholdFactory,
    PendingDocumentFactory,
    PendingHouseholdFactory,
    PendingIndividualFactory,
)
from tests.extras.test_utils.factories.program import ProgramFactory
from hct_mis_api.apps.program.models import ProgramPartnerThrough
from hct_mis_api.apps.utils.models import MergeStatusModel


class TestImportedHouseholdQuery(APITestCase):
    databases = "__all__"
    fixtures = (f"{settings.PROJECT_ROOT}/apps/geo/fixtures/data.json",)

    ALL_IMPORTED_HOUSEHOLD_QUERY = """
    query allHouseholds{
      allHouseholds(businessArea: "afghanistan", orderBy: "size", rdiMergeStatus: "PENDING") {
        edges {
          node {
            size
            countryOrigin
            address
          }
        }
      }
    }
    """
    IMPORTED_HOUSEHOLD_QUERY = """
    query Household($id: ID!) {
      household(id: $id) {
        size
        countryOrigin
        address
      }
    }
    """

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        call_command("loadbusinessareas")
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")
        cls.partner = PartnerFactory(name="TEST1")
        cls.user = UserFactory.create(partner=cls.partner)
        cls.program = ProgramFactory(name="Program_1", status="ACTIVE")
        ProgramPartnerThrough.objects.create(
            program=cls.program,
            partner=cls.partner,
            full_area_access=True,
        )
        sizes_list = (2, 4, 5, 1, 3, 11, 14)
        cls.households = [
            HouseholdFactory(
                size=size,
                address="Lorem Ipsum",
                country_origin=Country.objects.get(iso_code2="PL"),
                rdi_merge_status=MergeStatusModel.PENDING,
                program=cls.program,
            )
            for size in sizes_list
        ]
        for household in cls.households:
            household.registration_data_import.business_area_slug = "afghanistan"
            household.registration_data_import.save()

    @parameterized.expand(
        [
            (
                "with_permission",
                [Permissions.RDI_VIEW_DETAILS],
            ),
            (
                "without_permission",
                [],
            ),
        ]
    )
    def test_imported_household_query_all(self, _: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=self.ALL_IMPORTED_HOUSEHOLD_QUERY,
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
            (
                "with_permission",
                [Permissions.RDI_VIEW_DETAILS],
            ),
            (
                "without_permission",
                [],
            ),
        ]
    )
    def test_imported_household_query_single(self, _: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        self.snapshot_graphql_request(
            request_string=self.IMPORTED_HOUSEHOLD_QUERY,
            context={
                "user": self.user,
                "headers": {
                    "Business-Area": self.business_area.slug,
                    "Program": self.id_to_base64(self.program.id, "ProgramNode"),
                },
            },
            variables={"id": self.id_to_base64(self.households[0].id, "HouseholdNode")},
        )

    @parameterized.expand(
        [
            ("detail_id", "test123", "HH-12344"),
            ("enumerator_rec_id", 123, "HH-12355"),
        ]
    )
    def test_imported_household_query(self, field_name: str, value: Any, hh_unicef_id: str) -> None:
        self.create_user_role_with_permissions(self.user, [Permissions.RDI_VIEW_DETAILS], self.business_area)
        country = CountryFactory()
        hh = PendingHouseholdFactory(country=country, unicef_id=hh_unicef_id, program=self.program)
        setattr(hh, field_name, value)
        hh.save()
        ind = PendingIndividualFactory(
            unicef_id="IND-123",
            household=hh,
            phone_no="+48123123213",
            phone_no_alternative="+48123123213",
            phone_no_valid=True,
            phone_no_alternative_valid=True,
            detail_id="test123",
            preferred_language="en",
            program=self.program,
        )
        PendingDocumentFactory(individual=ind, country=country, photo="", program=self.program)

        query = """
        query household($id: ID!) {
          household(id: $id) {
            importId
            country
            individuals(rdiMergeStatus: "PENDING") {
              edges {
                node {
                  phoneNo
                  phoneNoAlternative
                  phoneNoValid
                  phoneNoAlternativeValid
                  importId
                  preferredLanguage
                  documents {
                    edges {
                      node {
                        photo
                        country
                      }
                    }
                  }
                }
              }
            }
          }
        }
        """

        self.snapshot_graphql_request(
            request_string=query,
            context={
                "user": self.user,
                "headers": {
                    "Business-Area": self.business_area.slug,
                    "Program": self.id_to_base64(self.program.id, "ProgramNode"),
                },
            },
            variables={"id": self.id_to_base64(hh.id, "HouseholdNode")},
        )
