from typing import Any, List, Optional

from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
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
            name
            startDate
            endDate
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
            name
            startDate
            endDate
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
            name
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
            cycle__name="Default Cycle 001",
            cycle__start_date="2020-01-01",
            cycle__end_date="2020-01-02",
        )
        cls.program_cycle = ProgramCycleFactory(
            program=cls.program,
            start_date="2021-01-01",
            end_date="2022-01-01",
            name="Cycle 002",
        )

    @parameterized.expand(
        [
            ("without_permission_program_in_draft", [], Program.DRAFT, {}),
            ("with_permission_program_in_draft", [Permissions.PROGRAMME_CYCLE_CREATE], Program.DRAFT, {}),
            (
                "with_permission_program_in_active_wrong_start_date",
                [Permissions.PROGRAMME_CYCLE_CREATE],
                Program.ACTIVE,
                {"start_date": "1999-01-01"},
            ),
            (
                "with_permission_program_in_active_wrong_end_date",
                [Permissions.PROGRAMME_CYCLE_CREATE],
                Program.ACTIVE,
                {"end_date": "2999-01-01"},
            ),
            (
                "with_permission_program_in_active_end_date_is_more_then_start_date",
                [Permissions.PROGRAMME_CYCLE_CREATE],
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
            "name": "Test Name Program Cycle New",
            "startDate": kwargs.get("start_date", "2022-11-11"),
            "endDate": kwargs.get("end_date"),
        }

        self.snapshot_graphql_request(
            request_string=CREATE_PROGRAM_CYCLE_MUTATION,
            context={"user": self.user, "headers": {"Program": self.id_to_base64(self.program.id, "ProgramNode")}},
            variables={"programCycleData": inputs},
        )

    def test_create_program_cycle_when_cycles_without_end_date(self) -> None:
        self.create_user_role_with_permissions(self.user, [Permissions.PROGRAMME_CYCLE_CREATE], self.business_area)
        self.program.status = Program.ACTIVE
        self.program.save()

        inputs = {
            "name": "Test Name Program Cycle New 002",
            "startDate": "2022-11-11",
        }
        context = {"user": self.user, "headers": {"Program": self.id_to_base64(self.program.id, "ProgramNode")}}

        self.graphql_request(
            request_string=CREATE_PROGRAM_CYCLE_MUTATION,
            context=context,
            variables={"programCycleData": inputs},
        )
        self.snapshot_graphql_request(
            request_string=CREATE_PROGRAM_CYCLE_MUTATION,
            context=context,
            variables={
                "programCycleData": {"name": "Cycle New Name", "startDate": "2022-11-25", "endDate": "2022-12-12"}
            },
        )

    def test_create_program_cycle_when_cycles_overlapping(self) -> None:
        self.create_user_role_with_permissions(self.user, [Permissions.PROGRAMME_CYCLE_CREATE], self.business_area)
        self.program.status = Program.ACTIVE
        self.program.save()

        inputs = {"name": "Test Name Program Cycle New 002", "startDate": "2055-11-11", "endDate": "2055-11-30"}
        context = {"user": self.user, "headers": {"Program": self.id_to_base64(self.program.id, "ProgramNode")}}

        # cycle "2055/11/11"->"2055/11/30"
        self.graphql_request(
            request_string=CREATE_PROGRAM_CYCLE_MUTATION,
            context=context,
            variables={"programCycleData": inputs},
        )
        self.snapshot_graphql_request(
            request_string=CREATE_PROGRAM_CYCLE_MUTATION,
            context=context,
            variables={"programCycleData": {"name": "Cycle New 333", "startDate": "2055-11-25"}},
        )
        self.snapshot_graphql_request(
            request_string=CREATE_PROGRAM_CYCLE_MUTATION,
            context=context,
            variables={
                "programCycleData": {"name": "Cycle New 444", "startDate": "2055-11-25", "endDate": "2055-12-12"}
            },
        )

    def test_create_program_cycle_with_the_same_name(self) -> None:
        self.create_user_role_with_permissions(self.user, [Permissions.PROGRAMME_CYCLE_CREATE], self.business_area)
        self.program.status = Program.ACTIVE
        self.program.save()

        inputs = {
            "name": "TheSameName",
            "startDate": "2055-11-11",
            "endDate": "2055-12-12",
        }
        context = {"user": self.user, "headers": {"Program": self.id_to_base64(self.program.id, "ProgramNode")}}

        self.graphql_request(
            request_string=CREATE_PROGRAM_CYCLE_MUTATION,
            context=context,
            variables={"programCycleData": inputs},
        )
        self.snapshot_graphql_request(
            request_string=CREATE_PROGRAM_CYCLE_MUTATION,
            context=context,
            variables={"programCycleData": {"name": "TheSameName", "startDate": "2056-01-01"}},
        )

    def test_update_program_cycle(self) -> None:
        self.program.status = Program.ACTIVE
        self.program.save()

        inputs = {"name": "New Cycle for Update", "startDate": "2055-11-11"}
        context = {"user": self.user, "headers": {"Program": self.id_to_base64(self.program.id, "ProgramNode")}}
        self.create_user_role_with_permissions(self.user, [Permissions.PROGRAMME_CYCLE_CREATE], self.business_area)

        self.graphql_request(
            request_string=CREATE_PROGRAM_CYCLE_MUTATION,
            context=context,
            variables={"programCycleData": inputs},
        )
        cycle_id = self.program.cycles.get(name="New Cycle for Update").pk
        encoded_cycle_id = self.id_to_base64(cycle_id, "ProgramCycleNode")
        # without perms
        self.snapshot_graphql_request(
            request_string=UPDATE_PROGRAM_CYCLE_MUTATION,
            context={"user": self.user, "headers": {"Program": self.id_to_base64(self.program.id, "ProgramNode")}},
            variables={
                "programCycleData": {
                    "programCycleId": encoded_cycle_id,
                    "name": "NEW NEW NAME 1",
                    "startDate": "2055-11-12",
                }
            },
        )

        self.create_user_role_with_permissions(self.user, [Permissions.PROGRAMME_CYCLE_UPDATE], self.business_area)

        self.snapshot_graphql_request(
            request_string=UPDATE_PROGRAM_CYCLE_MUTATION,
            context={"user": self.user, "headers": {"Program": self.id_to_base64(self.program.id, "ProgramNode")}},
            variables={
                "programCycleData": {
                    "programCycleId": encoded_cycle_id,
                    "name": "NEW NEW NAME 22",
                    "startDate": "2055-11-13",
                }
            },
        )

        self.snapshot_graphql_request(
            request_string=UPDATE_PROGRAM_CYCLE_MUTATION,
            context={"user": self.user, "headers": {"Program": self.id_to_base64(self.program.id, "ProgramNode")}},
            variables={
                "programCycleData": {
                    "programCycleId": encoded_cycle_id,
                    "name": "NEW NEW NAME 333",
                    "startDate": "2055-11-14",
                    "endDate": "2055-11-22",
                }
            },
        )
        # name=None
        self.snapshot_graphql_request(
            request_string=UPDATE_PROGRAM_CYCLE_MUTATION,
            context={"user": self.user, "headers": {"Program": self.id_to_base64(self.program.id, "ProgramNode")}},
            variables={
                "programCycleData": {
                    "programCycleId": encoded_cycle_id,
                    "name": None,
                    "startDate": "2055-11-11",
                    "endDate": "2055-11-11",
                }
            },
        )
        # start_date=None
        self.snapshot_graphql_request(
            request_string=UPDATE_PROGRAM_CYCLE_MUTATION,
            context={"user": self.user, "headers": {"Program": self.id_to_base64(self.program.id, "ProgramNode")}},
            variables={
                "programCycleData": {
                    "programCycleId": encoded_cycle_id,
                    "name": "NEW NEW NAME2",
                    "startDate": None,
                    "endDate": "2055-11-21",
                }
            },
        )
        # end_date=None
        self.snapshot_graphql_request(
            request_string=UPDATE_PROGRAM_CYCLE_MUTATION,
            context={"user": self.user, "headers": {"Program": self.id_to_base64(self.program.id, "ProgramNode")}},
            variables={
                "programCycleData": {
                    "programCycleId": encoded_cycle_id,
                    "name": "NEW NEW NAME3",
                    "startDate": "2055-11-11",
                    "endDate": None,
                }
            },
        )

    def test_delete_program_cycle(self) -> None:
        self.program.status = Program.ACTIVE
        self.program.save()

        inputs = {"name": "New Cycle 001", "startDate": "2055-11-11"}
        context = {"user": self.user, "headers": {"Program": self.id_to_base64(self.program.id, "ProgramNode")}}
        self.create_user_role_with_permissions(self.user, [Permissions.PROGRAMME_CYCLE_CREATE], self.business_area)

        self.graphql_request(
            request_string=CREATE_PROGRAM_CYCLE_MUTATION,
            context=context,
            variables={"programCycleData": inputs},
        )

        cycle = self.program.cycles.filter(name="New Cycle 001").first()
        encoded_cycle_id = self.id_to_base64(cycle.pk, "ProgramCycleNode")
        self.snapshot_graphql_request(
            request_string=DELETE_PROGRAM_CYCLE_MUTATION,
            context=context,
            variables={"programCycleId": encoded_cycle_id},
        )

        self.create_user_role_with_permissions(self.user, [Permissions.PROGRAMME_CYCLE_REMOVE], self.business_area)

        self.program.status = Program.DRAFT
        self.program.save()
        cycle.status = ProgramCycle.ACTIVE
        cycle.save()
        self.snapshot_graphql_request(
            request_string=DELETE_PROGRAM_CYCLE_MUTATION,
            context=context,
            variables={"programCycleId": encoded_cycle_id},
        )

        self.program.status = Program.ACTIVE
        self.program.save()
        self.snapshot_graphql_request(
            request_string=DELETE_PROGRAM_CYCLE_MUTATION,
            context=context,
            variables={"programCycleId": encoded_cycle_id},
        )

        cycle.status = ProgramCycle.DRAFT
        cycle.save()
        self.snapshot_graphql_request(
            request_string=DELETE_PROGRAM_CYCLE_MUTATION,
            context=context,
            variables={"programCycleId": encoded_cycle_id},
        )
