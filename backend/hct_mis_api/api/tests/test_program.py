from rest_framework.reverse import reverse

from ...apps.program.models import Program
from ..models import Grant
from .base import HOPEApiTestCase


class CreateProgramTests(HOPEApiTestCase):
    databases = ["default"]
    user_permissions = [Grant.API_PROGRAM_CREATE]

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.url = reverse("api:program-create", args=[cls.business_area.slug])

    def test_create_program(self):
        data = {
            "name": "Program #1",
            "start_date": "2022-09-27",
            "end_date": "2022-09-27",
            "budget": "10000",
            "frequency_of_payments": "ONE_OFF",
            "sector": "CHILD_PROTECTION",
            "cash_plus": True,
            "population_goal": 101,
        }
        response = self.client.post(self.url, data, format="json")
        data = response.json()
        program: Program = Program.objects.filter(name="Program #1").first()
        self.assertTrue(program)
        self.assertDictEqual(
            data,
            {
                "budget": "10000.00",
                "cash_plus": True,
                "end_date": "2022-09-27",
                "frequency_of_payments": "ONE_OFF",
                "id": str(program.id),
                "name": "Program #1",
                "population_goal": 101,
                "sector": "CHILD_PROTECTION",
                "start_date": "2022-09-27",
            },
        )

        self.assertEqual(program.business_area, self.business_area)
