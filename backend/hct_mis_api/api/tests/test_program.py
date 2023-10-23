from rest_framework.reverse import reverse

from hct_mis_api.api.models import Grant
from hct_mis_api.api.tests.base import HOPEApiTestCase
from hct_mis_api.apps.account.fixtures import BusinessAreaFactory
from hct_mis_api.apps.core.fixtures import DataCollectingTypeFactory
from hct_mis_api.apps.program.models import Program


class CreateProgramTests(HOPEApiTestCase):
    databases = {"default"}
    user_permissions = [Grant.API_PROGRAM_CREATE]

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.url = reverse("api:program-create", args=[cls.business_area.slug])
        cls.business_area_ukraine = BusinessAreaFactory(name="ukraine")
        cls.data_collecting_type = DataCollectingTypeFactory(business_areas=[cls.business_area_ukraine])

    def test_create_program(self) -> None:
        self.maxDiff = None
        data = {
            "name": "Program #1",
            "start_date": "2022-09-27",
            "end_date": "2022-09-27",
            "budget": "10000",
            "frequency_of_payments": "ONE_OFF",
            "sector": "CHILD_PROTECTION",
            "cash_plus": True,
            "population_goal": 101,
            "business_area": self.business_area.id,
            "data_collecting_type": self.data_collecting_type.id,
        }
        response = self.client.post(self.url, data, format="json")
        program = Program.objects.filter(name=data["name"]).first()
        self.assertEqual(program.name, data["name"])
        if not (program := Program.objects.filter(name="Program #1").first()):
            self.fail("Program was not present")
        self.assertTrue(program)
        self.assertDictEqual(
            response.json(),
            {
                "id": str(program.id),
                "name": "Program #1",
                "start_date": "2022-09-27",
                "end_date": "2022-09-27",
                "budget": "10000.00",
                "frequency_of_payments": "ONE_OFF",
                "sector": "CHILD_PROTECTION",
                "cash_plus": True,
                "population_goal": 101,
                "business_area": str(self.business_area.id),
                "data_collecting_type": {
                    "id": self.data_collecting_type.id,
                    "label": self.data_collecting_type.label,
                    "code": self.data_collecting_type.code,
                    "description": "",
                    "active": True,
                    "individual_filters_available": False,
                    "household_filters_available": True,
                    "recalculate_composition": False,
                    "compatible_types": [],
                    "limit_to": [self.business_area_ukraine.slug],
                },
            },
        )

        self.assertEqual(program.business_area, self.business_area)
