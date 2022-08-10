from django.core.exceptions import ValidationError
from django.test import TestCase

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.grievance.models import GrievanceTicket


class TestGrievanceModelValidation(TestCase):
    @classmethod
    def setUpTestData(cls):
        create_afghanistan()
        cls.user = UserFactory.create()
        cls.base_model_data = {
            "status": GrievanceTicket.STATUS_NEW,
            "description": "test description",
            "area": "test area",
            "language": "english",
            "consent": True,
            "business_area": BusinessArea.objects.first(),
            "assigned_to": cls.user,
            "created_by": cls.user,
        }

        cls.valid_model_data = {
            "category": GrievanceTicket.CATEGORY_DATA_CHANGE,
            "issue_type": GrievanceTicket.ISSUE_TYPE_INDIVIDUAL_DATA_CHANGE_DATA_UPDATE,
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
            "issue_type": GrievanceTicket.ISSUE_TYPE_INDIVIDUAL_DATA_CHANGE_DATA_UPDATE,
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
            ValidationError,
            "{'issue_type': ['Invalid issue type for selected category']}",
            grievance_ticket_1.save,
        )
        self.assertRaisesMessage(
            ValidationError,
            "{'issue_type': ['Invalid issue type for selected category']}",
            grievance_ticket_2.save,
        )
