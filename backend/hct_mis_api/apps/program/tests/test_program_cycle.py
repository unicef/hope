from decimal import Decimal
from typing import Any, List, Optional

from django.core.exceptions import ValidationError
from django.test import TestCase

from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.payment.fixtures import PaymentPlanFactory
from hct_mis_api.apps.program.fixtures import ProgramCycleFactory, ProgramFactory
from hct_mis_api.apps.program.models import Program, ProgramCycle

CREATE_PROGRAM_CYCLE_MUTATION = """
mutation createProgramCycle($programCycleData: CreateProgramCycleInput!){
  createProgramCycle(programCycleData: $programCycleData){
    program{
      cycles{
        totalCount
        edges{
          node{
            status
            title
            startDate
            endDate
            totalDeliveredQuantityUsd
            totalEntitledQuantityUsd
            totalUndeliveredQuantityUsd
          }
        }
      }
    }
  }
}
"""


UPDATE_PROGRAM_CYCLE_MUTATION = """
mutation updateProgramCycle($programCycleData: UpdateProgramCycleInput!){
  updateProgramCycle(programCycleData: $programCycleData){
    program{
      cycles{
        totalCount
        edges{
          node{
            status
            title
            startDate
            endDate
            totalDeliveredQuantityUsd
            totalEntitledQuantityUsd
            totalUndeliveredQuantityUsd
          }
        }
      }
    }
  }
}
"""

DELETE_PROGRAM_CYCLE_MUTATION = """
mutation DeleteProgramCycle($programCycleId: ID!){
  deleteProgramCycle(programCycleId: $programCycleId){
    program{
      cycles{
        totalCount
        edges{
          node{
            status
            title
            startDate
            endDate
          }
        }
      }
    }
  }
}
"""


