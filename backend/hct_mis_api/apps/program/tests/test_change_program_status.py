from account.fixtures import UserFactory
from core.fixtures import LocationFactory
from core.tests import APITestCase
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
        self.base_program_data = {
            'name': 'Test',
            'start_date': '2019-12-20T15:00:00',
            'end_date': '2021-12-20T15:00:00',
            'location_id': self.location.id,
            'program_ca_id': '5e0a38c6-7bcb-4b4a-b8e0-311e8c694ae3',
            'budget': 20000000,
            'description': 'my description of program',
            'frequency_of_payments': 'REGULAR',
            'sector': 'EDUCATION',
            'scope': 'FULL',
            'cash_plus': True,
            'population_goal': 150000,
        }

    def test_draft_to_active(self):
        program = Program.objects.create(
            status='DRAFT',
            **self.base_program_data,
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
        program = Program.objects.create(
            status='ACTIVE',
            **self.base_program_data,
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
        program = Program.objects.create(
            status='FINISHED',
            **self.base_program_data,
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
        program = Program.objects.create(
            status='DRAFT',
            **self.base_program_data,
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
        program = Program.objects.create(
            status='ACTIVE',
            **self.base_program_data,
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
        program = Program.objects.create(
            status='FINISHED',
            **self.base_program_data,
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
