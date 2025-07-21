from typing import Any, List
from unittest.mock import patch

from django.contrib.auth.models import AnonymousUser

from parameterized import parameterized

from tests.extras.test_utils.factories.account import PartnerFactory, RoleFactory, UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from tests.extras.test_utils.factories.core import (
    create_afghanistan,
    generate_data_collecting_types,
)
from hct_mis_api.apps.core.models import DataCollectingType
from tests.extras.test_utils.factories.payment import PaymentPlanFactory
from hct_mis_api.apps.program.fixtures import (
    BeneficiaryGroupFactory,
    ProgramCycleFactory,
    ProgramFactory,
)
from hct_mis_api.apps.program.models import Program, ProgramPartnerThrough
from hct_mis_api.apps.registration_data.fixtures import RegistrationDataImportFactory
from hct_mis_api.apps.registration_data.models import RegistrationDataImport


class TestAllProgramsQuery(APITestCase):
    ALL_PROGRAMS_QUERY = """
    query AllPrograms($businessArea: String!, $orderBy: String, $compatibleDct: Boolean, $beneficiaryGroupMatch: Boolean) {
        allPrograms(businessArea: $businessArea, orderBy: $orderBy, compatibleDct: $compatibleDct, beneficiaryGroupMatch: $beneficiaryGroupMatch) {
          totalCount
          edges {
            node {
              name
            }
          }
        }
      }
    """

    ALL_PROGRAMS_QUERY_WITH_PROGRAM_CYCLE_FILTERS = """
    query AllPrograms($businessArea: String!, $orderBy: String, $name: String, $compatibleDct: Boolean, $cycleOrderBy: String, $cycleSearch: String, $cycleTotalDeliveredQuantityUsdFrom: Float, $cycleTotalDeliveredQuantityUsdTo: Float) {
        allPrograms(businessArea: $businessArea, orderBy: $orderBy, name: $name, compatibleDct: $compatibleDct) {
          totalCount
          edges {
            node {
              name
              cycles(orderBy: $cycleOrderBy, search: $cycleSearch, totalDeliveredQuantityUsdFrom: $cycleTotalDeliveredQuantityUsdFrom, totalDeliveredQuantityUsdTo: $cycleTotalDeliveredQuantityUsdTo) {
                totalCount
                edges {
                  node {
                    status
                    title
                    totalDeliveredQuantityUsd
                  }
                }
              }
            }
          }
        }
      }
    """

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.business_area = create_afghanistan()
        generate_data_collecting_types()
        data_collecting_type = DataCollectingType.objects.get(code="full_collection")
        cls.data_collecting_type_compatible = DataCollectingType.objects.get(code="size_only")
        cls.data_collecting_type_compatible.compatible_types.add(cls.data_collecting_type_compatible)
        data_collecting_type.compatible_types.add(cls.data_collecting_type_compatible, data_collecting_type)

        cls.business_area.data_collecting_types.set(DataCollectingType.objects.all().values_list("id", flat=True))

        cls.partner = PartnerFactory(name="WFP")
        cls.partner.allowed_business_areas.add(cls.business_area)
        role = RoleFactory(name="Role for WFP")
        cls.add_partner_role_in_business_area(cls.partner, cls.business_area, [role])

        cls.user = UserFactory.create(partner=cls.partner)

        cls.unicef_partner = PartnerFactory(name="UNICEF")
        other_partner = PartnerFactory(name="Other Partner")
        other_partner.allowed_business_areas.add(cls.business_area)

        program_with_partner_access = ProgramFactory.create(
            name="Program with partner access",
            status=Program.DRAFT,
            business_area=cls.business_area,
            data_collecting_type=data_collecting_type,
            partner_access=Program.SELECTED_PARTNERS_ACCESS,
        )
        ProgramPartnerThrough.objects.create(
            program=program_with_partner_access,
            partner=cls.partner,
        )

        ProgramFactory.create(
            name="Program with all partners access",
            status=Program.ACTIVE,
            business_area=cls.business_area,
            data_collecting_type=data_collecting_type,
            partner_access=Program.ALL_PARTNERS_ACCESS,
            cycle__title="Default Cycle",
        )

        ProgramFactory.create(
            name="Program with none partner access",
            status=Program.ACTIVE,
            business_area=cls.business_area,
            data_collecting_type=data_collecting_type,
            partner_access=Program.NONE_PARTNERS_ACCESS,
        )

        program_without_partner_access = ProgramFactory.create(
            name="Program without partner access",
            status=Program.ACTIVE,
            business_area=cls.business_area,
            data_collecting_type=data_collecting_type,
            partner_access=Program.SELECTED_PARTNERS_ACCESS,
        )
        ProgramPartnerThrough.objects.create(
            program=program_without_partner_access,
            partner=other_partner,
        )

    @parameterized.expand(
        [
            ("with_permission", [Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS]),
            ("without_permission", []),
        ]
    )
    def test_all_programs_query(self, _: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)
        self.snapshot_graphql_request(
            request_string=self.ALL_PROGRAMS_QUERY,
            context={
                "user": self.user,
                "headers": {
                    "Business-Area": self.business_area.slug,
                },
            },
            variables={"businessArea": self.business_area.slug, "orderBy": "name"},
        )

    def test_all_programs_query_unicef_partner(self) -> None:
        user = UserFactory.create(partner=self.unicef_partner)
        # granting any role in the business area to the user; permission to view programs is inherited from the unicef partner
        self.create_user_role_with_permissions(user, [Permissions.RDI_MERGE_IMPORT], self.business_area)
        self.snapshot_graphql_request(
            request_string=self.ALL_PROGRAMS_QUERY,
            context={
                "user": user,
                "headers": {
                    "Business-Area": self.business_area.slug,
                },
            },
            variables={"businessArea": self.business_area.slug, "orderBy": "name"},
        )

    def test_all_programs_query_filter_dct(self) -> None:
        program = ProgramFactory.create(
            name="Program for dct filter",
            status=Program.ACTIVE,
            business_area=self.business_area,
            data_collecting_type=self.data_collecting_type_compatible,
            partner_access=Program.ALL_PARTNERS_ACCESS,
        )
        # program that does not have the current program in the compatible types
        ProgramFactory.create(
            name="Program not compatible",
            status=Program.ACTIVE,
            business_area=self.business_area,
            data_collecting_type=DataCollectingType.objects.get(code="partial_individuals"),
            partner_access=Program.ALL_PARTNERS_ACCESS,
        )

        user = UserFactory.create(partner=self.unicef_partner)
        self.create_user_role_with_permissions(user, [Permissions.RDI_MERGE_IMPORT], self.business_area)
        self.snapshot_graphql_request(
            request_string=self.ALL_PROGRAMS_QUERY,
            context={
                "user": user,
                "headers": {
                    "Business-Area": self.business_area.slug,
                    "Program": self.id_to_base64(program.id, "ProgramNode"),
                },
            },
            variables={"businessArea": self.business_area.slug, "orderBy": "name", "compatibleDct": True},
        )

    def test_all_programs_query_filter_beneficiary_group(self) -> None:
        beneficiary_group1 = BeneficiaryGroupFactory(name="Beneficiary Group 1")
        beneficiary_group2 = BeneficiaryGroupFactory(name="Beneficiary Group 2")
        program1 = ProgramFactory.create(
            name="Program Beneficiary Group 1",
            status=Program.ACTIVE,
            business_area=self.business_area,
            beneficiary_group=beneficiary_group1,
        )
        ProgramFactory.create(
            name="Other Program Beneficiary Group 1",
            status=Program.ACTIVE,
            business_area=self.business_area,
            beneficiary_group=beneficiary_group1,
        )
        ProgramFactory.create(
            name="Program Beneficiary Group 2",
            status=Program.ACTIVE,
            business_area=self.business_area,
            beneficiary_group=beneficiary_group2,
        )

        user = UserFactory.create(partner=self.unicef_partner)
        self.create_user_role_with_permissions(user, [Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS], self.business_area)
        self.snapshot_graphql_request(
            request_string=self.ALL_PROGRAMS_QUERY,
            context={
                "user": user,
                "headers": {
                    "Business-Area": self.business_area.slug,
                    "Program": self.id_to_base64(program1.id, "ProgramNode"),
                },
            },
            variables={"businessArea": self.business_area.slug, "orderBy": "name", "beneficiaryGroupMatch": True},
        )

        self.snapshot_graphql_request(
            request_string=self.ALL_PROGRAMS_QUERY,
            context={
                "user": user,
                "headers": {
                    "Business-Area": self.business_area.slug,
                    "Program": self.id_to_base64(program1.id, "ProgramNode"),
                },
            },
            variables={"businessArea": self.business_area.slug, "orderBy": "name", "beneficiaryGroupMatch": False},
        )

    @patch("django.contrib.auth.models.AnonymousUser.is_authenticated", new_callable=lambda: False)
    def test_all_programs_query_user_not_authenticated(self, mock_is_authenticated: Any) -> None:
        self.snapshot_graphql_request(
            request_string=self.ALL_PROGRAMS_QUERY,
            context={
                "user": AnonymousUser,
                "headers": {
                    "Business-Area": self.business_area.slug,
                },
            },
            variables={"businessArea": self.business_area.slug, "orderBy": "name"},
        )

    def test_all_programs_with_cycles_filter(self) -> None:
        self.create_user_role_with_permissions(
            self.user, [Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS], self.business_area
        )
        self.user.partner = self.unicef_partner
        self.user.save()
        self.snapshot_graphql_request(
            request_string=self.ALL_PROGRAMS_QUERY_WITH_PROGRAM_CYCLE_FILTERS,
            context={
                "user": self.user,
                "headers": {
                    "Business-Area": self.business_area.slug,
                },
            },
            variables={
                "businessArea": self.business_area.slug,
                "orderBy": "name",
                "name": "Program with all partners access",
                "cycleSearch": "Default",
            },
        )
        program = Program.objects.get(name="Program with all partners access")

        cycle = ProgramCycleFactory(program=program, title="Second CYCLE with total_delivered_quantity_usd")
        PaymentPlanFactory(program_cycle=cycle, total_delivered_quantity_usd=999)

        self.snapshot_graphql_request(
            request_string=self.ALL_PROGRAMS_QUERY_WITH_PROGRAM_CYCLE_FILTERS,
            context={
                "user": self.user,
                "headers": {
                    "Business-Area": self.business_area.slug,
                },
            },
            variables={
                "businessArea": self.business_area.slug,
                "orderBy": "name",
                "name": "Program with all partners access",
                "cycleTotalDeliveredQuantityUsdFrom": 100,
            },
        )
        self.snapshot_graphql_request(
            request_string=self.ALL_PROGRAMS_QUERY_WITH_PROGRAM_CYCLE_FILTERS,
            context={
                "user": self.user,
                "headers": {
                    "Business-Area": self.business_area.slug,
                },
            },
            variables={
                "businessArea": self.business_area.slug,
                "orderBy": "name",
                "name": "Program with all partners access",
                "cycleOrderBy": "title",
                "cycleTotalDeliveredQuantityUsdTo": 1000,
            },
        )
        self.snapshot_graphql_request(
            request_string=self.ALL_PROGRAMS_QUERY_WITH_PROGRAM_CYCLE_FILTERS,
            context={
                "user": self.user,
                "headers": {
                    "Business-Area": self.business_area.slug,
                },
            },
            variables={
                "businessArea": self.business_area.slug,
                "orderBy": "name",
                "name": "Program with all partners access",
                "cycleTotalDeliveredQuantityUsdFrom": 555,
                "cycleTotalDeliveredQuantityUsdTo": 1000,
            },
        )
        self.snapshot_graphql_request(
            request_string=self.ALL_PROGRAMS_QUERY_WITH_PROGRAM_CYCLE_FILTERS,
            context={
                "user": self.user,
                "headers": {
                    "Business-Area": self.business_area.slug,
                },
            },
            variables={
                "businessArea": self.business_area.slug,
                "orderBy": "name",
                "name": "Program with all partners access",
                "cycleOrderBy": "title",
                "cycleTotalDeliveredQuantityUsdTo": None,
            },
        )

    def test_program_can_run_deduplication_and_is_deduplication_disabled(self) -> None:
        program1 = ProgramFactory.create(
            name="Program for dct filter",
            status=Program.ACTIVE,
            business_area=self.business_area,
            biometric_deduplication_enabled=True,
        )
        self.snapshot_graphql_request(
            request_string="""
            query canRunDeduplicationAndIsDeduplicationDisabled {
              canRunDeduplication
              isDeduplicationDisabled
            }
            """,
            context={
                "user": self.user,
                "headers": {
                    "Business-Area": self.business_area.slug,
                    "Program": self.id_to_base64(program1.id, "ProgramNode"),
                },
            },
            variables={},
        )
        RegistrationDataImportFactory(
            deduplication_engine_status=RegistrationDataImport.DEDUP_ENGINE_PENDING,
            data_source=RegistrationDataImport.XLS,
            program=program1,
        )
        self.snapshot_graphql_request(
            request_string="""
                    query canRunDeduplicationAndIsDeduplicationDisabled {
                      canRunDeduplication
                      isDeduplicationDisabled
                    }
                    """,
            context={
                "user": self.user,
                "headers": {
                    "Business-Area": self.business_area.slug,
                    "Program": self.id_to_base64(program1.id, "ProgramNode"),
                },
            },
            variables={},
        )
        RegistrationDataImportFactory(
            deduplication_engine_status=RegistrationDataImport.DEDUP_ENGINE_IN_PROGRESS,
            data_source=RegistrationDataImport.XLS,
            program=program1,
        )
        self.snapshot_graphql_request(
            request_string="""
                    query canRunDeduplicationAndIsDeduplicationDisabled {
                      canRunDeduplication
                      isDeduplicationDisabled
                    }
                    """,
            context={
                "user": self.user,
                "headers": {
                    "Business-Area": self.business_area.slug,
                    "Program": self.id_to_base64(program1.id, "ProgramNode"),
                },
            },
            variables={},
        )

    def test_all_programs_query_without_ba_header(self) -> None:
        self.snapshot_graphql_request(
            request_string=self.ALL_PROGRAMS_QUERY,
            context={
                "user": self.user,
                "headers": {},
            },
            variables={"businessArea": self.business_area.slug},
        )
