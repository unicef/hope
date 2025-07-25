from typing import Any

from django.core.management import call_command
from django.urls import reverse

import pytest
from extras.test_utils.factories.account import PartnerFactory, UserFactory

from hct_mis_api.apps.core.languages import LANGUAGES, Languages

pytestmark = pytest.mark.django_db


class TestChoicesViewSet:
    @pytest.fixture(autouse=True)
    def setup(self, api_client: Any) -> None:
        self.partner = PartnerFactory(name="unittest")
        self.user = UserFactory(partner=self.partner, first_name="Test", last_name="User")
        self.client = api_client(self.user)

    def test_get_payment_verification_plan_sampling(self) -> None:
        response = self.client.get(reverse("api:choices-payment-verification-plan-sampling"))
        assert response.status_code == 200
        response_data = response.data
        assert response_data is not None
        assert len(response_data) == 2
        assert "FULL_LIST" in response_data[0]["value"]
        assert "RANDOM" in response_data[1]["value"]
        assert response_data == [
            {"name": "Full list", "value": "FULL_LIST"},
            {"name": "Random sampling", "value": "RANDOM"},
        ]

    def test_get_payment_verification_summary_status(self) -> None:
        response = self.client.get(reverse("api:choices-payment-verification-summary-status"))
        assert response.status_code == 200
        response_data = response.data
        assert response_data is not None
        assert len(response_data) == 3
        assert "ACTIVE" in response_data[0]["value"]
        assert "FINISHED" in response_data[1]["value"]
        assert "PENDING" in response_data[2]["value"]
        assert response_data == [
            {"name": "Active", "value": "ACTIVE"},
            {"name": "Finished", "value": "FINISHED"},
            {"name": "Pending", "value": "PENDING"},
        ]

    def test_get_languages(self) -> None:
        # Test without filter
        response = self.client.get(reverse("api:choices-languages"))
        assert response.status_code == 200
        response_data = response.data
        assert len(response_data) == len(LANGUAGES)
        expected_data_full = sorted(
            [{"name": lang.english, "value": lang.code} for lang in LANGUAGES], key=lambda x: x["name"].lower()
        )
        assert sorted(response_data, key=lambda x: x["name"].lower()) == expected_data_full

        # Test with filter code "en"
        response_en = self.client.get(reverse("api:choices-languages"), {"code": "en"})
        assert response_en.status_code == 200
        response_data_en = response_en.data
        assert len(response_data_en) < len(response_data)
        filtered_langs_en = Languages.filter_by_code("en")
        expected_data_en = sorted(
            [{"name": lang.english, "value": lang.code} for lang in filtered_langs_en], key=lambda x: x["name"].lower()
        )
        assert len(response_data_en) == len(expected_data_en)
        assert sorted(response_data_en, key=lambda x: x["name"].lower()) == expected_data_en
        # Check if English is present
        assert any(lang["value"] == "en-us" for lang in response_data_en)

        # Test with filter code "Pols"
        response_pl = self.client.get(reverse("api:choices-languages"), {"code": "Pols"})
        assert response_pl.status_code == 200
        response_data_pl = response_pl.data
        assert len(response_data_pl) == 1
        filtered_langs_pl = Languages.filter_by_code("Pols")
        expected_data_pl = sorted(
            [{"name": lang.english, "value": lang.code} for lang in filtered_langs_pl], key=lambda x: x["name"].lower()
        )
        assert len(response_data_pl) == len(expected_data_pl)
        assert sorted(response_data_pl, key=lambda x: x["name"].lower()) == expected_data_pl
        # Check if Polish is present
        assert any(lang["value"] == "pl-pl" for lang in response_data_pl)

        # Test with filter code that matches nothing
        response_none = self.client.get(reverse("api:choices-languages"), {"code": "xyzabc"})
        assert response_none.status_code == 200
        assert len(response_none.data) == 0

    def test_get_countries(self) -> None:
        call_command("loadcountries")
        response = self.client.get(reverse("api:choices-countries"))
        assert response.status_code == 200
        response_data = response.data
        assert response_data is not None
        assert len(response_data) == 250
        assert response_data[0] == {"name": "ABW", "value": "Aruba"}
