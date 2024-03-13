import contextlib
from typing import Iterator

from rest_framework.reverse import reverse

from hct_mis_api.api.models import APIToken, Grant
from hct_mis_api.api.tests.base import HOPEApiTestCase
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program


@contextlib.contextmanager
def token_grant_permission(token: APIToken, grant: Grant) -> Iterator:
    old = token.grants
    token.grants += [grant.name]
    token.save()
    yield
    token.grants = old
    token.save()


class CreateProgramTests(HOPEApiTestCase):
    databases = {"default"}
    user_permissions = []

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.create_url = reverse("api:program-create", args=[cls.business_area.slug])
        cls.list_url = reverse("api:program-list", args=[cls.business_area.slug])

    def test_create_program(self) -> None:
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
        response = self.client.post(self.create_url, data, format="json")
        assert response.status_code == 403

        with token_grant_permission(self.token, Grant.API_READ_ONLY):
            response = self.client.post(self.create_url, data, format="json")
            assert response.status_code == 403

        with token_grant_permission(self.token, Grant.API_PROGRAM_CREATE):
            response = self.client.post(self.create_url, data, format="json")

        assert response.status_code == 201, data
        data = response.json()

        if not (program := Program.objects.filter(name="Program #1").first()):
            self.fail("Program was not present")
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

    def test_list_program(self) -> None:
        program: Program = ProgramFactory(
            budget=10000,
            start_date="2022-01-12",
            end_date="2022-09-12",
            business_area=self.business_area,
            population_goal=200,
        )
        with token_grant_permission(self.token, Grant.API_READ_ONLY):
            response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        self.assertDictEqual(
            response.json()[0],
            {
                "budget": "10000.00",
                "cash_plus": program.cash_plus,
                "end_date": "2022-09-12",
                "frequency_of_payments": program.frequency_of_payments,
                "id": str(program.id),
                "name": program.name,
                "population_goal": 200,
                "sector": program.sector,
                "start_date": "2022-01-12",
            },
        )
