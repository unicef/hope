from django.core.exceptions import ValidationError
from django.test import TransactionTestCase

from hct_mis_api.apps.account.fixtures import (
    PartnerFactory,
    RoleAssignmentFactory,
    RoleFactory,
    UserFactory,
)
from hct_mis_api.apps.account.models import RoleAssignment
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program


class TestRoleAssignmentModel(TransactionTestCase):
    def setUp(self) -> None:
        self.business_area = create_afghanistan()
        self.role = RoleFactory(
            name="Test Role",
            permissions=["PROGRAMME_CREATE", "PROGRAMME_FINISH"],
        )
        self.role2 = RoleFactory(
            name="Test Role 2",
            permissions=["PROGRAMME_UPDATE"],
        )
        self.user = UserFactory(first_name="Test", last_name="User")
        self.partner = PartnerFactory(name="Partner")
        self.program1 = ProgramFactory(
            business_area=self.business_area,
            name="Program 1",
            status=Program.ACTIVE,
        )
        self.program2 = ProgramFactory(
            business_area=self.business_area,
            name="Program 2",
            status=Program.ACTIVE,
        )
        RoleAssignmentFactory(
            user=self.user,
            role=self.role,
            business_area=self.business_area,
        )

    def test_user_or_partner(self) -> None:
        # Either user or partner must be set
        with self.assertRaises(ValidationError) as ve_context:
            RoleAssignment.objects.create(
                user=None,
                partner=None,
                role=self.role2,
                business_area=self.business_area,
            )
        self.assertIn(
            "Either user or partner must be set, but not both.",
            str(ve_context.exception),
        )

    def test_user_or_partner_not_both(self) -> None:
        # Not possible to have both user and partner in the same role assignment
        with self.assertRaises(ValidationError) as ve_context:
            RoleAssignment.objects.create(
                user=self.user,
                role=self.role2,
                business_area=self.business_area,
                partner=self.partner,
                program=self.program1,
            )
        self.assertIn(
            "Either user or partner must be set, but not both.",
            str(ve_context.exception),
        )

    def test_is_available_for_partner_flag(self) -> None:
        # is_available_for_partner flag is set to True
        role_assignment = RoleAssignment.objects.create(
            user=None,
            partner=self.partner,
            role=self.role2,
            business_area=self.business_area,
        )
        self.assertIsNotNone(role_assignment.id)

        # is_available_for_partner flag is set to False
        self.role2.is_available_for_partner = False
        self.role2.save()
        with self.assertRaises(ValidationError) as ve_context:
            RoleAssignment.objects.create(
                user=None,
                partner=self.partner,
                role=self.role2,
                business_area=self.business_area,
            )
        self.assertIn(
            "Partner can only be assigned roles that are available for partners.",
            str(ve_context.exception),
        )

        # user can be assigned the role despite the flag
        role_assignment_user = RoleAssignment.objects.create(
            user=self.user,
            partner=None,
            role=self.role2,
            business_area=self.business_area,
        )
        self.assertIsNotNone(role_assignment_user.id)
