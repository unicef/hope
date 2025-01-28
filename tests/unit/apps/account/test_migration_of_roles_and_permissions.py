from importlib import import_module

from django.apps import apps
from django.test import TestCase
from django.utils import timezone

from hct_mis_api.apps.account.fixtures import (
    BusinessAreaFactory,
    PartnerFactory,
    UserFactory,
)
from hct_mis_api.apps.account.models import (
    AdminAreaLimitedTo,
    Partner,
    Role,
    RoleAssignment,
)
from hct_mis_api.apps.core.models import BusinessAreaPartnerThrough
from hct_mis_api.apps.geo.fixtures import AreaFactory, AreaTypeFactory, CountryFactory
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import ProgramPartnerThrough

data_migration = import_module("hct_mis_api.apps.account.migrations.0006_migration")


# TODO: remove this file after removal of BusinessAreaPartnerThrough and ProgramPartnerThrough - see the comment below
class MigrateUserRolesTest(TestCase):
    """
    These tests are for the migration of user roles from the old structure to the new one.
    (UserRole -> RoleAssignment, removal of BusinessAreaPartnerThrough, ProgramPartnerThrough, introduction of AdminAreaLimitedTo, changes for UNICEF Partner to be a parent of UNICEF HQ and UNICEF subpartners per BA, etc.)
    This file is to be removed after actual removal of BusinessAreaPartnerThrough and ProgramPartnerThrough, after the migrations and confirmation that data is correct.
    """

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()

        cls.business_area_afg = BusinessAreaFactory(name="Afghanistan", slug="afghanistan", code="AFG", active=True)
        cls.business_area_ukr = BusinessAreaFactory(name="Ukraine", slug="ukraine", code="UKR", active=True)

        # remove partners that were created in signal for creating BAs - to keep the data as it was before changes
        Partner.objects.filter(parent__name="UNICEF").delete()

        cls.program_1_afg = ProgramFactory(name="Program 1 AFG", business_area=cls.business_area_afg)
        cls.program_2_afg = ProgramFactory(name="Program 2 AFG", business_area=cls.business_area_afg)
        cls.program_1_ukr = ProgramFactory(name="Program 1 UKR", business_area=cls.business_area_ukr)
        cls.program_2_ukr = ProgramFactory(name="Program 2 UKR", business_area=cls.business_area_ukr)

        cls.country_afg = CountryFactory(name="Afghanistan", iso_code3="AFG", iso_code2="AF", iso_num="040")
        cls.country_afg.business_areas.set([cls.business_area_afg])
        cls.area_type_afg = AreaTypeFactory(name="Area Type in Afg", country=cls.country_afg, area_level=1)
        cls.area_1_afg = AreaFactory(name="Area 1 Afg", area_type=cls.area_type_afg, p_code="AREA1-AFG")
        cls.area_2_afg = AreaFactory(name="Area 2 Afg", area_type=cls.area_type_afg, p_code="AREA2-AFG")

        cls.country_ukr = CountryFactory(name="Ukraine", iso_code3="UKR", iso_code2="UK", iso_num="050")
        cls.country_ukr.business_areas.set([cls.business_area_ukr])
        cls.area_type_ukr = AreaTypeFactory(name="Area Type in Ukr", country=cls.country_ukr, area_level=1)
        cls.area_1_ukr = AreaFactory(name="Area 1 Ukr", area_type=cls.area_type_ukr, p_code="AREA1-UKR")

        # users currently under UNICEF Partner
        cls.partner_unicef = PartnerFactory(name="UNICEF")

        cls.user_unicef_in_afg = UserFactory(partner=cls.partner_unicef)
        cls.user_unicef_in_ukr = UserFactory(partner=cls.partner_unicef)
        cls.unicef_user_hq = UserFactory(partner=cls.partner_unicef)
        cls.unicef_user_without_any_role = UserFactory(partner=cls.partner_unicef)

        # users under custom partners
        cls.partner_1 = PartnerFactory(name="Partner 1")
        cls.user_1_partner_1 = UserFactory(partner=cls.partner_1)
        cls.user_2_partner_1 = UserFactory(partner=cls.partner_1)

        cls.partner_2 = PartnerFactory(name="Partner 2")
        cls.user_1_partner_2 = UserFactory(partner=cls.partner_2)
        cls.user_2_partner_2 = UserFactory(partner=cls.partner_2)

        cls.partner_3 = PartnerFactory(name="Partner 3")
        cls.user_3 = UserFactory(partner=cls.partner_3)

        cls.user_no_partner = UserFactory(partner=None)

        cls.partner_empty = PartnerFactory(name="Default Empty Partner")
        cls.user_default_empty_partner = UserFactory(partner=cls.partner_empty)

        # roles and access
        cls.role_1 = Role.objects.create(name="Role 1")
        cls.role_2 = Role.objects.create(name="Role 2")

        # user_unicef_in_afg - role in Afghanistan, partner UNICEF
        RoleAssignment.objects.create(
            business_area=cls.business_area_afg,
            user=cls.user_unicef_in_afg,
            role=cls.role_1,
        )
        # user_unicef_in_ukr - role in Ukraine, partner UNICEF
        RoleAssignment.objects.create(
            business_area=cls.business_area_ukr,
            user=cls.user_unicef_in_ukr,
            role=cls.role_2,
        )
        # unicef_user_hq - role in Afghanistan and Ukraine, partner UNICEF
        RoleAssignment.objects.create(
            business_area=cls.business_area_afg,
            user=cls.unicef_user_hq,
            role=cls.role_1,
        )
        RoleAssignment.objects.create(
            business_area=cls.business_area_ukr,
            user=cls.unicef_user_hq,
            role=cls.role_2,
        )
        # unicef_user_without_any_role - no role, partner UNICEF

        # UNICEF has access to all programs
        ProgramPartnerThrough.objects.create(
            program=cls.program_1_afg,
            partner=cls.partner_unicef,
            full_area_access=True,
        )
        ProgramPartnerThrough.objects.create(
            program=cls.program_2_afg,
            partner=cls.partner_unicef,
            full_area_access=True,
        )
        ProgramPartnerThrough.objects.create(
            program=cls.program_1_ukr,
            partner=cls.partner_unicef,
            full_area_access=True,
        )
        ProgramPartnerThrough.objects.create(
            program=cls.program_2_ukr,
            partner=cls.partner_unicef,
            full_area_access=True,
        )

        # Partner 1 has access to Program 1 AFG, no roles
        partner_1_program_1_afg = ProgramPartnerThrough.objects.create(
            program=cls.program_1_afg,
            partner=cls.partner_1,
        )
        partner_1_program_1_afg.areas.set([cls.area_1_afg])
        # user_1_partner_1 - role in Afghanistan, Ukraine
        RoleAssignment.objects.create(
            business_area=cls.business_area_afg,
            user=cls.user_1_partner_1,
            role=cls.role_1,
        )
        RoleAssignment.objects.create(
            business_area=cls.business_area_ukr,
            user=cls.user_1_partner_1,
            role=cls.role_2,
        )
        # user_2_partner_1 - role in Ukraine
        RoleAssignment.objects.create(
            business_area=cls.business_area_ukr,
            user=cls.user_2_partner_1,
            role=cls.role_2,
        )

        # Partner 2 has access to Program 1 and 2 AFG and Program 1 UKR and has 2 roles in Ukraine
        partner_2_program_1_afg = ProgramPartnerThrough.objects.create(
            program=cls.program_1_afg,
            partner=cls.partner_2,
        )
        partner_2_program_1_afg.areas.set([cls.area_1_afg])
        ProgramPartnerThrough.objects.create(
            program=cls.program_2_afg,
            partner=cls.partner_2,
            full_area_access=True,
        )
        partner_2_program_1_ukr = ProgramPartnerThrough.objects.create(
            program=cls.program_1_ukr,
            partner=cls.partner_2,
        )
        partner_2_program_1_ukr.areas.set([cls.area_1_ukr])
        partner_2_ukr = BusinessAreaPartnerThrough.objects.create(
            business_area=cls.business_area_ukr,
            partner=cls.partner_2,
        )
        partner_2_ukr.roles.set([cls.role_1, cls.role_2])

        # user_1_partner_2 - role in Afghanistan
        RoleAssignment.objects.create(
            business_area=cls.business_area_afg,
            user=cls.user_1_partner_2,
            role=cls.role_1,
        )

        # user_2_partner_2 - role in Ukraine
        RoleAssignment.objects.create(
            business_area=cls.business_area_ukr,
            user=cls.user_2_partner_2,
            role=cls.role_2,
        )

        # Partner 3 has access to Program 1 AFG, role_2 in Ukraine
        partner_3_program_1_afg = ProgramPartnerThrough.objects.create(
            program=cls.program_1_afg,
            partner=cls.partner_3,
        )
        partner_3_program_1_afg.areas.set([cls.area_1_afg, cls.area_2_afg])
        partner_3_ukr = BusinessAreaPartnerThrough.objects.create(
            business_area=cls.business_area_ukr,
            partner=cls.partner_3,
        )
        partner_3_ukr.roles.set([cls.role_2])

        # user_3 - role in Afghanistan
        RoleAssignment.objects.create(
            business_area=cls.business_area_afg,
            user=cls.user_3,
            role=cls.role_1,
        )

        # user_no_partner - role in Afghanistan, no partner
        RoleAssignment.objects.create(
            business_area=cls.business_area_afg,
            user=cls.user_no_partner,
            role=cls.role_1,
        )

        # user_default_empty_partner - role in Afghanistan, partner Default Empty Partner
        RoleAssignment.objects.create(
            business_area=cls.business_area_afg,
            user=cls.user_default_empty_partner,
            role=cls.role_1,
        )

    def test_user_roles_migration(self) -> None:
        # call all 3 functions to check the final result
        data_migration.migrate_user_roles(apps, None)
        data_migration.migrate_partner_roles_and_access(apps, None)
        data_migration.migrate_unicef_partners(apps, None)

        now = timezone.now()

        # user_unicef_in_afg - has role_1 in Afg, UNICEF has access to all programs -> should have role_1 in Afg for each program
        self.assertEqual(self.user_unicef_in_afg.role_assignments.count(), 2)
        self.assertIsNotNone(
            RoleAssignment.objects.filter(
                user=self.user_unicef_in_afg,
                business_area=self.business_area_afg,
                role=self.role_1,
                program=self.program_1_afg,
                expiry_date=None,
            ).first()
        )
        self.assertIsNotNone(
            RoleAssignment.objects.filter(
                user=self.user_unicef_in_afg,
                business_area=self.business_area_afg,
                role=self.role_1,
                program=self.program_2_afg,
                expiry_date=None,
            ).first()
        )

        # user_unicef_in_ukr - has role_2 in Ukr, UNICEF has access to all programs -> should have role_2 in Ukr for each program
        self.assertEqual(self.user_unicef_in_ukr.role_assignments.count(), 2)
        self.assertIsNotNone(
            RoleAssignment.objects.filter(
                user=self.user_unicef_in_ukr,
                business_area=self.business_area_ukr,
                role=self.role_2,
                program=self.program_1_ukr,
                expiry_date=None,
            ).first()
        )
        self.assertIsNotNone(
            RoleAssignment.objects.filter(
                user=self.user_unicef_in_ukr,
                business_area=self.business_area_ukr,
                role=self.role_2,
                program=self.program_2_ukr,
                expiry_date=None,
            ).first()
        )

        # unicef_user_hq - has role_1 in Afg and role_2 Ukr, UNICEF has access to all programs -> should have role_1 in Afg and role_2 Ukr for each program
        self.assertEqual(self.unicef_user_hq.role_assignments.count(), 4)
        self.assertIsNotNone(
            RoleAssignment.objects.filter(
                user=self.unicef_user_hq,
                business_area=self.business_area_afg,
                role=self.role_1,
                program=self.program_1_afg,
            ).first()
        )
        self.assertIsNotNone(
            RoleAssignment.objects.filter(
                user=self.unicef_user_hq,
                business_area=self.business_area_afg,
                role=self.role_1,
                program=self.program_2_afg,
            ).first()
        )
        self.assertIsNotNone(
            RoleAssignment.objects.filter(
                user=self.unicef_user_hq,
                business_area=self.business_area_ukr,
                role=self.role_2,
                program=self.program_1_ukr,
                expiry_date=None,
            ).first()
        )
        self.assertIsNotNone(
            RoleAssignment.objects.filter(
                user=self.unicef_user_hq,
                business_area=self.business_area_ukr,
                role=self.role_2,
                program=self.program_2_ukr,
                expiry_date=None,
            ).first()
        )

        # unicef_user_without_any_role - no role, UNICEF has access to all programs -> should have no roles
        self.assertEqual(self.unicef_user_without_any_role.role_assignments.count(), 0)

        # user_1_partner_1 - has role_1 in Afg and role_2 in Ukr, his partner has access to Program 1 AFG -> should have role_1 in Program 1 AFG, role_2 in Ukr is marked as expired
        self.assertEqual(self.user_1_partner_1.role_assignments.count(), 2)
        self.assertIsNotNone(
            RoleAssignment.objects.filter(
                user=self.user_1_partner_1,
                business_area=self.business_area_afg,
                role=self.role_1,
                program=self.program_1_afg,
                expiry_date=None,
            ).first()
        )
        self.assertIsNotNone(
            RoleAssignment.objects.filter(
                user=self.user_1_partner_1,
                business_area=self.business_area_ukr,
                role=self.role_2,
                program=None,
                expiry_date__lte=now,
            ).first()
        )

        # user_2_partner_1 - has role_2 in Ukr, his partner has access to Program 1 AFG -> his role in Ukr is marked as expired
        self.assertEqual(self.user_2_partner_1.role_assignments.count(), 1)
        self.assertIsNotNone(
            RoleAssignment.objects.filter(
                user=self.user_2_partner_1,
                business_area=self.business_area_ukr,
                role=self.role_2,
                program=None,
                expiry_date__lte=now,
            ).first()
        )

        # user_1_partner_2 - has role_1 in Afg, his partner has access to Program 1 and 2 AFG and Program 1 UKR -> should have role_1 in Afg for each program
        self.assertEqual(self.user_1_partner_2.role_assignments.count(), 2)
        self.assertIsNotNone(
            RoleAssignment.objects.filter(
                user=self.user_1_partner_2,
                business_area=self.business_area_afg,
                role=self.role_1,
                program=self.program_1_afg,
                expiry_date=None,
            ).first()
        )
        self.assertIsNotNone(
            RoleAssignment.objects.filter(
                user=self.user_1_partner_2,
                business_area=self.business_area_afg,
                role=self.role_1,
                program=self.program_2_afg,
                expiry_date=None,
            ).first()
        )

        # user_2_partner_2 - has role_2 in Ukr, his partner has access to Program 1 and 2 AFG and Program 1 UKR -> should have role_2 in Ukr for Program 1
        self.assertEqual(self.user_2_partner_2.role_assignments.count(), 1)
        self.assertIsNotNone(
            RoleAssignment.objects.filter(
                user=self.user_2_partner_2,
                business_area=self.business_area_ukr,
                role=self.role_2,
                program=self.program_1_ukr,
                expiry_date=None,
            ).first()
        )

        # user_3 - has role_1 in Afg, his partner has access to Program 1 in AFG -> role marked as expired
        self.assertEqual(self.user_3.role_assignments.count(), 1)
        self.assertIsNotNone(
            RoleAssignment.objects.filter(
                user=self.user_3,
                business_area=self.business_area_afg,
                role=self.role_1,
                program=self.program_1_afg,
                expiry_date=None,
            ).first()
        )

        # user_no_partner - has role_1 in Afg, no partner -> role marked as expired
        self.assertEqual(self.user_no_partner.role_assignments.count(), 1)
        self.assertIsNotNone(
            RoleAssignment.objects.filter(
                user=self.user_no_partner,
                business_area=self.business_area_afg,
                role=self.role_1,
                program=None,
                expiry_date__lte=now,
            ).first()
        )

        # user_default_empty_partner - has role_1 in Afg, partner Default Empty Partner -> role marked as expired
        self.assertEqual(self.user_default_empty_partner.role_assignments.count(), 1)

    def test_partner_roles_migration(self) -> None:
        # additional partner that has role and access but is a parent -> no RoleAssignment should be created
        partner_parent = PartnerFactory(name="Parent Partner")
        PartnerFactory(name="Child Partner", parent=partner_parent)
        partner_parent_afg = BusinessAreaPartnerThrough.objects.create(
            business_area=self.business_area_afg,
            partner=partner_parent,
        )
        partner_parent_afg.roles.set([self.role_1, self.role_2])
        ProgramPartnerThrough.objects.create(
            program=self.program_1_afg,
            partner=partner_parent,
            full_area_access=True,
        )

        # call all 3 functions to check the final result
        data_migration.migrate_user_roles(apps, None)
        data_migration.migrate_partner_roles_and_access(apps, None)
        data_migration.migrate_unicef_partners(apps, None)

        # partner_unicef - UNICEF partner has no roles, has access to all programs -> no RoleAssignment should be created
        self.assertEqual(self.partner_unicef.role_assignments.count(), 0)

        # partner_1 - has no roles, access to Program 1 AFG -> no RoleAssignment should be created
        self.assertEqual(self.partner_1.role_assignments.count(), 0)

        # partner_2 - has role_1 and role_2 in Ukr, access to Program 1 and 2 AFG and Program 1 UKR -> should have role_1 and role_2 in Ukr for Program 1
        self.assertEqual(self.partner_2.role_assignments.count(), 2)
        self.assertIsNotNone(
            RoleAssignment.objects.filter(
                partner=self.partner_2,
                business_area=self.business_area_ukr,
                role=self.role_1,
                program=self.program_1_ukr,
                expiry_date=None,
            ).first()
        )
        self.assertIsNotNone(
            RoleAssignment.objects.filter(
                partner=self.partner_2,
                business_area=self.business_area_ukr,
                role=self.role_2,
                program=self.program_1_ukr,
                expiry_date=None,
            ).first()
        )

        # partner_3 - has role_2 in Ukraine, access to Program 1 AFG -> no RoleAssignment should be created
        self.assertEqual(self.partner_3.role_assignments.count(), 0)

        # partner_empty - has no roles, no access -> no RoleAssignment should be created
        self.assertEqual(self.partner_empty.role_assignments.count(), 0)

    def test_unicef_partners_migration(self) -> None:
        self.assertEqual(self.partner_unicef.user_set.count(), 4)

        # call all 3 functions to check the final result
        data_migration.migrate_user_roles(apps, None)
        data_migration.migrate_partner_roles_and_access(apps, None)
        data_migration.migrate_unicef_partners(apps, None)

        self.user_unicef_in_afg.refresh_from_db()
        self.user_unicef_in_ukr.refresh_from_db()
        self.unicef_user_hq.refresh_from_db()
        self.unicef_user_without_any_role.refresh_from_db()

        # check UNICEF subpartners creation
        self.assertEqual(Partner.objects.filter(parent=self.partner_unicef).count(), 3)
        self.assertEqual(self.partner_unicef.user_set.count(), 0)

        unicef_in_afg = Partner.objects.filter(name="UNICEF Partner for afghanistan").first()
        unicef_in_ukr = Partner.objects.filter(name="UNICEF Partner for ukraine").first()
        unicef_hq = Partner.objects.filter(name="UNICEF HQ").first()

        self.assertIsNotNone(unicef_in_afg)
        self.assertIsNotNone(unicef_in_ukr)
        self.assertIsNotNone(unicef_hq)

        self.assertEqual(
            unicef_in_afg.parent,
            self.partner_unicef,
        )
        self.assertEqual(
            unicef_in_ukr.parent,
            self.partner_unicef,
        )
        self.assertEqual(
            unicef_hq.parent,
            self.partner_unicef,
        )

        # check users reassignment to UNICEF subpartners

        # user_unicef_in_afg - has role only in Afg -> should be under UNICEF Partner for Afg
        self.assertEqual(
            self.user_unicef_in_afg.partner,
            unicef_in_afg,
        )

        # user_unicef_in_ukr - has role only in Ukr -> should be under UNICEF Partner for Ukr
        self.assertEqual(
            self.user_unicef_in_ukr.partner,
            unicef_in_ukr,
        )

        # unicef_user_hq - has roles in Afg and Ukr -> should be under UNICEF HQ
        self.assertEqual(
            self.unicef_user_hq.partner,
            unicef_hq,
        )

        # unicef_user_without_any_role - no role -> should be under Default Empty Partner
        self.assertEqual(
            self.unicef_user_without_any_role.partner,
            self.partner_empty,
        )

        # UNICEF subpartners per BA should be allowed in specific BA; UNICEF HQ should be allowed in all
        self.assertEqual(
            unicef_in_afg.allowed_business_areas.count(),
            1,
        )
        self.assertEqual(
            unicef_in_afg.allowed_business_areas.first(),
            self.business_area_afg,
        )

        self.assertEqual(
            unicef_in_ukr.allowed_business_areas.count(),
            1,
        )
        self.assertEqual(
            unicef_in_ukr.allowed_business_areas.first(),
            self.business_area_ukr,
        )

        self.assertEqual(
            unicef_hq.allowed_business_areas.count(),
            2,
        )
        self.assertTrue(self.business_area_afg in unicef_hq.allowed_business_areas.all())
        self.assertTrue(self.business_area_ukr in unicef_hq.allowed_business_areas.all())

        # check roles for UNICEF subpartners
        # newly created "Role for UNICEF Partners" should be assigned for UNICEF subpartners per BA
        # and "Role with all permissions" for UNICEF HQ
        role_with_all_permissions = Role.objects.get(name="Role with all permissions")
        role_for_unicef_partners = Role.objects.filter(name="Role for UNICEF Partners").first()
        self.assertIsNotNone(role_for_unicef_partners)

        self.assertEqual(
            unicef_in_afg.role_assignments.count(),
            1,
        )
        self.assertEqual(
            unicef_in_afg.role_assignments.first().role,
            role_for_unicef_partners,
        )

        self.assertEqual(
            unicef_in_ukr.role_assignments.count(),
            1,
        )
        self.assertEqual(
            unicef_in_ukr.role_assignments.first().role,
            role_for_unicef_partners,
        )

        self.assertEqual(
            unicef_hq.role_assignments.count(),
            2,
        )
        self.assertEqual(
            unicef_hq.role_assignments.all()[0].role,
            role_with_all_permissions,
        )
        self.assertEqual(
            unicef_hq.role_assignments.all()[1].role,
            role_with_all_permissions,
        )

        # check if there are no admin area restrictions
        self.assertEqual(
            unicef_in_afg.admin_area_limits.count(),
            0,
        )
        self.assertEqual(
            unicef_in_ukr.admin_area_limits.count(),
            0,
        )
        self.assertEqual(
            unicef_hq.admin_area_limits.count(),
            0,
        )

    def test_admin_area_limits(self) -> None:
        # call all 3 functions to check the final result
        data_migration.migrate_user_roles(apps, None)
        data_migration.migrate_partner_roles_and_access(apps, None)
        data_migration.migrate_unicef_partners(apps, None)

        self.assertEqual(AdminAreaLimitedTo.objects.count(), 4)

        # partner_unicef - UNICEF partner had full_area_access in programs -> no area limits
        self.assertEqual(
            self.partner_unicef.admin_area_limits.count(),
            0,
        )

        # partner_1 - has access to only area_1_afg in Program 1 AFG -> should have area limit in Program 1 AFG
        self.assertEqual(
            self.partner_1.admin_area_limits.count(),
            1,
        )
        self.assertEqual(
            self.partner_1.admin_area_limits.first().areas.count(),
            1,
        )
        self.assertEqual(
            self.partner_1.admin_area_limits.first().areas.first(),
            self.area_1_afg,
        )

        # partner_2 - has access to area_1_afg in Program 1 AFG and full_area_access in Program 2 AFG -> should have area limit in Program 1 AFG, no area limits in Program 2 AFG;
        # also has access to area_1_ukr in Program 1 UKR -> should have area limit in Program 1 UK
        self.assertEqual(
            self.partner_2.admin_area_limits.count(),
            2,
        )
        self.assertEqual(
            self.partner_2.admin_area_limits.filter(program=self.program_1_afg).first().areas.count(),
            1,
        )
        self.assertEqual(
            self.partner_2.admin_area_limits.filter(program=self.program_1_afg).first().areas.first(),
            self.area_1_afg,
        )
        self.assertEqual(
            self.partner_2.admin_area_limits.filter(program=self.program_2_afg).count(),
            0,
        )
        self.assertEqual(
            self.partner_2.admin_area_limits.filter(program=self.program_1_ukr).first().areas.count(),
            1,
        )
        self.assertEqual(
            self.partner_2.admin_area_limits.filter(program=self.program_1_ukr).first().areas.first(),
            self.area_1_ukr,
        )

        # partner_3 - has access to area_1_afg and area_2_afg in Program 1 AFG -> should have area limit in Program 1 AFG
        self.assertEqual(
            self.partner_3.admin_area_limits.count(),
            1,
        )
        self.assertEqual(
            self.partner_3.admin_area_limits.first().areas.count(),
            2,
        )
        self.assertTrue(self.area_1_afg in self.partner_3.admin_area_limits.first().areas.all())
        self.assertTrue(self.area_2_afg in self.partner_3.admin_area_limits.first().areas.all())

        # partner_empty - has no access -> no area limits
        self.assertEqual(
            self.partner_empty.admin_area_limits.count(),
            0,
        )
