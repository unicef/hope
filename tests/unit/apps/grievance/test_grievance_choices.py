from typing import Any

from extras.test_utils.factories.account import PartnerFactory, UserFactory
from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.household import DocumentTypeFactory
import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from hope.apps.account.permissions import Permissions
from hope.apps.core.utils import to_choice_object
from hope.apps.grievance.constants import PRIORITY_CHOICES, URGENCY_CHOICES
from hope.apps.grievance.models import GrievanceTicket
from hope.apps.household.models import DocumentType

pytestmark = pytest.mark.django_db()


class TestGrievanceChoices:
    @pytest.fixture(autouse=True)
    def setup(self, api_client: Any) -> None:
        self.choices_url = "api:grievance:grievance-tickets-global-choices"
        self.afghanistan = create_afghanistan()
        self.partner = PartnerFactory(name="TestPartner")
        self.user = UserFactory(partner=self.partner)
        self.api_client = api_client(self.user)

        DocumentTypeFactory(key="passport", label="Passport")
        DocumentTypeFactory(key="id_card", label="ID Card")
        DocumentTypeFactory(key="birth_certificate", label="Birth Certificate")

    def test_get_choices_without_permissions(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PROGRAMME_FINISH],
            business_area=self.afghanistan,
        )
        response = self.api_client.get(reverse(self.choices_url, kwargs={"business_area_slug": self.afghanistan.slug}))
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_choices(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE],
            business_area=self.afghanistan,
        )
        response = self.api_client.get(reverse(self.choices_url, kwargs={"business_area_slug": self.afghanistan.slug}))
        categories = dict(GrievanceTicket.CATEGORY_CHOICES)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == {
            "grievance_ticket_status_choices": to_choice_object(GrievanceTicket.STATUS_CHOICES),
            "grievance_ticket_category_choices": to_choice_object(GrievanceTicket.CATEGORY_CHOICES),
            "grievance_ticket_manual_category_choices": to_choice_object(GrievanceTicket.CREATE_CATEGORY_CHOICES),
            "grievance_ticket_system_category_choices": to_choice_object(GrievanceTicket.SYSTEM_CATEGORIES),
            "grievance_ticket_priority_choices": to_choice_object(PRIORITY_CHOICES),
            "grievance_ticket_urgency_choices": to_choice_object(URGENCY_CHOICES),
            "grievance_ticket_issue_type_choices": [
                {"category": key, "label": categories[key], "sub_categories": value}
                for (key, value) in GrievanceTicket.ISSUE_TYPES_CHOICES.items()
            ],
            "document_type_choices": [
                {"name": str(document_type.label), "value": document_type.key}
                for document_type in DocumentType.objects.order_by("key")
            ],
        }
