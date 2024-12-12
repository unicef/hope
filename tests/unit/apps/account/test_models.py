from django.core.exceptions import ValidationError
from django.test import TransactionTestCase

from hct_mis_api.apps.account.fixtures import RoleFactory, UserFactory, RoleAssignmentFactory, PartnerFactory
from hct_mis_api.apps.account.models import RoleAssignment
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.geo.fixtures import AreaFactory
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

    def test_unique_user_role_assignment(self) -> None:
       # Not possible to have the same role assigned to the same user in the same BA
        with self.assertRaises(ValidationError) as ve_context:
            RoleAssignment.objects.create(
                user=self.user,
                role=self.role,
                business_area=self.business_area,
            )
        self.assertIn(
            "This role is already assigned to the user in the business area.",
            str(ve_context.exception),
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
            'Either user or partner must be set, but not both.',
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
            'Either user or partner must be set, but not both.',
            str(ve_context.exception),
        )

    def test_program_and_areas_only_for_partner(self) -> None:
        # Only partner can have program assigned
        with self.assertRaises(ValidationError) as ve_context:
            RoleAssignment.objects.create(
                user=self.user,
                partner=None,
                role=self.role2,
                business_area=self.business_area,
                program=self.program1,
            )
        self.assertIn(
            'Program and areas can only be assigned for partner roles; not for user roles.',
            str(ve_context.exception),
        )

        # Only partner can have areas assigned
        area = AreaFactory(name="Test Area")
        role_assignment = RoleAssignment.objects.create(
            user=self.user,
            partner=None,
            role=self.role2,
            business_area=self.business_area,
            program=None,
        )
        with self.assertRaises(ValidationError) as ve_context:
            role_assignment.areas.add(area)
            role_assignment.save()
        self.assertIn(
            'Program and areas can only be assigned for partner roles; not for user roles.',
            str(ve_context.exception),
        )

        # Partner can have program and areas assigned
        role_assignment = RoleAssignment.objects.create(
            user=None,
            partner=self.partner,
            role=self.role2,
            business_area=self.business_area,
            program=self.program1,
        )
        self.assertIsNotNone(role_assignment.id)

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
            'Partner can only be assigned roles that are available for partners.',
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
