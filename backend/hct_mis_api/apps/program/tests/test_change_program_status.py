from django.core.management import call_command

from account.fixtures import UserFactory
from core.base_test_case import APITestCase
from core.fixtures import AdminAreaFactory
from core.models import BusinessArea
from program.fixtures import ProgramFactory


class TestChangeProgramStatus(APITestCase):
    UPDATE_PROGRAM_MUTATION = """
    mutation UpdateProgram($programData: UpdateProgramInput) {
      updateProgram(programData: $programData) {
        program {
          status
        }
      }
    }
    """

    def setUp(self):
        super().setUp()
        call_command("loadbusinessareas")
        self.user = UserFactory.create()
        self.location = AdminAreaFactory.create()

    def test_draft_to_active(self):
        program = ProgramFactory.create(
            status="DRAFT",
            business_area=BusinessArea.objects.order_by("?").first(),
        )

        self.snapshot_graphql_request(
            request_string=self.UPDATE_PROGRAM_MUTATION,
            context={"user": self.user},
            variables={
                "programData": {
                    "id": self.id_to_base64(program.id, "Program"),
                    "status": "ACTIVE",
                }
            },
        )

    def test_active_to_finished(self):
        program = ProgramFactory.create(
            status="ACTIVE",
            business_area=BusinessArea.objects.order_by("?").first(),
        )

        self.snapshot_graphql_request(
            request_string=self.UPDATE_PROGRAM_MUTATION,
            context={"user": self.user},
            variables={
                "programData": {
                    "id": self.id_to_base64(program.id, "Program"),
                    "status": "FINISHED",
                }
            },
        )

    def test_finished_to_active(self):
        program = ProgramFactory.create(
            status="FINISHED",
            business_area=BusinessArea.objects.order_by("?").first(),
        )

        self.snapshot_graphql_request(
            request_string=self.UPDATE_PROGRAM_MUTATION,
            context={"user": self.user},
            variables={
                "programData": {
                    "id": self.id_to_base64(program.id, "Program"),
                    "status": "ACTIVE",
                }
            },
        )

    def test_draft_to_finished(self):
        program = ProgramFactory.create(
            status="DRAFT",
            business_area=BusinessArea.objects.order_by("?").first(),
        )

        self.snapshot_graphql_request(
            request_string=self.UPDATE_PROGRAM_MUTATION,
            context={"user": self.user},
            variables={
                "programData": {
                    "id": self.id_to_base64(program.id, "Program"),
                    "status": "FINISHED",
                }
            },
        )

    def test_active_to_draft(self):
        program = ProgramFactory.create(
            status="ACTIVE",
            business_area=BusinessArea.objects.order_by("?").first(),
        )

        self.snapshot_graphql_request(
            request_string=self.UPDATE_PROGRAM_MUTATION,
            context={"user": self.user},
            variables={
                "programData": {
                    "id": self.id_to_base64(program.id, "Program"),
                    "status": "DRAFT",
                }
            },
        )

    def test_finished_to_draft(self):
        program = ProgramFactory.create(
            status="FINISHED",
            business_area=BusinessArea.objects.order_by("?").first(),
        )

        self.snapshot_graphql_request(
            request_string=self.UPDATE_PROGRAM_MUTATION,
            context={"user": self.user},
            variables={
                "programData": {
                    "id": self.id_to_base64(program.id, "Program"),
                    "status": "DRAFT",
                }
            },
        )
