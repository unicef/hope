from io import BytesIO
from pathlib import Path

from django.conf import settings
from django.contrib.admin.options import get_content_type_for_model
from django.core.files import File

from hct_mis_api.apps.payment.utils import float_to_decimal
from hct_mis_api.apps.household.fixtures import create_household
from hct_mis_api.apps.household.models import Household
from hct_mis_api.apps.payment.xlsx.XlsxPaymentPlanImportService import XlsxPaymentPlanImportService
from hct_mis_api.apps.payment.models import PaymentPlan, ServiceProvider, PaymentChannel, Payment
from hct_mis_api.apps.payment.xlsx.XlsxPaymentPlanExportService import XlsxPaymentPlanExportService
from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.payment.fixtures import (
    ServiceProviderFactory,
    RealProgramFactory,
    PaymentPlanFactory,
    PaymentFactory
)
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.models import BusinessArea, FileTemp
from hct_mis_api.apps.core.fixtures import create_afghanistan


def valid_file():
    content = Path(f"{settings.PROJECT_ROOT}/apps/payment/tests/test_file/pp_payment_list_valid.xlsx").read_bytes()
    return File(BytesIO(content), name="pp_payment_list_valid.xlsx")


def invalid_file():
    content = Path(f"{settings.PROJECT_ROOT}/apps/payment/tests/test_file/pp_payment_list_invalid.xlsx").read_bytes()
    return File(BytesIO(content), name="pp_payment_list_invalid.xlsx")


class ImportExportPaymentPlanPaymentListTest(APITestCase):

    @classmethod
    def setUpTestData(cls):
        create_afghanistan()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")

        if not Household.objects.all().count():
            for n in range(1, 4):
                create_household(
                    {"size": n, "address": "Lorem Ipsum", "country_origin": "PL"},
                )

        if ServiceProvider.objects.count() < 3:
            ServiceProviderFactory.create_batch(3)
        program = RealProgramFactory()
        cls.payment_plan = PaymentPlanFactory(program=program, business_area=cls.business_area)
        program.households.set(Household.objects.all().values_list("id", flat=True))
        for household in program.households.all():
            PaymentFactory(payment_plan=cls.payment_plan, household=household, excluded=False)

        cls.user = UserFactory()
        cls.payment_plan = PaymentPlan.objects.all().last()

        # set Lock status
        cls.payment_plan.status_lock()
        cls.payment_plan.save()
        for p_ch in PaymentChannel.objects.all():
            p_ch.delivery_mechanism = "Deposit to Card"
            p_ch.save()

        cls.xlsx_valid_file = FileTemp.objects.create(
            object_id=cls.payment_plan.pk,
            content_type=get_content_type_for_model(cls.payment_plan),
            created_by=cls.user,
            file=valid_file(),
        ).file

        cls.xlsx_invalid_file = FileTemp.objects.create(
            object_id=cls.payment_plan.pk,
            content_type=get_content_type_for_model(cls.payment_plan),
            created_by=cls.user,
            file=invalid_file(),
        ).file

    def test_import_invalid_file(self):
        error_msg = [
            ('Payment Plan - Payment List', 'A2', 'This payment id 123123 is not in Payment Plan Payment List'),
            (
                'Payment Plan - Payment List',
                'F3',
                "Payment_channel should be one of ['Cardless cash withdrawal', 'Cash', 'Cash by FSP', 'Cheque', "
                "'Deposit to Card', 'In Kind', 'Mobile Money', 'Other', 'Pre-paid card', 'Referral', 'Transfer', "
                "'Transfer to Account', 'Voucher'] but received Invalid"
            ),
            (
                'Payment Plan - Payment List',
                'F3',
                "You can't set payment_channel Invalid for Payment with already assigned "
                "payment channel Deposit to Card"
            )
        ]
        service = XlsxPaymentPlanImportService(self.payment_plan, self.xlsx_invalid_file)
        wb = service.open_workbook()
        # override imported sheet payment id
        wb.active["A3"].value = str(self.payment_plan.all_active_payments[1].unicef_id)

        service.validate()
        self.assertEqual(service.errors, error_msg)

    def test_import_valid_file(self):
        all_active_payments = self.payment_plan.payments.exclude(excluded=True)
        # override imported payment id
        payment_id_1 = str(all_active_payments[0].unicef_id)
        payment_id_2 = str(all_active_payments[1].unicef_id)
        payment_1 = Payment.objects.get(unicef_id=payment_id_1)
        payment_2 = Payment.objects.get(unicef_id=payment_id_2)

        payment_2.assigned_payment_channel = None
        payment_2.save()

        service = XlsxPaymentPlanImportService(self.payment_plan, self.xlsx_valid_file)
        wb = service.open_workbook()

        wb.active["A2"].value = payment_id_1
        wb.active["A3"].value = payment_id_2
        wb.active["F2"].value = payment_1.assigned_payment_channel.delivery_mechanism
        wb.active["F3"].value = "Referral"

        service.validate()
        self.assertEqual(service.errors, [])

        service.import_payment_list()
        payment_1.refresh_from_db()
        payment_2.refresh_from_db()

        self.assertEqual(float_to_decimal(wb.active["I2"].value), payment_1.entitlement_quantity)
        self.assertEqual(float_to_decimal(wb.active["I3"].value), payment_2.entitlement_quantity)
        self.assertEqual("Referral", payment_2.assigned_payment_channel.delivery_mechanism)

    def test_export_payment_plan_payment_list(self):
        export_service = XlsxPaymentPlanExportService(self.payment_plan)
        export_service.save_xlsx_file(self.user)

        self.assertTrue(self.payment_plan.has_payment_list_xlsx_file)

        wb = export_service.generate_workbook()

        self.assertEqual(wb.active["A2"].value, str(self.payment_plan.all_active_payments[0].unicef_id))
        self.assertEqual(wb.active["I2"].value, self.payment_plan.all_active_payments[0].entitlement_quantity)
        self.assertEqual(wb.active["J2"].value, self.payment_plan.all_active_payments[0].entitlement_quantity_usd)
        self.assertEqual(
            wb.active["F2"].value, self.payment_plan.all_active_payments[0].assigned_payment_channel.delivery_mechanism
        )
