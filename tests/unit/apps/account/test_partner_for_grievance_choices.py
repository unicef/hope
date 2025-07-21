from tests.extras.test_utils.factories.account import PartnerFactory, UserFactory
from hct_mis_api.apps.account.models import Partner, Role
from hct_mis_api.apps.core.base_test_case import APITestCase
from tests.extras.test_utils.factories.core import create_afghanistan
from tests.extras.test_utils.factories.household import create_household_and_individuals
from tests.extras.test_utils.factories.program import ProgramFactory
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
        cls.program_any = ProgramFactory(name="Test Program Any", status=Program.DRAFT, business_area=cls.business_area)
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
        cls.user = UserFactory(partner=partner_unicef, username="unicef_user")

        # partner with access to Test Program - should be returned if Program is passed or if neither program nor household/individual is passed
        # (because it has access to ANY program in this BA)
        partner_with_access_to_test_program = PartnerFactory(name="Partner with access to Test Program")
        cls.update_partner_access_to_program(partner_with_access_to_test_program, cls.program)

        # partner with access to Test Program for Household - should be returned if Program is not passed and household/individual is passed or if neither program nor household/individual is passed
        # (because it has access to ANY program in this BA)
        partner_with_access_to_test_program_for_hh = PartnerFactory(
            name="Partner with access to Test Program for Household"
        )
        cls.update_partner_access_to_program(partner_with_access_to_test_program_for_hh, cls.program_for_household)

        # partner with access to Test Program Any - should be returned if  neither program nor household/individual is passed
        # (because it has access to ANY program in this BA)
        partner_with_access_to_test_program_any = PartnerFactory(name="Partner with with access to Test Program Any")
        cls.update_partner_access_to_program(partner_with_access_to_test_program_any, cls.program_any)

        # partner without access to any program in this BA (but with role, which should not matter) - should not be returned in any case
        role = Role.objects.create(name="Partner role")
        partner_without_program_access = PartnerFactory(name="Partner Without Program Access")
        cls.add_partner_role_in_business_area(partner_without_program_access, cls.business_area, [role])

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
