from account.fixtures import UserFactory
from core.fixtures import LocationFactory
from core.base_test_case import APITestCase
from program.fixtures import ProgramFactory
from program.models import Program


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
        self.user = UserFactory.create()
        self.location = LocationFactory.create()

    def test_draft_to_active(self):
        program = ProgramFactory.create(
            status='DRAFT',
        )

        self.snapshot_graphql_request(
            request_string=self.UPDATE_PROGRAM_MUTATION,
            context={'user': self.user},
            variables={
                'programData': {
                    'id': self.id_to_base64(program.id, 'Program'),
                    'status': 'ACTIVE'
                }
            },
        )

    def test_active_to_finished(self):
        program = ProgramFactory.create(
            status='ACTIVE',
        )

        self.snapshot_graphql_request(
            request_string=self.UPDATE_PROGRAM_MUTATION,
            context={'user': self.user},
            variables={
                'programData': {
                    'id': self.id_to_base64(program.id, 'Program'),
                    'status': 'FINISHED'
                }
            },
        )

    def test_finished_to_active(self):
        program = ProgramFactory.create(
            status='FINISHED',
        )

        self.snapshot_graphql_request(
            request_string=self.UPDATE_PROGRAM_MUTATION,
            context={'user': self.user},
            variables={
                'programData': {
                    'id': self.id_to_base64(program.id, 'Program'),
                    'status': 'ACTIVE'
                }
            },
        )

    def test_draft_to_finished(self):
        program = ProgramFactory.create(
            status='DRAFT',
        )

        self.snapshot_graphql_request(
            request_string=self.UPDATE_PROGRAM_MUTATION,
            context={'user': self.user},
            variables={
                'programData': {
                    'id': self.id_to_base64(program.id, 'Program'),
                    'status': 'FINISHED'
                }
            },
        )

    def test_active_to_draft(self):
        program = ProgramFactory.create(
            status='ACTIVE',
        )

        self.snapshot_graphql_request(
            request_string=self.UPDATE_PROGRAM_MUTATION,
            context={'user': self.user},
            variables={
                'programData': {
                    'id': self.id_to_base64(program.id, 'Program'),
                    'status': 'DRAFT'
                }
            },
        )

    def test_finished_to_draft(self):
        program = ProgramFactory.create(
            status='FINISHED',
        )

        self.snapshot_graphql_request(
            request_string=self.UPDATE_PROGRAM_MUTATION,
            context={'user': self.user},
            variables={
                'programData': {
                    'id': self.id_to_base64(program.id, 'Program'),
                    'status': 'DRAFT'
                }
            },
        )
