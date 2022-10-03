import zipfile

from io import BytesIO
from pathlib import Path
from unittest.mock import patch

from django.conf import settings
from django.contrib.admin.options import get_content_type_for_model
from django.core.files import File

from hct_mis_api.apps.payment.utils import float_to_decimal
from hct_mis_api.apps.household.fixtures import create_household
from hct_mis_api.apps.household.models import Household, Individual
from hct_mis_api.apps.payment.xlsx.XlsxPaymentPlanImportService import XlsxPaymentPlanImportService
from hct_mis_api.apps.payment.models import (
    PaymentPlan,
    ServiceProvider,
    FinancialServiceProvider,
)
from hct_mis_api.apps.payment.xlsx.XlsxPaymentPlanExportService import XlsxPaymentPlanExportService
from hct_mis_api.apps.payment.xlsx.XlsxPaymentPlanExportPerFspService import XlsxPaymentPlanExportPerFspService
from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.payment.fixtures import (
    ServiceProviderFactory,
    RealProgramFactory,
    PaymentPlanFactory,
    PaymentFactory,
    PaymentChannelFactory,
)
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.models import BusinessArea, FileTemp
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.geo import models as geo_models


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
        country_origin = geo_models.Country.objects.filter(iso_code2="PL").first()

        if not Household.objects.all().count():
            for n in range(1, 4):
                create_household(
                    {"size": n, "address": "Lorem Ipsum", "country_origin": country_origin},
                )

        if ServiceProvider.objects.count() < 3:
            ServiceProviderFactory.create_batch(3)
        program = RealProgramFactory()
        cls.payment_plan = PaymentPlanFactory(program=program, business_area=cls.business_area)
        program.households.set(Household.objects.all().values_list("id", flat=True))
        for household in program.households.all():
            PaymentFactory(parent=cls.payment_plan, household=household, excluded=False, assigned_payment_channel=None)

        cls.user = UserFactory()
        cls.payment_plan = PaymentPlan.objects.all().last()

        # set Lock status
        cls.payment_plan.status_lock()
        cls.payment_plan.save()
        for ind in Individual.objects.all():
            PaymentChannelFactory(individual=ind, delivery_mechanism="Deposit to Card")

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
        self.maxDiff = None
        error_msg = [
            ("Payment Plan - Payment List", "A2", "This payment id 123123 is not in Payment Plan Payment List"),
            (
                "Payment Plan - Payment List",
                "F3",
                "Payment_channel should be one of ['Cardless cash withdrawal', 'Cash', 'Cash by FSP', 'Cheque', "
                "'Deposit to Card', 'In Kind', 'Mobile Money', 'Other', 'Pre-paid card', 'Referral', 'Transfer', "
                "'Transfer to Account', 'Voucher'] but received Invalid",
            ),
            (
                "Payment Plan - Payment List",
                "F3",
                "You can't set payment_channel Invalid for Collector with already assigned "
                "payment channel(s): Deposit to Card",
            ),
        ]
        service = XlsxPaymentPlanImportService(self.payment_plan, self.xlsx_invalid_file)
        wb = service.open_workbook()
        # override imported sheet payment id
        wb.active["A3"].value = str(self.payment_plan.not_excluded_payments[1].unicef_id)

        service.validate()
        self.assertEqual(service.errors, error_msg)

    def test_import_valid_file(self):
        self.maxDiff = None
        not_excluded_payments = self.payment_plan.not_excluded_payments.all()
        # override imported payment id
        payment_id_1 = str(not_excluded_payments[0].unicef_id)
        payment_id_2 = str(not_excluded_payments[1].unicef_id)
        payment_1 = not_excluded_payments[0]
        payment_2 = not_excluded_payments[1]
        payment_2.collector.payment_channels.all().delete()

        service = XlsxPaymentPlanImportService(self.payment_plan, self.xlsx_valid_file)
        wb = service.open_workbook()

        payment_1_payment_channels = ", ".join(
            list(
                payment_1.collector.payment_channels.all()
                .distinct("delivery_mechanism")
                .values_list("delivery_mechanism", flat=True)
            )
        )
        wb.active["A2"].value = payment_id_1
        wb.active["A3"].value = payment_id_2
        wb.active["F2"].value = payment_1_payment_channels
        wb.active["F3"].value = "Referral"

        service.validate()
        self.assertEqual(service.errors, [])

        with patch("hct_mis_api.apps.core.exchange_rates.api.ExchangeRateAPI.fetch_exchange_rates") as mock:
            mock.return_value = {}
            service.import_payment_list()
        payment_1.refresh_from_db()
        payment_2.refresh_from_db()

        self.assertEqual(float_to_decimal(wb.active["I2"].value), payment_1.entitlement_quantity)
        self.assertEqual(float_to_decimal(wb.active["I3"].value), payment_2.entitlement_quantity)
        self.assertEqual("Referral", payment_2.collector.payment_channels.first().delivery_mechanism)

    def test_export_payment_plan_payment_list(self):
        export_service = XlsxPaymentPlanExportService(self.payment_plan)
        export_service.save_xlsx_file(self.user)

        self.assertTrue(self.payment_plan.has_export_file)

        wb = export_service.generate_workbook()
        payment = self.payment_plan.not_excluded_payments.order_by("unicef_id").first()
        self.assertEqual(wb.active["A2"].value, str(payment.unicef_id))
        self.assertEqual(wb.active["I2"].value, payment.entitlement_quantity)
        self.assertEqual(wb.active["J2"].value, payment.entitlement_quantity_usd)
        self.assertEqual(wb.active["F2"].value, "")

    def test_export_payment_plan_payment_list_per_fsp(self):
        # add assigned_payment_channel
        for p in self.payment_plan.not_excluded_payments.all():
            p.assigned_payment_channel = p.collector.payment_channels.first()
            p.save()

        export_service = XlsxPaymentPlanExportPerFspService(self.payment_plan)
        export_service.export_per_fsp(self.user)

        self.assertTrue(self.payment_plan.has_export_file)
        self.assertIsNotNone(self.payment_plan.payment_list_export_file_link)
        self.assertTrue(
            self.payment_plan.export_file.file.name.startswith(
                f"payment_plan_payment_list_{self.payment_plan.unicef_id}"
            )
        )
        fsp_ids = export_service.payment_list.values_list("financial_service_provider_id", flat=True)
        with zipfile.ZipFile(self.payment_plan.export_file.file, mode="r") as zip_file:
            file_list = zip_file.namelist()
            self.assertEqual(len(fsp_ids), len(file_list))
            fsp_names = FinancialServiceProvider.objects.filter(id__in=fsp_ids).values_list("name", flat=True)
            file_list_fsp = [
                f.replace(".xlsx", "").replace(f"payment_plan_payment_list_{self.payment_plan.unicef_id}_FSP_", "")
                for f in file_list
            ]
            for fsp_name in fsp_names:
                self.assertIn(fsp_name, file_list_fsp)
