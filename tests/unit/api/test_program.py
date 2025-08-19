from datetime import timedelta

from django.utils import timezone

from extras.test_utils.factories.account import BusinessAreaFactory
from extras.test_utils.factories.core import DataCollectingTypeFactory
from extras.test_utils.factories.program import BeneficiaryGroupFactory, ProgramFactory
from rest_framework.reverse import reverse
from unit.api.base import HOPEApiTestCase, token_grant_permission

from hope.api.models import Grant
from hope.apps.core.models import BusinessArea
from hope.apps.program.models import Program


class APIProgramTests(HOPEApiTestCase):
    databases = {"default"}
    user_permissions = []

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.create_url = reverse("api:program-create", args=[cls.business_area.slug])
        cls.list_url = reverse("api:program-list", args=[cls.business_area.slug])

    def test_create_program(self) -> None:
        data_collecting_type = DataCollectingTypeFactory()
        beneficiary_group = BeneficiaryGroupFactory()
        data = {
            "name": "Program #1",
            "start_date": "2022-09-27",
            "end_date": "2022-09-27",
            "budget": "10000",
            "frequency_of_payments": "ONE_OFF",
            "sector": "CHILD_PROTECTION",
            "cash_plus": True,
            "population_goal": 101,
            "data_collecting_type": data_collecting_type.id,
            "beneficiary_group": str(beneficiary_group.id),
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
        assert program
        assert data == {
            "budget": "10000.00",
            "cash_plus": True,
            "end_date": "2022-09-27",
            "frequency_of_payments": "ONE_OFF",
            "id": str(program.id),
            "name": "Program #1",
            "population_goal": 101,
            "sector": "CHILD_PROTECTION",
            "start_date": "2022-09-27",
            "data_collecting_type": data_collecting_type.id,
            "beneficiary_group": str(beneficiary_group.id),
        }

        assert program.business_area == self.business_area

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

        assert response.status_code == 200
        assert len(response.json()) == 2
        assert {
            "budget": str(program1.budget),
            "cash_plus": program1.cash_plus,
            "end_date": program1.end_date.strftime("%Y-%m-%d"),
            "frequency_of_payments": program1.frequency_of_payments,
            "id": str(program1.id),
            "name": program1.name,
            "population_goal": program1.population_goal,
            "sector": program1.sector,
            "start_date": program1.start_date.strftime("%Y-%m-%d"),
            "data_collecting_type": program1.data_collecting_type_id,
            "beneficiary_group": str(program1.beneficiary_group_id),
        } in response.json()
        assert {
            "budget": str(program2.budget),
            "cash_plus": program2.cash_plus,
            "end_date": program2.end_date.strftime("%Y-%m-%d"),
            "frequency_of_payments": program2.frequency_of_payments,
            "id": str(program2.id),
            "name": program2.name,
            "population_goal": program2.population_goal,
            "sector": program2.sector,
            "start_date": program2.start_date.strftime("%Y-%m-%d"),
            "data_collecting_type": program2.data_collecting_type_id,
            "beneficiary_group": str(program2.beneficiary_group_id),
        } in response.json()


class APIGlobalProgramTests(HOPEApiTestCase):
    databases = {"default"}
    user_permissions = []

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.list_url = reverse("api:program-global-list")
        cls.program1: Program = ProgramFactory(
            budget=10000,
            start_date="2022-01-12",
            end_date="2022-09-12",
            business_area=cls.business_area,
            population_goal=200,
            status=Program.ACTIVE,
        )
        cls.program2: Program = ProgramFactory(
            budget=200,
            start_date="2022-01-10",
            end_date="2022-09-10",
            business_area=cls.business_area,
            population_goal=200,
            status=Program.DRAFT,
        )

        # program from another BA - also listed as we do not filter by BA
        cls.business_area2 = BusinessAreaFactory(name="Ukraine")
        cls.program_from_another_ba = ProgramFactory(
            budget=200,
            start_date="2022-01-10",
            end_date="2022-09-10",
            business_area=cls.business_area2,
            population_goal=400,
            status=Program.ACTIVE,
        )
        cls.program1.refresh_from_db()
        cls.program2.refresh_from_db()
        cls.program_from_another_ba.refresh_from_db()

        def expected_response(program: Program, business_area: BusinessArea) -> dict:
            return {
                "budget": str(program.budget),
                "business_area_code": business_area.code,
                "cash_plus": program.cash_plus,
                "end_date": program.end_date.strftime("%Y-%m-%d"),
                "frequency_of_payments": program.frequency_of_payments,
                "id": str(program.id),
                "name": program.name,
                "population_goal": program.population_goal,
                "programme_code": program.programme_code,
                "scope": program.scope,
                "sector": program.sector,
                "status": program.status,
                "start_date": program.start_date.strftime("%Y-%m-%d"),
                "beneficiary_group": str(program.beneficiary_group.id),
            }

        cls.program_from_another_ba_expected_response = expected_response(
            cls.program_from_another_ba,
            cls.business_area2,
        )

        cls.program1_expected_response = expected_response(
            cls.program1,
            cls.business_area,
        )
        cls.program2_expected_response = expected_response(
            cls.program2,
            cls.business_area,
        )

    def test_list_program(self) -> None:
        response = self.client.get(self.list_url)
        assert response.status_code == 403

        with token_grant_permission(self.token, Grant.API_READ_ONLY):
            response = self.client.get(self.list_url)
        assert response.status_code == 200
        assert len(response.json()["results"]) == 3
        assert self.program1_expected_response in response.json()["results"]
        assert self.program2_expected_response in response.json()["results"]
        assert self.program_from_another_ba_expected_response in response.json()["results"]

    def test_list_program_filter_business_area(self) -> None:
        with token_grant_permission(self.token, Grant.API_READ_ONLY):
            response = self.client.get(self.list_url, {"business_area": "afghanistan"})
        assert response.status_code == 200
        assert len(response.json()["results"]) == 2
        assert self.program_from_another_ba_expected_response not in response.json()["results"]

    def test_list_program_filter_active(self) -> None:
        with token_grant_permission(self.token, Grant.API_READ_ONLY):
            response = self.client.get(self.list_url, {"active": "true"})
        assert response.status_code == 200
        assert len(response.json()["results"]) == 2
        assert self.program2_expected_response not in response.json()["results"]

    def test_list_program_filter_not_active(self) -> None:
        with token_grant_permission(self.token, Grant.API_READ_ONLY):
            response = self.client.get(self.list_url, {"active": "false"})
        assert response.status_code == 200
        assert len(response.json()["results"]) == 1
        assert self.program2_expected_response in response.json()["results"]

    def test_list_program_filter_status(self) -> None:
        with token_grant_permission(self.token, Grant.API_READ_ONLY):
            response = self.client.get(self.list_url, {"status": Program.DRAFT})
        assert response.status_code == 200
        assert len(response.json()["results"]) == 1
        assert self.program2_expected_response in response.json()["results"]

    def test_list_program_filter_updated_at(self) -> None:
        tomorrow = (timezone.now() + timedelta(days=1)).date()
        tomorrow_str = tomorrow.strftime("%Y-%m-%d")
        yesterday = (timezone.now() - timedelta(days=1)).date()
        yesterday_str = yesterday.strftime("%Y-%m-%d")
        with token_grant_permission(self.token, Grant.API_READ_ONLY):
            response = self.client.get(self.list_url, {"updated_at_before": tomorrow_str})
        assert response.status_code == 200
        assert len(response.json()["results"]) == 3

        with token_grant_permission(self.token, Grant.API_READ_ONLY):
            response = self.client.get(self.list_url, {"updated_at_after": tomorrow_str})
        assert response.status_code == 200
        assert len(response.json()["results"]) == 0

        with token_grant_permission(self.token, Grant.API_READ_ONLY):
            response = self.client.get(self.list_url, {"updated_at_before": yesterday_str})
        assert response.status_code == 200
        assert len(response.json()["results"]) == 0

        with token_grant_permission(self.token, Grant.API_READ_ONLY):
            response = self.client.get(self.list_url, {"updated_at_after": yesterday_str})
        assert response.status_code == 200
        assert len(response.json()["results"]) == 3
