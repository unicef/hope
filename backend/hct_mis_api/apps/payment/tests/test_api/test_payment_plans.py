from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from hct_mis_api.apps.account.fixtures import PartnerFactory, UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.program.fixtures import ProgramFactory


class TestPaymentPlansListView(APITestCase):
    maxDiff = None

    def setUp(self) -> None:
        super().setUp()
        self.business_area = create_afghanistan()
        self.program = ProgramFactory(business_area=self.business_area)
        self.partner = PartnerFactory(name="TestPartner")
        self.headers = {
            "Business-Area": self.business_area.slug,
            "Program": self.id_to_base64(self.program.id, "ProgramNode"),
        }
        self.client = APIClient()
        self.maxDiff = None

    def test_list_payment_plans(self) -> None:
        url = reverse("payments:payment-plan-list")
        user = UserFactory(partner=self.partner)
        self.create_user_role_with_permissions(
            user,
            [Permissions.PM_VIEW_LIST, Permissions.PAYMENT_VIEW_LIST_NO_GPF],
            self.business_area,
            self.program,
        )
        self.client.force_authenticate(user=user)
        response = self.client.get(url, headers=self.headers)
        # self.assertEqual(response.status_code, status.HTTP_200_OK)
        print(response.__dict__)
        self.assertEqual(response.__dict__, [])
