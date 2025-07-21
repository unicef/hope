from typing import Any, List

from parameterized import parameterized

from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.models import PeriodicFieldData
from hct_mis_api.apps.program.models import Program
from tests.extras.test_utils.factories.account import PartnerFactory, UserFactory
from tests.extras.test_utils.factories.core import (
    FlexibleAttributeForPDUFactory,
    PeriodicFieldDataFactory,
    create_afghanistan,
)
from tests.extras.test_utils.factories.payment import PaymentPlanFactory
from tests.extras.test_utils.factories.program import ProgramFactory

PROGRAM_QUERY = """
    query Program($id: ID!) {
      program(id: $id) {
        name
        status
        canFinish
        targetPopulationsCount
        pduFields {
          label
          name
          pduData {
            subtype
            numberOfRounds
            roundsNames
          }
        }
      }
    }
    """


class TestProgramQuery(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.partner = PartnerFactory(name="WFP")
        cls.user = UserFactory.create(partner=cls.partner)

        cls.business_area = create_afghanistan()
        cls.program = ProgramFactory(business_area=cls.business_area, name="Test Program Query", status=Program.ACTIVE)
        pdu_data1 = PeriodicFieldDataFactory(
            subtype=PeriodicFieldData.DECIMAL,
            number_of_rounds=3,
            rounds_names=["Round 1", "Round 2", "Round 3"],
        )
        FlexibleAttributeForPDUFactory(
            program=cls.program,
            label="PDU Field 1",
            pdu_data=pdu_data1,
        )
        pdu_data2 = PeriodicFieldDataFactory(
            subtype=PeriodicFieldData.STRING,
            number_of_rounds=2,
            rounds_names=["Round January", "Round February"],
        )
        FlexibleAttributeForPDUFactory(
            program=cls.program,
            label="PDU Field 2",
            pdu_data=pdu_data2,
        )
        pdu_data3 = PeriodicFieldDataFactory(
            subtype=PeriodicFieldData.DATE,
            number_of_rounds=1,
            rounds_names=["Round *"],
        )
        FlexibleAttributeForPDUFactory(
            program=cls.program,
            label="PDU Field 3",
            pdu_data=pdu_data3,
        )
        pdu_data4 = PeriodicFieldDataFactory(
            subtype=PeriodicFieldData.BOOL,
            number_of_rounds=2,
            rounds_names=["Round A", "Round B"],
        )
        FlexibleAttributeForPDUFactory(
            program=cls.program,
            label="PDU Field 4",
            pdu_data=pdu_data4,
        )

        program_other = ProgramFactory(
            business_area=cls.business_area, name="Test Program Query Other", status=Program.ACTIVE
        )
        pdu_data_other = PeriodicFieldDataFactory(
            subtype=PeriodicFieldData.STRING,
            number_of_rounds=2,
            rounds_names=["Round January", "Round February"],
        )
        FlexibleAttributeForPDUFactory(
            program=program_other,
            label="PDU Field Other",
            pdu_data=pdu_data_other,
        )
        PaymentPlanFactory(program_cycle=cls.program.cycles.first())

    @parameterized.expand(
        [
            ("with_permission", [Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS]),
            ("without_permission", []),
        ]
    )
    def test_single_program_query(self, _: Any, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)
        self.snapshot_graphql_request(
            request_string=PROGRAM_QUERY,
            context={
                "user": self.user,
                "headers": {
                    "Business-Area": self.business_area.slug,
                },
            },
            variables={"id": self.id_to_base64(self.program.id, "ProgramNode")},
        )
