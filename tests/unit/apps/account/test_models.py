from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TransactionTestCase

from hct_mis_api.apps.account.fixtures import RoleFactory, UserFactory, RoleAssignmentFactory, PartnerFactory
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

    def test_unique_user_role_assignment(self) -> None:
       # Not possible to have the same role assigned to the same user in the same BA
        with self.assertRaises(IntegrityError) as ie_context:
            RoleAssignment.objects.create(
                user=self.user,
                role=self.role,
                business_area=self.business_area,
            )
        self.assertIn(
            'duplicate key value violates unique constraint "unique_user_role_assignment"',
            str(ie_context.exception),
        )

       # Possible to have the same role assigned to the same partner in the same BA (not failing for two records with user=None)
        RoleAssignment.objects.create(
            user=None,
            role=self.role,
            business_area=self.business_area,
            partner=self.partner,
            program=self.program1,
        )

        RoleAssignment.objects.create(
            user=None,
            role=self.role,
            business_area=self.business_area,
            partner=self.partner,
            program=self.program2,
        )
        self.assertEqual(RoleAssignment.objects.filter(role=self.role, business_area=self.business_area, partner=self.partner).count(), 2)

    def test_user_or_partner_not_both(self) -> None:
        # Not possible to have both user and partner in the same role assignment
        with self.assertRaises(ValidationError) as ve_context:
            RoleAssignment.objects.create(
                user=self.user,
                role=self.role,
                business_area=self.business_area,
                partner=self.partner,
                program=self.program1,
            )
        self.assertIn(
            'Either user or partner must be set, but not both.',
            str(ve_context.exception),
        )
