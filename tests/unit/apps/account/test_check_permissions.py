from django.contrib.auth.models import AnonymousUser
from django.test import TestCase

from hct_mis_api.apps.account.fixtures import PartnerFactory, RoleFactory, UserFactory
from hct_mis_api.apps.account.models import Role, RoleAssignment, User
from hct_mis_api.apps.account.permissions import Permissions, check_permissions
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea, BusinessAreaPartnerThrough
from hct_mis_api.apps.core.utils import encode_id_base64_required
from hct_mis_api.apps.geo.fixtures import AreaFactory
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program, ProgramPartnerThrough


class TestCheckPermissions(TestCase):
    user: User
    business_area: BusinessArea
    program: Program
    role: Role

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.user = UserFactory()
        cls.business_area = create_afghanistan()

        role_with_all_permissions = RoleFactory(name="Role with all permissions")
        role_with_all_permissions.permissions = [Permissions.POPULATION_VIEW_INDIVIDUALS_DETAILS.value]
        role_with_all_permissions.save()

        cls.program = ProgramFactory(status=Program.DRAFT, business_area=cls.business_area)
        cls.role = RoleFactory(
            name="POPULATION VIEW INDIVIDUALS DETAILS", permissions=["POPULATION_VIEW_INDIVIDUALS_DETAILS"]
        )
        cls.area = AreaFactory(name="POPULATION")

    def test_user_is_not_authenticated(self) -> None:
        user = AnonymousUser()
        self.assertFalse(check_permissions(user, [Permissions.POPULATION_VIEW_INDIVIDUALS_DETAILS]))

    def test_business_area_is_invalid(self) -> None:
        arguments = {"business_area": "invalid"}
        result = check_permissions(self.user, [Permissions.POPULATION_VIEW_INDIVIDUALS_DETAILS], **arguments)
        self.assertFalse(result)

    def test_user_is_unicef(self) -> None:
        unicef = PartnerFactory(name="UNICEF")
        partner = PartnerFactory(name="UNICEF HQ", parent=unicef)
        self.user.partner = partner
        self.user.save()

        arguments = {
            "business_area": self.business_area.slug,
            "Program": encode_id_base64_required(self.program.id, "Program"),
        }
        result = check_permissions(self.user, [Permissions.POPULATION_VIEW_INDIVIDUALS_DETAILS], **arguments)
        self.assertTrue(result)

    def test_user_is_not_unicef_and_has_permission_in_different_program(self) -> None:
        partner = PartnerFactory(name="Partner")
        self.user.partner = partner
        self.user.save()

        RoleAssignment.objects.create(
            user=self.user,
            business_area=self.business_area,
            role=self.role,
            program=ProgramFactory(business_area=self.business_area),
        )

        arguments = {
            "business_area": self.business_area.slug,
            "Program": encode_id_base64_required(self.program.id, "Program"),
        }
        result = check_permissions(self.user, [Permissions.POPULATION_VIEW_INDIVIDUALS_DETAILS], **arguments)
        self.assertFalse(result)

    def test_user_is_not_unicef_and_partner_has_permission_in_program(self) -> None:
        partner = PartnerFactory(name="Partner")
        partner.allowed_business_areas.add(self.business_area)
        RoleAssignment.objects.create(
            partner=partner, business_area=self.business_area, role=self.role, program=self.program
        )

        self.user.partner = partner
        self.user.save()

        arguments = {
            "business_area": self.business_area.slug,
            "Program": encode_id_base64_required(self.program.id, "Program"),
        }
        result = check_permissions(self.user, [Permissions.POPULATION_VIEW_INDIVIDUALS_DETAILS], **arguments)
        self.assertTrue(result)

    def test_user_is_not_unicef_and_user_has_permission_in_program(self) -> None:
        partner = PartnerFactory(name="Partner")
        self.user.partner = partner
        self.user.save()

        RoleAssignment.objects.create(
            user=self.user, business_area=self.business_area, role=self.role, program=self.program
        )

        arguments = {
            "business_area": self.business_area.slug,
            "Program": encode_id_base64_required(self.program.id, "Program"),
        }
        result = check_permissions(self.user, [Permissions.POPULATION_VIEW_INDIVIDUALS_DETAILS], **arguments)
        self.assertTrue(result)

    def test_user_is_not_unicef_and_partner_has_permission_in_whole_ba(self) -> None:
        partner = PartnerFactory(name="Partner")
        partner.allowed_business_areas.add(self.business_area)
        RoleAssignment.objects.create(partner=partner, business_area=self.business_area, role=self.role)

        self.user.partner = partner
        self.user.save()

        arguments = {
            "business_area": self.business_area.slug,
            "Program": encode_id_base64_required(self.program.id, "Program"),
        }
        result = check_permissions(self.user, [Permissions.POPULATION_VIEW_INDIVIDUALS_DETAILS], **arguments)
        self.assertTrue(result)

    def test_user_is_not_unicef_and_user_has_permission_in_whole_ba(self) -> None:
        partner = PartnerFactory(name="Partner")
        self.user.partner = partner
        self.user.save()

        RoleAssignment.objects.create(user=self.user, business_area=self.business_area, role=self.role)

        arguments = {
            "business_area": self.business_area.slug,
            "Program": encode_id_base64_required(self.program.id, "Program"),
        }
        result = check_permissions(self.user, [Permissions.POPULATION_VIEW_INDIVIDUALS_DETAILS], **arguments)
        self.assertTrue(result)
