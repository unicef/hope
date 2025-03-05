from hct_mis_api.apps.account.fixtures import PartnerFactory, UserFactory
from hct_mis_api.apps.account.models import Partner
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.household.fixtures import create_household_and_individuals
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program


class PartnerForGrievanceTest(APITestCase):
    PARTNER_FOR_GRIEVANCE_CHOICES_QUERY = """
    query partnerForGrievanceChoices ($householdId: ID, $individualId: ID) {
      partnerForGrievanceChoices (
        householdId: $householdId
        individualId: $individualId
        )
        {
        name
      }
    }
    """

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.business_area = create_afghanistan()
        cls.program = ProgramFactory(name="Test Program", status=Program.DRAFT, business_area=cls.business_area)
        cls.program_for_household = ProgramFactory(
            name="Test Program for Household", status=Program.DRAFT, business_area=cls.business_area
        )
        cls.household, individuals = create_household_and_individuals(
            household_data={
                "business_area": cls.business_area,
                "program_id": cls.program_for_household.pk,
            },
            individuals_data=[
                {
                    "business_area": cls.business_area,
                    "program_id": cls.program_for_household.pk,
                },
            ],
        )
        cls.individual = individuals[0]

        # UNICEF partner
        partner_unicef, _ = Partner.objects.get_or_create(name="UNICEF")
        unicef_hq, _ = Partner.objects.get_or_create(name="UNICEF HQ", parent=partner_unicef)
        cls.user = UserFactory(partner=unicef_hq, username="unicef_user")

        # partner with access to Test Program - should be returned if Program is passed or if neither program nor household/individual is passed
        # (because it has access to ANY program in this BA)
        partner_with_access_to_test_program = PartnerFactory(name="Partner with access to Test Program")
        cls.create_partner_role_with_permissions(
            partner_with_access_to_test_program, [], cls.business_area, cls.program
        )

        # partner with access to Test Program for Household - should be returned if Program is not passed and household/individual is passed or if neither program nor household/individual is passed
        # (because it has access to ANY program in this BA)
        partner_with_access_to_test_program_for_hh = PartnerFactory(
            name="Partner with access to Test Program for Household"
        )
        cls.create_partner_role_with_permissions(
            partner_with_access_to_test_program_for_hh, [], cls.business_area, cls.program_for_household
        )

        # partner with access to all programs - should be returned if neither program nor household/individual is passed
        # or if any program is passed or if household/individual is passed
        # (because it has access to all programs in this BA)
        partner_with_access_to_all_programs = PartnerFactory(name="Partner with with access to All Programs")
        cls.create_partner_role_with_permissions(
            partner_with_access_to_all_programs, [], cls.business_area, whole_business_area_access=True
        )

        # partner without access to any program in this BA - should not be returned in any case
        PartnerFactory(name="Partner Without Program Access")

    def test_partner_choices_with_program(self) -> None:
        self.snapshot_graphql_request(
            request_string=self.PARTNER_FOR_GRIEVANCE_CHOICES_QUERY,
            context={
                "user": self.user,
                "headers": {
                    "Business-Area": self.business_area.slug,
                    "Program": self.id_to_base64(self.program.id, "ProgramNode"),
                },
            },
        )

    def test_partner_choices_without_program_but_with_household(self) -> None:
        self.snapshot_graphql_request(
            request_string=self.PARTNER_FOR_GRIEVANCE_CHOICES_QUERY,
            context={"user": self.user, "headers": {"Business-Area": self.business_area.slug}},
            variables={"householdId": self.id_to_base64(self.household.id, "HouseholdNode")},
        )

    def test_partner_choices_without_program_but_with_individual(self) -> None:
        self.snapshot_graphql_request(
            request_string=self.PARTNER_FOR_GRIEVANCE_CHOICES_QUERY,
            context={"user": self.user, "headers": {"Business-Area": self.business_area.slug}},
            variables={"individualId": self.id_to_base64(self.individual.id, "IndividualNode")},
        )

    def test_partner_choices_without_program_and_without_household_and_individual(self) -> None:
        self.snapshot_graphql_request(
            request_string=self.PARTNER_FOR_GRIEVANCE_CHOICES_QUERY,
            context={"user": self.user, "headers": {"Business-Area": self.business_area.slug}},
        )
