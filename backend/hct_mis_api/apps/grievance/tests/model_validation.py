from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.test import TestCase

from core.models import BusinessArea
from grievance.models import GrievanceTicket


class TestGrievanceModelValidation(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("loadbusinessareas")

        cls.base_model_data = {
            "status": GrievanceTicket.STATUS_OPEN,
            "description": "test description",
            "admin": "test admin",
            "area": "test area",
            "language": "english",
            "consent": True,
            "business_area": BusinessArea.objects.first(),
        }

        cls.valid_model_data = {
            "category": GrievanceTicket.CATEGORY_DATA_CHANGE,
            "issue_type": GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_DATA_UPDATE,
        }

        cls.valid_model_2_data = {
            "category": GrievanceTicket.CATEGORY_POSITIVE_FEEDBACK,
            "issue_type": None,
        }

        cls.invalid_model_data = {
            "category": GrievanceTicket.CATEGORY_DATA_CHANGE,
            "issue_type": None,
        }

        cls.invalid_model_2_data = {
            "category": GrievanceTicket.CATEGORY_POSITIVE_FEEDBACK,
            "issue_type": GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_DATA_UPDATE,
        }

    def test_valid_issue_types(self):
        grievance_ticket_1 = GrievanceTicket(**self.base_model_data, **self.valid_model_data)
        grievance_ticket_2 = GrievanceTicket(**self.base_model_data, **self.valid_model_2_data)

        grievance_ticket_1.save()
        grievance_ticket_2.save()

        self.assertEqual(self.valid_model_data["issue_type"], grievance_ticket_1.issue_type)
        self.assertEqual(self.valid_model_2_data["issue_type"], grievance_ticket_2.issue_type)

    def test_invalid_issue_types(self):
        grievance_ticket_1 = GrievanceTicket(**self.base_model_data, **self.invalid_model_data)
        grievance_ticket_2 = GrievanceTicket(**self.base_model_data, **self.invalid_model_2_data)

        self.assertRaisesMessage(
            ValidationError, "{'issue_type': ['Invalid subcategory for selected category']}", grievance_ticket_1.save,
        )
        self.assertRaisesMessage(
            ValidationError, "{'issue_type': ['Invalid subcategory for selected category']}", grievance_ticket_2.save,
        )
