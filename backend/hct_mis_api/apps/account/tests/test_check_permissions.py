from django.contrib.auth.models import AnonymousUser
from django.test import TestCase

from hct_mis_api.apps.account.fixtures import PartnerFactory, RoleFactory, UserFactory
from hct_mis_api.apps.account.models import PartnerPermission, Role, User, UserRole
from hct_mis_api.apps.account.permissions import Permissions, check_permissions
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.utils import encode_id_base64_required
from hct_mis_api.apps.geo.fixtures import AreaFactory
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program


class TestCheckPermissions(TestCase):
    user: User
    business_area: BusinessArea
    program: Program
    role: Role

    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = UserFactory()
        cls.business_area = create_afghanistan()
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

    def test_user_is_unicef_and_has_access_to_business_area(self) -> None:
        partner = PartnerFactory(name="UNICEF")
        self.user.partner = partner
        self.user.save()
        UserRole.objects.create(business_area=self.business_area, user=self.user, role=self.role)

        arguments = {
            "business_area": self.business_area.slug,
            "Program": encode_id_base64_required(self.program.id, "Program"),
        }
        result = check_permissions(self.user, [Permissions.POPULATION_VIEW_INDIVIDUALS_DETAILS], **arguments)
        self.assertTrue(result)

    def test_user_is_unicef_and_does_not_have_access_to_business_area(self) -> None:
        partner = PartnerFactory(name="UNICEF")
        self.user.partner = partner
        self.user.save()
        arguments = {
            "business_area": self.business_area.slug,
            "Program": encode_id_base64_required(self.program.id, "Program"),
        }
        result = check_permissions(self.user, [Permissions.POPULATION_VIEW_INDIVIDUALS_DETAILS], **arguments)
        self.assertFalse(result)

    def test_user_is_not_unicef_and_has_access_to_business_area_without_access_to_program(self) -> None:
        partner = PartnerFactory(name="Partner")
        self.user.partner = partner
        self.user.save()

        UserRole.objects.create(business_area=self.business_area, user=self.user, role=self.role)

        arguments = {
            "business_area": self.business_area.slug,
            "Program": encode_id_base64_required(self.program.id, "Program"),
        }
        result = check_permissions(self.user, [Permissions.POPULATION_VIEW_INDIVIDUALS_DETAILS], **arguments)
        self.assertFalse(result)

    def test_user_is_not_unicef_and_has_access_to_business_area_and_program(self) -> None:
        permissions = PartnerPermission()
        permissions.set_program_areas(self.business_area.pk, self.program.pk, [str(self.area.pk)])
        partner = PartnerFactory(name="Partner", permissions=permissions.to_dict())
        self.user.partner = partner
        self.user.save()

        UserRole.objects.create(business_area=self.business_area, user=self.user, role=self.role)

        arguments = {
            "business_area": self.business_area.slug,
            "Program": encode_id_base64_required(self.program.id, "Program"),
        }
        result = check_permissions(self.user, [Permissions.POPULATION_VIEW_INDIVIDUALS_DETAILS], **arguments)
        self.assertTrue(result)

    def test_user_is_not_unicef_and_dont_have_access_to_business_area_but_has_access_to_business_area_via_partner(
        self,
    ) -> None:
        permissions = PartnerPermission()
        permissions.set_program_areas(self.business_area.pk, self.program.pk, [str(self.area.pk)])
        permissions.set_roles(self.business_area.pk, [str(self.role.pk)])
        partner = PartnerFactory(name="Partner", permissions=permissions.to_dict())
        self.user.partner = partner
        self.user.save()

        arguments = {
            "business_area": self.business_area.slug,
            "Program": encode_id_base64_required(self.program.id, "Program"),
        }
        result = check_permissions(self.user, [Permissions.POPULATION_VIEW_INDIVIDUALS_DETAILS], **arguments)
        self.assertTrue(result)

    def test_user_is_not_unicef_and_dont_have_access_to_business_area_at_all(self) -> None:
        permissions = PartnerPermission()
        permissions.set_program_areas(self.business_area.pk, self.program.pk, [str(self.area.pk)])
        partner = PartnerFactory(name="Partner", permissions=permissions.to_dict())
        self.user.partner = partner
        self.user.save()

        arguments = {
            "business_area": self.business_area.slug,
            "Program": encode_id_base64_required(self.program.id, "Program"),
        }
        result = check_permissions(self.user, [Permissions.POPULATION_VIEW_INDIVIDUALS_DETAILS], **arguments)
        self.assertFalse(result)
