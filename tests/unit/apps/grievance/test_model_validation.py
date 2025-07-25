from django.core.exceptions import ValidationError
from django.http import QueryDict
from django.test import TestCase

from extras.test_utils.factories.account import UserFactory
from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.payment import (
    FinancialServiceProviderFactory,
    FinancialServiceProviderXlsxTemplateFactory,
    generate_delivery_mechanisms,
)

from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.grievance.models import GrievanceTicket
from hct_mis_api.admin.payment_admin import FspXlsxTemplatePerDeliveryMechanismForm
from hct_mis_api.apps.payment.models import DeliveryMechanism, FinancialServiceProvider


class TestGrievanceModelValidation(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
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

    def test_valid_issue_types(self) -> None:
        grievance_ticket_1 = GrievanceTicket(**self.base_model_data, **self.valid_model_data)
        grievance_ticket_2 = GrievanceTicket(**self.base_model_data, **self.valid_model_2_data)

        grievance_ticket_1.save()
        grievance_ticket_2.save()

        self.assertEqual(self.valid_model_data["issue_type"], grievance_ticket_1.issue_type)
        self.assertEqual(self.valid_model_2_data["issue_type"], grievance_ticket_2.issue_type)

    def test_invalid_issue_types(self) -> None:
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


class TestFspXlsxTemplatePerDeliveryMechanismValidation(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        create_afghanistan()
        cls.user = UserFactory.create()
        generate_delivery_mechanisms()
        cls.dm_transfer_to_account = DeliveryMechanism.objects.get(code="transfer_to_account")

    def test_admin_form_clean(self) -> None:
        fsp_xls_template = FinancialServiceProviderXlsxTemplateFactory()
        fsp = FinancialServiceProviderFactory(
            name="Test FSP",
            vision_vendor_number="123",
            communication_channel=FinancialServiceProvider.COMMUNICATION_CHANNEL_API,
        )
        fsp.delivery_mechanisms.add(self.dm_transfer_to_account)

        # test valid form
        form_data_standalone = {
            "financial_service_provider": fsp.id,
            "delivery_mechanism": self.dm_transfer_to_account.id,
            "xlsx_template": fsp_xls_template.id,
        }
        form_data_standalone_query_dict = QueryDict(mutable=True)
        for key, value in form_data_standalone.items():
            form_data_standalone_query_dict[key] = value

        form = FspXlsxTemplatePerDeliveryMechanismForm(data=form_data_standalone_query_dict)
        self.assertTrue(form.is_valid())
        form.clean()

        # test inline form data valid
        form_data_inline = {
            "financial_service_provider": fsp.id,
            "delivery_mechanism": self.dm_transfer_to_account.id,
            "xlsx_template": fsp_xls_template.id,
            "delivery_mechanisms": [str(self.dm_transfer_to_account.id)],
        }

        form_data_inline_query_dict = QueryDict(mutable=True)
        for key, value in form_data_inline.items():
            if isinstance(value, list):
                form_data_inline_query_dict.setlist(key, value)
                continue
            form_data_inline_query_dict[key] = value
        form = FspXlsxTemplatePerDeliveryMechanismForm(data=form_data_inline_query_dict)
        print(form.errors)
        self.assertTrue(form.is_valid())
        form.clean()

        # test delivery mechanism not supported
        fsp.delivery_mechanisms.remove(self.dm_transfer_to_account)
        form = FspXlsxTemplatePerDeliveryMechanismForm(data=form_data_standalone_query_dict)
        self.assertFalse(form.is_valid())
        with self.assertRaisesMessage(
            ValidationError,
            "['Delivery Mechanism Transfer to Account is not supported by Financial Service Provider Test FSP (123): API']",
        ):
            form.clean()

        # test inline form data invalid
        form_data_inline = {
            "financial_service_provider": fsp.id,
            "delivery_mechanism": self.dm_transfer_to_account.id,
            "xlsx_template": fsp_xls_template.id,
            "delivery_mechanisms": ["12313213123"],
        }
        form_data_inline_query_dict = QueryDict(mutable=True)
        for key, value in form_data_inline.items():
            form_data_inline_query_dict[key] = value
        form = FspXlsxTemplatePerDeliveryMechanismForm(data=form_data_inline_query_dict)
        self.assertFalse(form.is_valid())
        with self.assertRaisesMessage(
            ValidationError,
            "['Delivery Mechanism Transfer to Account is not supported by Financial Service Provider Test FSP (123): API']",
        ):
            form.clean()
