from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TransactionTestCase

from hct_mis_api.apps.account.fixtures import (
    PartnerFactory,
    RoleAssignmentFactory,
    RoleFactory,
    UserFactory, AdminAreaLimitedToFactory,
)
from hct_mis_api.apps.account.models import RoleAssignment, AdminAreaLimitedTo
from hct_mis_api.apps.core.fixtures import create_afghanistan, create_ukraine
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
        self.partner.allowed_business_areas.add(self.business_area)
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

        self.area_1 = AreaFactory(name="Area 1", p_code="AREA1")

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

    def test_partner_role_in_business_area_vs_allowed_business_areas(self) -> None:
        # Possible to create RoleAssignment for a business area that is allowed for the partner
        RoleAssignment.objects.create(
            user=None,
            partner=self.partner,
            role=self.role,
            business_area=self.business_area,
        )

        # Partner with a different business area should raise a validation error
        not_allowed_ba = create_ukraine()
        with self.assertRaises(ValidationError) as ve_context:
            RoleAssignment.objects.create(
                user=None,
                partner=self.partner,
                role=self.role,
                business_area=not_allowed_ba,
            )
        self.assertIn(
            f"{not_allowed_ba} is not within the allowed business areas for {self.partner}.",
            str(ve_context.exception),
        )

        # Validation not relevant for user
        RoleAssignment.objects.create(
            user=self.user,
            partner=None,
            role=self.role,
            business_area=not_allowed_ba,
        )

    def test_unique_user_role_business_area_program_constraint(self) -> None:
        # Creating a second role assignment with the same user, role, business area, and program should raise an error
        role_new = RoleFactory(name="Test Role Duplicate")
        RoleAssignment.objects.create(
            user=self.user,
            partner=None,
            role=role_new,
            business_area=self.business_area,
            program=self.program1,
        )
        with self.assertRaises(IntegrityError):
            RoleAssignment.objects.create(
                user=self.user,
                partner=None,
                role=role_new,
                business_area=self.business_area,
                program=self.program1,
            )

        RoleAssignment.objects.create(
            user=self.user,
            partner=None,
            role=role_new,
            business_area=self.business_area,
            program=None,
        )
        with self.assertRaises(IntegrityError):
            RoleAssignment.objects.create(
                user=self.user,
                partner=None,
                role=role_new,
                business_area=self.business_area,
                program=None,
            )

    def test_unique_partner_role_business_area_program_constraint(self) -> None:
        # Creating a second role assignment with the same partner, role, business area, and program should raise an error
        role_new = RoleFactory(name="Test Role Duplicate")
        RoleAssignment.objects.create(
            user=None,
            partner=self.partner,
            role=role_new,
            business_area=self.business_area,
            program=self.program1,
        )
        with self.assertRaises(IntegrityError):
            RoleAssignment.objects.create(
                user=None,
                partner=self.partner,
                role=role_new,
                business_area=self.business_area,
                program=self.program1,
            )

        RoleAssignment.objects.create(
            user=None,
            partner=self.partner,
            role=role_new,
            business_area=self.business_area,
            program=None,
        )
        with self.assertRaises(IntegrityError):
            RoleAssignment.objects.create(
                user=None,
                partner=self.partner,
                role=role_new,
                business_area=self.business_area,
                program=None,
            )

    def test_role_assignment_for_parent_partner(self) -> None:
        parent_partner = PartnerFactory(name="Parent Partner")
        child_partner = PartnerFactory(name="Child Partner", parent=parent_partner)
        parent_partner.allowed_business_areas.add(self.business_area)
        child_partner.allowed_business_areas.add(self.business_area)

        # Can create RoleAssignment for child partner
        RoleAssignment.objects.create(
            user=None,
            partner=child_partner,
            role=self.role,
            business_area=self.business_area,
        )

        with self.assertRaises(ValidationError) as ve_context:
            RoleAssignment.objects.create(
                user=None,
                partner=parent_partner,
                role=self.role,
                business_area=self.business_area,
            )
        self.assertIn(
            f"{parent_partner} is a parent partner and cannot have role assignments.",
            str(ve_context.exception),
        )

    def test_parent_partner_with_role_assignment(self) -> None:
        parent_partner = PartnerFactory(name="Parent Partner")
        parent_partner.allowed_business_areas.add(self.business_area)

        # Role for the Partner
        RoleAssignment.objects.create(
            user=None,
            partner=parent_partner,
            role=self.role,
            business_area=self.business_area,
        )

        with self.assertRaises(ValidationError) as ve_context:
            PartnerFactory(name="Child Partner", parent=parent_partner)

        self.assertIn(
            f"{parent_partner} cannot become a parent as it has RoleAssignments.",
            str(ve_context.exception),
        )

    def test_area_limits_for_program_with_selected_partner_access(self) -> None:
        # Possible to have area limits for a program with selected partner access
        self.program1.partner_access = Program.SELECTED_PARTNERS_ACCESS
        self.program1.save()

        AdminAreaLimitedToFactory(
            partner=self.partner,
            program=self.program1,
            areas=[self.area_1]
        )

    def test_area_limits_for_program_with_all_partner_access(self) -> None:
        # Not possible to have area limits for a program with ALL_PARTNERS_ACCESS
        self.program1.partner_access = Program.ALL_PARTNERS_ACCESS
        self.program1.save()
        with self.assertRaises(ValidationError) as ve_context:
            AdminAreaLimitedToFactory(
                partner=self.partner,
                program=self.program1,
                areas=[self.area_1]
            )
        self.assertIn(
            f"Area limits cannot be set for programs with {self.program1.partner_access} access.",
            str(ve_context.exception),
        )

    def test_area_limits_for_program_with_none_partner_access(self) -> None:
        # Not possible to have area limits for a program with NONE_PARTNERS_ACCESS
        self.program1.partner_access = Program.NONE_PARTNERS_ACCESS
        self.program1.save()
        with self.assertRaises(ValidationError) as ve_context:
            AdminAreaLimitedToFactory(
                partner=self.partner,
                program=self.program1,
                areas=[self.area_1]
            )
        self.assertIn(
            f"Area limits cannot be set for programs with {self.program1.partner_access} access.",
            str(ve_context.exception),
        )
