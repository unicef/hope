from typing import Callable
import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from hct_mis_api.apps.account.fixtures import BusinessAreaFactory, PartnerFactory, UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.utils import encode_id_base64_required
from hct_mis_api.apps.program.fixtures import ProgramFactory

pytestmark = pytest.mark.django_db


class TestPeriodicDataUpdateTemplateViews:
    def set_up(self, api_client: Callable, afghanistan: BusinessAreaFactory, id_to_base64: Callable) -> None:
        self.partner = PartnerFactory(name="TestPartner")
        self.user = UserFactory(partner=self.partner)
        self.client = api_client(self.user)
        self.afghanistan = afghanistan
        self.program = ProgramFactory(business_area=self.afghanistan)
        encoded_program_id = encode_id_base64_required(self.program.id, "Program")
        self.url_list = reverse(
            f"api:programs:{encoded_program_id}:periodic-data-update:periodic-data-update-templates",
            kwargs={
                "business_area": self.afghanistan.slug,
                "program_id": id_to_base64(self.program1.id, "Program"),
            },
        )
        self.url_detail = reverse(
            f"api:programs:{encoded_program_id}:periodic-data-update:periodic-data-update-templates",
            kwargs={
                "business_area": self.afghanistan.slug,
                "program_id": id_to_base64(self.program1.id, "Program"),
            },
        )

    @pytest.mark.parametrize(
        "permissions, expected_status",
        [
            ([], [], status.HTTP_403_FORBIDDEN),
            ([Permissions.PDU_VIEW_LIST_AND_DETAILS], [], status.HTTP_200_OK),
            ([], [Permissions.PDU_VIEW_LIST_AND_DETAILS], status.HTTP_200_OK),
            ([Permissions.PDU_VIEW_LIST_AND_DETAILS], [Permissions.PDU_VIEW_LIST_AND_DETAILS], status.HTTP_200_OK),
        ],
    )
    def test_list_periodic_data_update_templates_permission(
        self,
        permissions: list,
        partner_permissions: list,
        expected_status: str,
        api_client: Callable,
        afghanistan: BusinessAreaFactory,
        create_user_role_with_permissions: Callable,
        create_partner_role_with_permissions: Callable,
        id_to_base64: Callable,
    ) -> None:
        self.set_up(api_client, afghanistan, id_to_base64)
        create_user_role_with_permissions(
            self.user,
            permissions,
            self.afghanistan,
            self.program1,
        )
        create_partner_role_with_permissions(
            self.partner,
            partner_permissions,
            self.afghanistan
        )

        response = self.client.get(self.url_list)
        assert response.status_code == expected_status

    # Nala: test also access to program

    def test_list_periodic_data_update_templates(self, api_client: Callable, afghanistan: BusinessAreaFactory,
                                                 create_user_role_with_permissions: Callable,
                                                 update_partner_access_to_program: Callable,
                                                 id_to_base64: Callable) -> None:
        self.set_up(api_client, afghanistan, id_to_base64)
        response = self.client.get(self.url_list)
        assert response.status_code == status.HTTP_200_OK
