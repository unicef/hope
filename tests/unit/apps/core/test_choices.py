from typing import Any

from django.urls import reverse

import pytest

from hct_mis_api.apps.account.fixtures import PartnerFactory, UserFactory

pytestmark = pytest.mark.django_db


class TestFeedbackViewSet:
    @pytest.fixture(autouse=True)
    def setup(self, api_client: Any) -> None:
        self.partner = PartnerFactory(name="unittest")
        self.user = UserFactory(partner=self.partner, first_name="Test", last_name="User")
        self.client = api_client(self.user)

    def test_payment_verification_plan_sampling(self) -> None:
        response_data = self.client.get(reverse("api:choices-payment-verification-plan-sampling")).data
        assert response_data is not None
        assert len(response_data) == 2
        assert "FULL_LIST" in response_data[0]["value"]
        assert "RANDOM" in response_data[1]["value"]
