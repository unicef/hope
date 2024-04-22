from typing import Any, List

from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import PartnerFactory, UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import (
    create_afghanistan,
    generate_data_collecting_types,
)
from hct_mis_api.apps.core.models import BusinessArea, DataCollectingType
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program, ProgramPartnerThrough


class TestAllProgramsQuery(APITestCase):
    ALL_PROGRAMS_QUERY = """
    query AllPrograms($businessArea: String!, $orderBy: String) {
        allPrograms(businessArea: $businessArea, orderBy: $orderBy) {
          totalCount
          edges {
            node {
              name
            }
          }
        }
      }
    """

    @classmethod
    def setUpTestData(cls) -> None:
        create_afghanistan()
        generate_data_collecting_types()
        data_collecting_type = DataCollectingType.objects.get(code="full_collection")
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")
        cls.business_area.data_collecting_types.set(DataCollectingType.objects.all().values_list("id", flat=True))

        cls.partner = PartnerFactory(name="WFP")
        cls.user = UserFactory.create(partner=cls.partner)

        cls.unicef_partner = PartnerFactory(name="UNICEF")
        other_partner = PartnerFactory(name="Other Partner")

        program_with_partner_access = ProgramFactory.create(
            name="Program with partner access",
            status=Program.DRAFT,
            business_area=cls.business_area,
            data_collecting_type=data_collecting_type,
            partner_access=Program.SELECTED_PARTNERS_ACCESS,
        )
        ProgramPartnerThrough.objects.create(
            program=program_with_partner_access,
            partner=cls.partner,
        )
        ProgramPartnerThrough.objects.create(
            program=program_with_partner_access,
            partner=cls.unicef_partner,
        )

        program_with_all_partners_access = ProgramFactory.create(
            name="Program with all partners access",
            status=Program.ACTIVE,
            business_area=cls.business_area,
            data_collecting_type=data_collecting_type,
            partner_access=Program.ALL_PARTNERS_ACCESS,
        )
        ProgramPartnerThrough.objects.create(
            program=program_with_all_partners_access,
            partner=cls.partner,
        )
        ProgramPartnerThrough.objects.create(
            program=program_with_all_partners_access,
            partner=cls.unicef_partner,
        )
        ProgramPartnerThrough.objects.create(
            program=program_with_all_partners_access,
            partner=other_partner,
        )

        program_with_none_partner_access = ProgramFactory.create(
            name="Program with none partner access",
            status=Program.ACTIVE,
            business_area=cls.business_area,
            data_collecting_type=data_collecting_type,
            partner_access=Program.NONE_PARTNERS_ACCESS,
        )
        ProgramPartnerThrough.objects.create(
            program=program_with_none_partner_access,
            partner=cls.unicef_partner,
        )

        program_without_partner_access = ProgramFactory.create(
            name="Program without partner access",
            status=Program.ACTIVE,
            business_area=cls.business_area,
            data_collecting_type=data_collecting_type,
            partner_access=Program.SELECTED_PARTNERS_ACCESS,
        )
        ProgramPartnerThrough.objects.create(
            program=program_without_partner_access,
            partner=cls.unicef_partner,
        )
        ProgramPartnerThrough.objects.create(
            program=program_without_partner_access,
            partner=other_partner,
        )

    @parameterized.expand(
        [
            ("with_permission", [Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS]),
            ("without_permission", []),
        ]
    )
    def test_all_programs_query(self, _: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)
        self.snapshot_graphql_request(
            request_string=self.ALL_PROGRAMS_QUERY,
            context={
                "user": self.user,
                "headers": {
                    "Business-Area": self.business_area.slug,
                },
            },
            variables={"businessArea": self.business_area.slug, "orderBy": "name"},
        )

    def test_all_programs_query_unicef_partner(self) -> None:
        user = UserFactory.create(partner=self.unicef_partner)
        # granting any role in the business area to the user; permission to view programs is inherited from the unicef partner
        self.create_user_role_with_permissions(user, [Permissions.RDI_MERGE_IMPORT], self.business_area)
        self.snapshot_graphql_request(
            request_string=self.ALL_PROGRAMS_QUERY,
            context={
                "user": user,
                "headers": {
                    "Business-Area": self.business_area.slug,
                },
            },
            variables={"businessArea": self.business_area.slug, "orderBy": "name"},
        )
