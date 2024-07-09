import contextlib
from typing import Iterator

from rest_framework.reverse import reverse

from hct_mis_api.api.models import APIToken, Grant
from hct_mis_api.api.tests.base import HOPEApiTestCase
from hct_mis_api.apps.account.fixtures import BusinessAreaFactory
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


class APIProgramTests(HOPEApiTestCase):
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
                "business_area_code": self.business_area.code,
                "cash_plus": True,
                "end_date": "2022-09-27",
                "frequency_of_payments": "ONE_OFF",
                "id": str(program.id),
                "name": "Program #1",
                "population_goal": 101,
                "programme_code": program.programme_code,
                "scope": program.scope,
                "sector": "CHILD_PROTECTION",
                "start_date": "2022-09-27",
                "status": program.status,
            },
        )

        self.assertEqual(program.business_area, self.business_area)

    def test_list_program(self) -> None:
        program1: Program = ProgramFactory(
            budget=10000,
            start_date="2022-01-12",
            end_date="2022-09-12",
            business_area=self.business_area,
            population_goal=200,
            status=Program.ACTIVE,
        )
        program2: Program = ProgramFactory(
            budget=200,
            start_date="2022-01-10",
            end_date="2022-09-10",
            business_area=self.business_area,
            population_goal=200,
            status=Program.DRAFT,
        )
        program1.refresh_from_db()
        program2.refresh_from_db()
        # program from another BA
        ProgramFactory(
            budget=200,
            start_date="2022-01-10",
            end_date="2022-09-10",
            business_area=BusinessAreaFactory(name="Ukraine"),
            population_goal=400,
            status=Program.ACTIVE,
        )
        response = self.client.get(self.list_url)
        assert response.status_code == 403
        with token_grant_permission(self.token, Grant.API_READ_ONLY):
            response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 2)
        self.assertIn(
            {
                "budget": str(program1.budget),
                "business_area_code": self.business_area.code,
                "cash_plus": program1.cash_plus,
                "end_date": program1.end_date.strftime("%Y-%m-%d"),
                "frequency_of_payments": program1.frequency_of_payments,
                "id": str(program1.id),
                "name": program1.name,
                "population_goal": program1.population_goal,
                "programme_code": program1.programme_code,
                "scope": program1.scope,
                "sector": program1.sector,
                "status": program1.status,
                "start_date": program1.start_date.strftime("%Y-%m-%d"),
            },
            response.json(),
        )
        self.assertIn(
            {
                "budget": str(program2.budget),
                "business_area_code": self.business_area.code,
                "cash_plus": program2.cash_plus,
                "end_date": program2.end_date.strftime("%Y-%m-%d"),
                "frequency_of_payments": program2.frequency_of_payments,
                "id": str(program2.id),
                "name": program2.name,
                "population_goal": program2.population_goal,
                "programme_code": program2.programme_code,
                "scope": program2.scope,
                "sector": program2.sector,
                "status": program2.status,
                "start_date": program2.start_date.strftime("%Y-%m-%d"),
            },
            response.json(),
        )
