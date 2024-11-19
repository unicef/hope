from django.core.exceptions import ValidationError
from django.test import TestCase

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.grievance.models import GrievanceTicket
from hct_mis_api.apps.payment.admin import FspXlsxTemplatePerDeliveryMechanismForm
from hct_mis_api.apps.payment.fixtures import (
    FinancialServiceProviderFactory,
    FinancialServiceProviderXlsxTemplateFactory,
    generate_delivery_mechanisms,
)
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
        fsp_xls_template = FinancialServiceProviderXlsxTemplateFactory(
            core_fields=["bank_name__transfer_to_account", "bank_account_number__transfer_to_account"]
        )

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
        form = FspXlsxTemplatePerDeliveryMechanismForm(data=form_data_standalone)
        self.assertTrue(form.is_valid())
        form.clean()

        # test inline form data valid
        form_data_inline = {
            "financial_service_provider": fsp.id,
            "delivery_mechanism": self.dm_transfer_to_account.id,
            "xlsx_template": fsp_xls_template.id,
            "delivery_mechanisms": [str(self.dm_transfer_to_account.id)],
        }
        form = FspXlsxTemplatePerDeliveryMechanismForm(data=form_data_inline)
        self.assertTrue(form.is_valid())
        form.clean()

        # test missing required core fields
        fsp_xls_template.core_fields = []
        fsp_xls_template.save()

        form = FspXlsxTemplatePerDeliveryMechanismForm(data=form_data_standalone)
        self.assertFalse(form.is_valid())
        with self.assertRaisesMessage(
            ValidationError,
            "[\"['bank_name__transfer_to_account', 'bank_account_number__transfer_to_account'] fields are required by delivery mechanism Transfer to Account and must be present in the template core fields\"]",
        ):
            form.clean()

        fsp_xls_template.core_fields = ["bank_name__transfer_to_account", "bank_account_number__transfer_to_account"]
        fsp_xls_template.save()

        # test delivery mechanism not supported
        fsp.delivery_mechanisms.remove(self.dm_transfer_to_account)
        form = FspXlsxTemplatePerDeliveryMechanismForm(data=form_data_standalone)
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
        form = FspXlsxTemplatePerDeliveryMechanismForm(data=form_data_inline)
        self.assertFalse(form.is_valid())
        with self.assertRaisesMessage(
            ValidationError,
            "['Delivery Mechanism Transfer to Account is not supported by Financial Service Provider Test FSP (123): API']",
        ):
            form.clean()