class TestProgramCycle(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        create_afghanistan()
        cls.user = UserFactory.create()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")
        cls.program = ProgramFactory(
            status=Program.DRAFT,
            business_area=cls.business_area,
            start_date="2020-01-01",
            end_date="2099-12-31",
            cycle__title="Default Cycle 001",
            cycle__start_date="2020-01-01",
            cycle__end_date="2020-01-02",
        )
        cls.program_cycle = ProgramCycleFactory(
            program=cls.program,
            start_date="2021-01-01",
            end_date="2022-01-01",
            title="Cycle 002",
        )
        cls.context = {
            "user": cls.user,
            "headers": {"program": cls.id_to_base64(cls.program.id, "ProgramNode"), "business-area": "afghanistan"},
        }

    @parameterized.expand(
        [
            ("without_permission_program_in_draft", [], Program.DRAFT, {}),
            ("with_permission_program_in_draft", [Permissions.PM_PROGRAMME_CYCLE_CREATE], Program.DRAFT, {}),
            (
                "with_permission_program_in_active_wrong_start_date",
                [Permissions.PM_PROGRAMME_CYCLE_CREATE],
                Program.ACTIVE,
                {"start_date": "1999-01-01"},
            ),
            (
                "with_permission_program_in_active_wrong_end_date",
                [Permissions.PM_PROGRAMME_CYCLE_CREATE],
                Program.ACTIVE,
                {"end_date": "2999-01-01"},
            ),
            (
                "with_permission_program_in_active_end_date_is_more_then_start_date",
                [Permissions.PM_PROGRAMME_CYCLE_CREATE],
                Program.ACTIVE,
                {"start_date": "2098-02-22", "end_date": "2098-02-11"},
            ),
        ]
    )
    def test_create_program_cycle(
        self, _: Any, permissions: List[Permissions], status: str, kwargs: Optional[Any]
    ) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)
        self.program.status = status
        self.program.save()

        inputs = {
            "title": "Test Name Program Cycle New",
            "startDate": kwargs.get("start_date", "2022-11-11"),
            "endDate": kwargs.get("end_date"),
        }

        self.snapshot_graphql_request(
            request_string=CREATE_PROGRAM_CYCLE_MUTATION,
            context=self.context,
            variables={"programCycleData": inputs},
        )

    def test_create_program_cycle_when_cycles_without_end_date(self) -> None:
        self.create_user_role_with_permissions(self.user, [Permissions.PM_PROGRAMME_CYCLE_CREATE], self.business_area)
        self.program.status = Program.ACTIVE
        self.program.save()

        inputs = {
            "title": "Test Name Program Cycle New 002",
            "startDate": "2022-11-11",
        }

        self.graphql_request(
            request_string=CREATE_PROGRAM_CYCLE_MUTATION,
            context=self.context,
            variables={"programCycleData": inputs},
        )
        self.snapshot_graphql_request(
            request_string=CREATE_PROGRAM_CYCLE_MUTATION,
            context=self.context,
            variables={
                "programCycleData": {"title": "Cycle New Name", "startDate": "2022-11-25", "endDate": "2022-12-12"}
            },
        )

    def test_create_program_cycle_when_cycles_overlapping(self) -> None:
        self.create_user_role_with_permissions(self.user, [Permissions.PM_PROGRAMME_CYCLE_CREATE], self.business_area)
        self.program.status = Program.ACTIVE
        self.program.save()

        inputs = {"title": "Test Name Program Cycle New 002", "startDate": "2055-11-11", "endDate": "2055-11-30"}

        # cycle "2055/11/11"->"2055/11/30"
        self.graphql_request(
            request_string=CREATE_PROGRAM_CYCLE_MUTATION,
            context=self.context,
            variables={"programCycleData": inputs},
        )
        # overlapping start_date
        self.snapshot_graphql_request(
            request_string=CREATE_PROGRAM_CYCLE_MUTATION,
            context=self.context,
            variables={"programCycleData": {"title": "Cycle New 333", "startDate": "2055-11-25"}},
        )
        # overlapping start_date
        self.snapshot_graphql_request(
            request_string=CREATE_PROGRAM_CYCLE_MUTATION,
            context=self.context,
            variables={
                "programCycleData": {"title": "Cycle New 444", "startDate": "2055-11-25", "endDate": "2055-12-12"}
            },
        )
        # overlapping end_date
        self.snapshot_graphql_request(
            request_string=CREATE_PROGRAM_CYCLE_MUTATION,
            context=self.context,
            variables={
                "programCycleData": {"title": "Cycle New 555", "startDate": "2055-11-01", "endDate": "2055-11-11"}
            },
        )
        # overlapping both
        self.snapshot_graphql_request(
            request_string=CREATE_PROGRAM_CYCLE_MUTATION,
            context=self.context,
            variables={
                "programCycleData": {"title": "Cycle New 555", "startDate": "2055-11-12", "endDate": "2055-11-29"}
            },
        )

    def test_create_program_cycle_with_the_same_name(self) -> None:
        self.create_user_role_with_permissions(self.user, [Permissions.PM_PROGRAMME_CYCLE_CREATE], self.business_area)
        self.program.status = Program.ACTIVE
        self.program.save()

        inputs = {
            "title": "TheSameName",
            "startDate": "2055-11-11",
            "endDate": "2055-12-12",
        }

        self.graphql_request(
            request_string=CREATE_PROGRAM_CYCLE_MUTATION,
            context=self.context,
            variables={"programCycleData": inputs},
        )
        self.snapshot_graphql_request(
            request_string=CREATE_PROGRAM_CYCLE_MUTATION,
            context=self.context,
            variables={"programCycleData": {"title": "TheSameName", "startDate": "2056-01-01"}},
        )

    def test_update_program_cycle(self) -> None:
        self.program.status = Program.ACTIVE
        self.program.save()

        inputs = {"title": "New Cycle for Update", "startDate": "2055-11-11"}
        self.create_user_role_with_permissions(self.user, [Permissions.PM_PROGRAMME_CYCLE_CREATE], self.business_area)

        self.graphql_request(
            request_string=CREATE_PROGRAM_CYCLE_MUTATION,
            context=self.context,
            variables={"programCycleData": inputs},
        )
        cycle_id = self.program.cycles.get(title="New Cycle for Update").pk
        encoded_cycle_id = self.id_to_base64(cycle_id, "ProgramCycleNode")
        # without perms
        self.snapshot_graphql_request(
            request_string=UPDATE_PROGRAM_CYCLE_MUTATION,
            context=self.context,
            variables={
                "programCycleData": {
                    "programCycleId": encoded_cycle_id,
                    "title": "NEW NEW NAME 1",
                    "startDate": "2055-11-12",
                }
            },
        )

        self.create_user_role_with_permissions(self.user, [Permissions.PM_PROGRAMME_CYCLE_UPDATE], self.business_area)

        self.snapshot_graphql_request(
            request_string=UPDATE_PROGRAM_CYCLE_MUTATION,
            context=self.context,
            variables={
                "programCycleData": {
                    "programCycleId": encoded_cycle_id,
                    "title": "NEW NEW NAME 22",
                    "startDate": "2055-11-13",
                }
            },
        )

        self.snapshot_graphql_request(
            request_string=UPDATE_PROGRAM_CYCLE_MUTATION,
            context=self.context,
            variables={
                "programCycleData": {
                    "programCycleId": encoded_cycle_id,
                    "startDate": "2055-11-14",
                    "endDate": "2055-11-22",
                }
            },
        )
        # title=None
        self.snapshot_graphql_request(
            request_string=UPDATE_PROGRAM_CYCLE_MUTATION,
            context=self.context,
            variables={
                "programCycleData": {
                    "programCycleId": encoded_cycle_id,
                    "title": None,
                    "startDate": "2055-11-11",
                    "endDate": "2055-11-11",
                }
            },
        )
        # start_date=None
        self.snapshot_graphql_request(
            request_string=UPDATE_PROGRAM_CYCLE_MUTATION,
            context=self.context,
            variables={
                "programCycleData": {
                    "programCycleId": encoded_cycle_id,
                    "title": "NEW NEW NAME2",
                    "startDate": None,
                    "endDate": "2055-11-21",
                }
            },
        )
        # end_date=None
        self.snapshot_graphql_request(
            request_string=UPDATE_PROGRAM_CYCLE_MUTATION,
            context=self.context,
            variables={
                "programCycleData": {
                    "programCycleId": encoded_cycle_id,
                    "startDate": "2055-11-11",
                    "endDate": None,
                }
            },
        )

    def test_delete_program_cycle(self) -> None:
        self.program.status = Program.ACTIVE
        self.program.save()

        inputs = {"title": "New Cycle 001", "startDate": "2055-11-11"}
        self.create_user_role_with_permissions(self.user, [Permissions.PM_PROGRAMME_CYCLE_CREATE], self.business_area)

        self.graphql_request(
            request_string=CREATE_PROGRAM_CYCLE_MUTATION,
            context=self.context,
            variables={"programCycleData": inputs},
        )

        cycle = self.program.cycles.get(title="New Cycle 001")
        encoded_cycle_id = self.id_to_base64(cycle.pk, "ProgramCycleNode")
        self.snapshot_graphql_request(
            request_string=DELETE_PROGRAM_CYCLE_MUTATION,
            context=self.context,
            variables={"programCycleId": encoded_cycle_id},
        )

        self.create_user_role_with_permissions(self.user, [Permissions.PM_PROGRAMME_CYCLE_DELETE], self.business_area)

        self.program.status = Program.DRAFT
        self.program.save()
        cycle.status = ProgramCycle.ACTIVE
        cycle.save()
        self.snapshot_graphql_request(
            request_string=DELETE_PROGRAM_CYCLE_MUTATION,
            context=self.context,
            variables={"programCycleId": encoded_cycle_id},
        )

        self.program.status = Program.ACTIVE
        self.program.save()
        self.snapshot_graphql_request(
            request_string=DELETE_PROGRAM_CYCLE_MUTATION,
            context=self.context,
            variables={"programCycleId": encoded_cycle_id},
        )

        cycle.status = ProgramCycle.DRAFT
        cycle.save()
        self.snapshot_graphql_request(
            request_string=DELETE_PROGRAM_CYCLE_MUTATION,
            context=self.context,
            variables={"programCycleId": encoded_cycle_id},
        )


