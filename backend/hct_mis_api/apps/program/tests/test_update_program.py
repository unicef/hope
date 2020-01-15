from account.fixtures import UserFactory
from core.fixtures import LocationFactory
from core.tests import APITestCase
from program.models import Program


class TestUpdateProgram(APITestCase):
    UPDATE_PROGRAM_MUTATION = """
    mutation UpdateProgram($programData: UpdateProgramInput) {
      updateProgram(programData: $programData) {
        program {
          name
          status
        }
      }
    }
    """

    def test_update_program_not_authenticated(self):
        self.snapshot_graphql_request(
            request_string=self.UPDATE_PROGRAM_MUTATION,
            variables={
                'programData': {
                    'id': 'UHJvZ3JhbU5vZGU6MTc4MWEwMGMtMjhl'
                          'OS00OGRmLTlhOTUtZDg5ZWVmYWM1ZmY0',
                    'name': 'updated name',
                    'status': 'FINISHED'
                }
            },
        )

    def test_update_program_authenticated(self):
        user = UserFactory.create()
        location = LocationFactory.create()

        program = Program.objects.create(
            name='Test',
            status='DRAFT',
            start_date='2019-12-20T15:00:00',
            end_date='2021-12-20T15:00:00',
            location_id=location.id,
            program_ca_id='5e0a38c6-7bcb-4b4a-b8e0-311e8c694ae3',
            budget=20000000,
            description='my description of program',
            frequency_of_payments='REGULAR',
            sector='EDUCATION',
            scope='FULL',
            cash_plus=True,
            population_goal=150000,
        )

        self.snapshot_graphql_request(
            request_string=self.UPDATE_PROGRAM_MUTATION,
            context={'user': user},
            variables={
                'programData': {
                    'id': self.id_to_base64(program.id, 'Program'),
                    'name': 'updated name',
                    'status': 'ACTIVE'
                }
            },
        )

        updated_program = Program.objects.get(id=program.id)

        assert updated_program.status == 'ACTIVE'
        assert updated_program.name == 'updated name'
