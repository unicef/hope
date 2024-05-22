from django.conf import settings
from django.test import TestCase

from hct_mis_api.apps.account.fixtures import PartnerFactory, RoleFactory
from hct_mis_api.apps.core.fixtures import create_afghanistan, create_ukraine
from hct_mis_api.apps.geo.fixtures import AreaFactory, AreaTypeFactory, CountryFactory
from hct_mis_api.apps.geo.models import Area
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.one_time_scripts.migrate_partner_permissions_and_access import (
    migrate_partner_permissions_and_access,
)


class TestMigratePartnerPermissionsAndAccess(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.partner_unicef = PartnerFactory(name="UNICEF", permissions={})
        cls.afghanistan = create_afghanistan()
        cls.ukraine = create_ukraine()

        cls.program_in_afg_1 = ProgramFactory(name="Program in Afg 1", business_area=cls.afghanistan)
        cls.program_in_afg_2 = ProgramFactory(name="Program in Afg 2", business_area=cls.afghanistan)

        cls.program_in_ukr_1 = ProgramFactory(name="Program in Ukr 1", business_area=cls.ukraine)
        cls.program_in_ukr_2 = ProgramFactory(name="Program in Ukr 2", business_area=cls.ukraine)

        cls.role_in_afg_1 = RoleFactory(name="Role in Afg 1")
        cls.role_in_afg_2 = RoleFactory(name="Role in Afg 2")

        cls.role_in_ukr_1 = RoleFactory(name="Role in Ukr 1")
        cls.role_in_ukr_2 = RoleFactory(name="Role in Ukr 2")

        country_afg = CountryFactory(name="Afghanistan")
        country_afg.business_areas.set([cls.afghanistan])
        area_type_afg = AreaTypeFactory(name="Area Type in Afg", country=country_afg)
        country_ukr = CountryFactory(
            name="Ukraine",
            short_name="Ukraine",
            iso_code2="UA",
            iso_code3="UKR",
            iso_num="0804",
        )
        country_ukr.business_areas.set([cls.ukraine])
        area_type_ukr = AreaTypeFactory(name="Area Type in Ukr", country=country_ukr)

        cls.area_in_afg_1 = AreaFactory(name="Area in AFG 1", area_type=area_type_afg)
        cls.area_in_afg_2 = AreaFactory(name="Area in AFG 2", area_type=area_type_afg)
        cls.area_in_afg_3 = AreaFactory(name="Area in AFG 3", area_type=area_type_afg)

        cls.area_in_ukr_1 = AreaFactory(name="Area in Ukr 1", area_type=area_type_ukr)
        cls.area_in_ukr_2 = AreaFactory(name="Area in Ukr 2", area_type=area_type_ukr)

        cls.partner_default_empty = PartnerFactory(name=settings.DEFAULT_EMPTY_PARTNER, permissions={})

        perm_no_access = {
            str(cls.afghanistan.id): {"roles": [str(cls.role_in_afg_1.id), str(cls.role_in_afg_2.id)], "programs": {}},
            str(cls.ukraine.id): {"roles": [str(cls.role_in_ukr_2.id)], "programs": {}},
        }
        cls.partner_without_access = PartnerFactory(name="Partner without access", permissions=perm_no_access)

        perm_no_role = {
            str(cls.afghanistan.id): {
                "roles": [],
                "programs": {
                    str(cls.program_in_afg_1.pk): [str(cls.area_in_afg_1.id)],
                    str(cls.program_in_afg_2.pk): [],
                },
            },
            str(cls.ukraine.id): {
                "roles": [],
                "programs": {
                    str(cls.program_in_ukr_1.pk): [],
                    str(cls.program_in_ukr_2.pk): [str(cls.area_in_ukr_2.id)],
                },
            },
        }
        cls.partner_without_role = PartnerFactory(name="Partner without perm", permissions=perm_no_role)

        perm = {
            str(cls.afghanistan.id): {
                "roles": [str(cls.role_in_afg_1.id), str(cls.role_in_afg_2.id)],
                "programs": {
                    str(cls.program_in_afg_1.pk): [str(cls.area_in_afg_1.id)],
                    str(cls.program_in_afg_2.pk): [],
                },
            },
            str(cls.ukraine.id): {
                "roles": [str(cls.role_in_ukr_1.id), str(cls.role_in_ukr_2.id)],
                "programs": {
                    str(cls.program_in_ukr_1.pk): [],
                    str(cls.program_in_ukr_2.pk): [str(cls.area_in_ukr_1.id), str(cls.area_in_ukr_2.id)],
                },
            },
        }
        cls.partner = PartnerFactory(name="Partner", permissions=perm)

    def test_migrate_partner_permissions_and_access(self) -> None:
        migrate_partner_permissions_and_access()

        areas_count_in_afg = Area.objects.filter(area_type__country__business_areas=self.afghanistan).count()
        areas_count_in_ukr = Area.objects.filter(area_type__country__business_areas=self.ukraine).count()

        # Default Empty Partner - no access, no roles
        self.assertEqual(self.partner_default_empty.program_partner_through.count(), 0)
        self.assertEqual(self.partner_default_empty.business_area_partner_through.count(), 0)

        # UNICEF Partner - full area access to all programs, no roles
        self.assertEqual(self.partner_unicef.program_partner_through.count(), 4)
        self.assertEqual(self.partner_unicef.business_area_partner_through.count(), 0)
        self.assertEqual(
            self.partner_unicef.program_partner_through.filter(program=self.program_in_afg_1).first().full_area_access,
            True,
        )
        self.assertEqual(
            self.partner_unicef.program_partner_through.filter(program=self.program_in_afg_1).first().areas.count(),
            areas_count_in_afg,
        )
        self.assertIn(
            self.area_in_afg_1,
            self.partner_unicef.program_partner_through.filter(program=self.program_in_afg_1).first().areas.all(),
        )
        self.assertIn(
            self.area_in_afg_2,
            self.partner_unicef.program_partner_through.filter(program=self.program_in_afg_1).first().areas.all(),
        )
        self.assertIn(
            self.area_in_afg_3,
            self.partner_unicef.program_partner_through.filter(program=self.program_in_afg_1).first().areas.all(),
        )
        self.assertEqual(
            self.partner_unicef.program_partner_through.filter(program=self.program_in_afg_2).first().full_area_access,
            True,
        )
        self.assertEqual(
            self.partner_unicef.program_partner_through.filter(program=self.program_in_afg_2).first().areas.count(),
            areas_count_in_afg,
        )
        self.assertIn(
            self.area_in_afg_1,
            self.partner_unicef.program_partner_through.filter(program=self.program_in_afg_2).first().areas.all(),
        )
        self.assertIn(
            self.area_in_afg_2,
            self.partner_unicef.program_partner_through.filter(program=self.program_in_afg_2).first().areas.all(),
        )
        self.assertIn(
            self.area_in_afg_3,
            self.partner_unicef.program_partner_through.filter(program=self.program_in_afg_2).first().areas.all(),
        )
        self.assertEqual(
            self.partner_unicef.program_partner_through.filter(program=self.program_in_ukr_1).first().full_area_access,
            True,
        )
        self.assertEqual(
            self.partner_unicef.program_partner_through.filter(program=self.program_in_ukr_1).first().areas.count(),
            areas_count_in_ukr,
        )
        self.assertIn(
            self.area_in_ukr_1,
            self.partner_unicef.program_partner_through.filter(program=self.program_in_ukr_1).first().areas.all(),
        )
        self.assertIn(
            self.area_in_ukr_2,
            self.partner_unicef.program_partner_through.filter(program=self.program_in_ukr_1).first().areas.all(),
        )
        self.assertEqual(
            self.partner_unicef.program_partner_through.filter(program=self.program_in_ukr_2).first().full_area_access,
            True,
        )
        self.assertEqual(
            self.partner_unicef.program_partner_through.filter(program=self.program_in_ukr_2).first().areas.count(),
            areas_count_in_ukr,
        )
        self.assertIn(
            self.area_in_ukr_2,
            self.partner_unicef.program_partner_through.filter(program=self.program_in_ukr_2).first().areas.all(),
        )
        self.assertIn(
            self.area_in_ukr_2,
            self.partner_unicef.program_partner_through.filter(program=self.program_in_ukr_2).first().areas.all(),
        )

        # Partner without access - roles, no access
        self.assertEqual(self.partner_without_access.program_partner_through.count(), 0)
        self.assertEqual(self.partner_without_access.business_area_partner_through.count(), 2)
        self.assertEqual(
            self.partner_without_access.business_area_partner_through.filter(business_area=self.afghanistan)
            .first()
            .roles.count(),
            2,
        )
        self.assertIn(
            self.role_in_afg_1,
            self.partner_without_access.business_area_partner_through.filter(business_area=self.afghanistan)
            .first()
            .roles.all(),
        )
        self.assertIn(
            self.role_in_afg_2,
            self.partner_without_access.business_area_partner_through.filter(business_area=self.afghanistan)
            .first()
            .roles.all(),
        )
        self.assertEqual(
            self.partner_without_access.business_area_partner_through.filter(business_area=self.ukraine)
            .first()
            .roles.count(),
            1,
        )
        self.assertIn(
            self.role_in_ukr_2,
            self.partner_without_access.business_area_partner_through.filter(business_area=self.ukraine)
            .first()
            .roles.all(),
        )

        # Partner without role - access, no roles
        self.assertEqual(self.partner_without_role.program_partner_through.count(), 4)
        self.assertEqual(self.partner_without_role.business_area_partner_through.count(), 0)
        self.assertEqual(
            self.partner_without_role.program_partner_through.filter(program=self.program_in_afg_1)
            .first()
            .areas.count(),
            1,
        )
        self.assertIn(
            self.area_in_afg_1,
            self.partner_without_role.program_partner_through.filter(program=self.program_in_afg_1).first().areas.all(),
        )
        self.assertEqual(
            self.partner_without_role.program_partner_through.filter(program=self.program_in_afg_2)
            .first()
            .full_area_access,
            True,
        )
        self.assertEqual(
            self.partner_without_role.program_partner_through.filter(program=self.program_in_afg_2)
            .first()
            .areas.count(),
            areas_count_in_afg,
        )
        self.assertIn(
            self.area_in_afg_1,
            self.partner_without_role.program_partner_through.filter(program=self.program_in_afg_2).first().areas.all(),
        )
        self.assertIn(
            self.area_in_afg_2,
            self.partner_without_role.program_partner_through.filter(program=self.program_in_afg_2).first().areas.all(),
        )
        self.assertIn(
            self.area_in_afg_3,
            self.partner_without_role.program_partner_through.filter(program=self.program_in_afg_2).first().areas.all(),
        )
        self.assertEqual(
            self.partner_without_role.program_partner_through.filter(program=self.program_in_ukr_1)
            .first()
            .full_area_access,
            True,
        )
        self.assertEqual(
            self.partner_without_role.program_partner_through.filter(program=self.program_in_ukr_1)
            .first()
            .areas.count(),
            areas_count_in_ukr,
        )
        self.assertIn(
            self.area_in_ukr_1,
            self.partner_without_role.program_partner_through.filter(program=self.program_in_ukr_1).first().areas.all(),
        )
        self.assertIn(
            self.area_in_ukr_2,
            self.partner_without_role.program_partner_through.filter(program=self.program_in_ukr_1).first().areas.all(),
        )
        self.assertEqual(
            self.partner_without_role.program_partner_through.filter(program=self.program_in_ukr_2)
            .first()
            .areas.count(),
            1,
        )
        self.assertIn(
            self.area_in_ukr_2,
            self.partner_without_role.program_partner_through.filter(program=self.program_in_ukr_2).first().areas.all(),
        )

        # Partner - access, roles
        self.assertEqual(self.partner.program_partner_through.count(), 4)
        self.assertEqual(self.partner.business_area_partner_through.count(), 2)
        self.assertEqual(
            self.partner.business_area_partner_through.filter(business_area=self.afghanistan).first().roles.count(), 2
        )
        self.assertIn(
            self.role_in_afg_1,
            self.partner.business_area_partner_through.filter(business_area=self.afghanistan).first().roles.all(),
        )
        self.assertIn(
            self.role_in_afg_2,
            self.partner.business_area_partner_through.filter(business_area=self.afghanistan).first().roles.all(),
        )
        self.assertEqual(
            self.partner.business_area_partner_through.filter(business_area=self.ukraine).first().roles.count(), 2
        )
        self.assertIn(
            self.role_in_ukr_1,
            self.partner.business_area_partner_through.filter(business_area=self.ukraine).first().roles.all(),
        )
        self.assertIn(
            self.role_in_ukr_2,
            self.partner.business_area_partner_through.filter(business_area=self.ukraine).first().roles.all(),
        )
        self.assertEqual(
            self.partner.program_partner_through.filter(program=self.program_in_afg_1).first().areas.count(), 1
        )
        self.assertIn(
            self.area_in_afg_1,
            self.partner.program_partner_through.filter(program=self.program_in_afg_1).first().areas.all(),
        )
        self.assertEqual(
            self.partner.program_partner_through.filter(program=self.program_in_afg_2).first().full_area_access,
            True,
        )
        self.assertEqual(
            self.partner.program_partner_through.filter(program=self.program_in_afg_2).first().areas.count(),
            areas_count_in_afg,
        )
        self.assertIn(
            self.area_in_afg_1,
            self.partner.program_partner_through.filter(program=self.program_in_afg_2).first().areas.all(),
        )
        self.assertIn(
            self.area_in_afg_2,
            self.partner.program_partner_through.filter(program=self.program_in_afg_2).first().areas.all(),
        )
        self.assertIn(
            self.area_in_afg_3,
            self.partner.program_partner_through.filter(program=self.program_in_afg_2).first().areas.all(),
        )
        self.assertEqual(
            self.partner.program_partner_through.filter(program=self.program_in_ukr_1).first().full_area_access,
            True,
        )
        self.assertEqual(
            self.partner.program_partner_through.filter(program=self.program_in_ukr_1).first().areas.count(),
            areas_count_in_ukr,
        )
        self.assertIn(
            self.area_in_ukr_1,
            self.partner.program_partner_through.filter(program=self.program_in_ukr_1).first().areas.all(),
        )
        self.assertIn(
            self.area_in_ukr_2,
            self.partner.program_partner_through.filter(program=self.program_in_ukr_1).first().areas.all(),
        )
        self.assertEqual(
            self.partner.program_partner_through.filter(program=self.program_in_ukr_2).first().areas.count(), 2
        )
        self.assertIn(
            self.area_in_ukr_2,
            self.partner.program_partner_through.filter(program=self.program_in_ukr_2).first().areas.all(),
        )
        self.assertIn(
            self.area_in_ukr_2,
            self.partner.program_partner_through.filter(program=self.program_in_ukr_2).first().areas.all(),
        )