class TestProgramCycleMethods(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        create_afghanistan()
        cls.user = UserFactory.create()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")
        cls.program = ProgramFactory(
            status=Program.DRAFT,
            business_area=cls.business_area,
            start_date="2020-01-01",
            end_date="2099-12-31",
            cycle__title="Default Cycle 001",
            cycle__start_date="2020-01-01",
            cycle__end_date="2020-01-02",
        )
        cls.cycle = ProgramCycleFactory(
            program=cls.program,
            start_date="2021-01-01",
            end_date="2022-01-01",
            title="Cycle 002",
        )

    def activate_program(self) -> None:
        self.cycle.program.status = Program.ACTIVE
        self.cycle.program.save()
        self.cycle.program.refresh_from_db()
        self.assertEqual(self.cycle.program.status, Program.ACTIVE)

    def test_set_active(self) -> None:
        with self.assertRaisesMessage(ValidationError, "Program should be within Active status."):
            self.cycle.set_active()
        self.activate_program()

        self.cycle.status = ProgramCycle.DRAFT
        self.cycle.save()
        self.assertEqual(self.cycle.status, ProgramCycle.DRAFT)
        self.cycle.set_active()
        self.cycle.refresh_from_db()
        self.assertEqual(self.cycle.status, ProgramCycle.ACTIVE)

        self.cycle.status = ProgramCycle.FINISHED
        self.cycle.save()
        self.assertEqual(self.cycle.status, ProgramCycle.FINISHED)
        self.cycle.set_active()
        self.cycle.refresh_from_db()
        self.assertEqual(self.cycle.status, ProgramCycle.ACTIVE)

        self.cycle.status = ProgramCycle.ACTIVE
        self.cycle.save()
        self.assertEqual(self.cycle.status, ProgramCycle.ACTIVE)
        self.cycle.set_active()
        self.cycle.refresh_from_db()
        self.assertEqual(self.cycle.status, ProgramCycle.ACTIVE)

    def test_set_draft(self) -> None:
        with self.assertRaisesMessage(ValidationError, "Program should be within Active status."):
            self.cycle.set_active()
        self.activate_program()

        self.cycle.status = ProgramCycle.FINISHED
        self.cycle.save()
        self.assertEqual(self.cycle.status, ProgramCycle.FINISHED)
        self.cycle.set_draft()
        self.cycle.refresh_from_db()
        self.assertEqual(self.cycle.status, ProgramCycle.FINISHED)

        self.cycle.status = ProgramCycle.ACTIVE
        self.cycle.save()
        self.assertEqual(self.cycle.status, ProgramCycle.ACTIVE)
        self.cycle.set_draft()
        self.cycle.refresh_from_db()
        self.assertEqual(self.cycle.status, ProgramCycle.DRAFT)

    def test_set_finish(self) -> None:
        with self.assertRaisesMessage(ValidationError, "Program should be within Active status."):
            self.cycle.set_finish()
        self.activate_program()

        self.cycle.status = ProgramCycle.DRAFT
        self.cycle.save()
        self.cycle.set_finish()
        self.cycle.refresh_from_db()
        self.assertEqual(self.cycle.status, ProgramCycle.DRAFT)

        self.cycle.status = ProgramCycle.ACTIVE
        self.cycle.save()
        self.cycle.set_finish()
        self.cycle.refresh_from_db()
        self.assertEqual(self.cycle.status, ProgramCycle.FINISHED)

    def test_total_entitled_quantity_usd(self) -> None:
        self.assertEqual(self.cycle.total_entitled_quantity_usd, Decimal("0.0"))
        PaymentPlanFactory(program=self.program, program_cycle=self.cycle, total_entitled_quantity_usd=Decimal(123.99))
        self.assertEqual(self.cycle.total_entitled_quantity_usd, Decimal("123.99"))

    def test_total_undelivered_quantity_usd(self) -> None:
        self.assertEqual(self.cycle.total_undelivered_quantity_usd, Decimal("0.0"))
        PaymentPlanFactory(
            program=self.program, program_cycle=self.cycle, total_undelivered_quantity_usd=Decimal(222.33)
        )
        self.assertEqual(self.cycle.total_undelivered_quantity_usd, Decimal("222.33"))

    def test_total_delivered_quantity_usd(self) -> None:
        self.assertEqual(self.cycle.total_delivered_quantity_usd, Decimal("0.0"))
        PaymentPlanFactory(program=self.program, program_cycle=self.cycle, total_delivered_quantity_usd=Decimal(333.11))
        self.assertEqual(self.cycle.total_delivered_quantity_usd, Decimal("333.11"))
