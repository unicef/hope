from django.urls import reverse
from django_webtest import WebTest
import pytest

from extras.test_utils.factories.account import (
    PartnerFactory,
    RoleAssignmentFactory,
    UserFactory,
)
from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.geo import AreaFactory, AreaTypeFactory
from extras.test_utils.factories.program import ProgramFactory
from hope.apps.account.models import AdminAreaLimitedTo, Partner, RoleAssignment
from hope.apps.geo.models import Area

pytestmark = pytest.mark.django_db()


class ProgramAdminTest(WebTest):
    csrf_checks = False

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.user = UserFactory(username="adminuser", is_staff=True, is_superuser=True)
        cls.business_area = create_afghanistan()
        cls.program = ProgramFactory(business_area=cls.business_area)
        cls.url = reverse("admin:program_program_area_limits", args=[cls.program.pk])

        area_type = AreaTypeFactory(name="State1", area_level=1)
        cls.admin_area1 = AreaFactory(
            name=f"{cls.business_area.slug} city 1",
            p_code=f"{cls.business_area.slug} 1",
            area_type=area_type,
        )
        cls.admin_area2 = AreaFactory(
            name=f"{cls.business_area.slug} city 2",
            p_code=f"{cls.business_area.slug} 2",
            area_type=area_type,
        )
        cls.admin_area3 = AreaFactory(
            name=f"{cls.business_area.slug} city 3",
            p_code=f"{cls.business_area.slug} 3",
            area_type=area_type,
        )
        cls.unicef = PartnerFactory(name="UNICEF")
        cls.unicef_hq = PartnerFactory(name="UNICEF HQ", parent=cls.unicef)
        cls.partner_without_role = PartnerFactory(name="Partner without role")
        cls.partner_with_role = PartnerFactory(name="Partner with role")

        RoleAssignment.objects.all().delete()
        RoleAssignmentFactory(
            partner=cls.partner_with_role,
            program=cls.program,
            business_area=cls.business_area,
        )

    def test_area_limits_get_request(self) -> None:
        response = self.app.get(self.url, user=self.user)
        assert response.status_code == 200
        assert "program_area_formset" in response.context
        assert "business_area" in response.context
        assert "areas" in response.context
        self.assertQuerysetEqual(
            response.context["areas"],
            Area.objects.filter(area_type__country__business_areas__id=self.program.business_area.id),
        )
        assert "partners" in response.context
        self.assertQuerysetEqual(
            response.context["partners"],
            Partner.objects.filter(id=self.partner_with_role.id),
        )
        assert "program" in response.context

    def test_area_limits_post_request_create(self) -> None:
        self.app.post(
            self.url,
            user=self.user,
            params={
                "program_areas-TOTAL_FORMS": "1",
                "program_areas-INITIAL_FORMS": "0",
                "program_areas-0-partner": self.partner_with_role.id,
                "program_areas-0-areas": [self.admin_area1.id, self.admin_area2.id],
            },
        )

        assert AdminAreaLimitedTo.objects.filter(partner=self.partner_with_role, program=self.program).exists()
        self.assertQuerysetEqual(
            AdminAreaLimitedTo.objects.get(partner=self.partner_with_role, program=self.program).areas.all(),
            Area.objects.filter(id__in=[self.admin_area1.id, self.admin_area2.id]),
        )

    def test_area_limits_post_request_edit(self) -> None:
        area_limit = AdminAreaLimitedTo.objects.create(partner=self.partner_with_role, program=self.program)
        area_limit.areas.set([self.admin_area1, self.admin_area2, self.admin_area3])
        self.app.post(
            self.url,
            user=self.user,
            params={
                "program_areas-TOTAL_FORMS": "1",
                "program_areas-INITIAL_FORMS": "1",
                "program_areas-0-partner": self.partner_with_role.id,
                "program_areas-0-areas": [self.admin_area1.id],
            },
        )
        assert AdminAreaLimitedTo.objects.filter(partner=self.partner_with_role, program=self.program).exists()
        self.assertQuerysetEqual(
            AdminAreaLimitedTo.objects.get(partner=self.partner_with_role, program=self.program).areas.all(),
            Area.objects.filter(id__in=[self.admin_area1.id]),
        )

    def test_area_limits_post_request_delete(self) -> None:
        area_limit = AdminAreaLimitedTo.objects.create(partner=self.partner_with_role, program=self.program)
        area_limit.areas.set([self.admin_area1, self.admin_area2, self.admin_area3])
        self.app.post(
            self.url,
            user=self.user,
            params={
                "program_areas-TOTAL_FORMS": "1",
                "program_areas-INITIAL_FORMS": "1",
                "program_areas-0-partner": self.partner_with_role.id,
                "program_areas-0-areas": [],
                "program_areas-0-DELETE": True,
            },
        )
        assert not AdminAreaLimitedTo.objects.filter(partner=self.partner_with_role, program=self.program).exists()
