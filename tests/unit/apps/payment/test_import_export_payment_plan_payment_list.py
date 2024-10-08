import zipfile
from io import BytesIO
from pathlib import Path
from typing import Any
from unittest import mock
from unittest.mock import patch

from django.conf import settings
from django.contrib.admin.options import get_content_type_for_model
from django.core.files import File
from django.test import TestCase
from django.urls import reverse

from graphql import GraphQLError

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.models import Role, User, UserRole
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import (
    BusinessArea,
    DataCollectingType,
    FileTemp,
    FlexibleAttribute,
)
from hct_mis_api.apps.geo import models as geo_models
from hct_mis_api.apps.household.fixtures import (
    BankAccountInfoFactory,
    DocumentFactory,
    create_household,
)
from hct_mis_api.apps.household.models import (
    IDENTIFICATION_TYPE_NATIONAL_ID,
    ROLE_PRIMARY,
    Document,
    Household,
    IndividualRoleInHousehold,
)
from hct_mis_api.apps.payment.delivery_mechanisms import DeliveryMechanismChoices
from hct_mis_api.apps.payment.fixtures import (
    DeliveryMechanismPerPaymentPlanFactory,
    FinancialServiceProviderFactory,
    FinancialServiceProviderXlsxTemplateFactory,
    FspXlsxTemplatePerDeliveryMechanismFactory,
    PaymentFactory,
    PaymentPlanFactory,
    RealProgramFactory,
    ServiceProviderFactory,
    generate_delivery_mechanisms,
)
from hct_mis_api.apps.payment.models import (
    DeliveryMechanism,
    FinancialServiceProvider,
    FinancialServiceProviderXlsxTemplate,
    FspXlsxTemplatePerDeliveryMechanism,
    PaymentHouseholdSnapshot,
    PaymentPlan,
    PaymentPlanSplit,
    ServiceProvider,
)
from hct_mis_api.apps.payment.services.payment_household_snapshot_service import (
    create_payment_plan_snapshot_data,
)
from hct_mis_api.apps.payment.services.payment_plan_services import PaymentPlanService
from hct_mis_api.apps.payment.utils import to_decimal
from hct_mis_api.apps.payment.xlsx.xlsx_error import XlsxError
from hct_mis_api.apps.payment.xlsx.xlsx_payment_plan_export_per_fsp_service import (
    XlsxPaymentPlanExportPerFspService,
)
from hct_mis_api.apps.payment.xlsx.xlsx_payment_plan_export_service import (
    XlsxPaymentPlanExportService,
)
from hct_mis_api.apps.payment.xlsx.xlsx_payment_plan_import_service import (
    XlsxPaymentPlanImportService,
)
from hct_mis_api.apps.program.fixtures import ProgramFactory


def valid_file() -> File:
    content = Path(f"{settings.TESTS_ROOT}/apps/payment/test_file/pp_payment_list_valid.xlsx").read_bytes()
    return File(BytesIO(content), name="pp_payment_list_valid.xlsx")


def invalid_file() -> File:
    content = Path(f"{settings.TESTS_ROOT}/apps/payment/test_file/pp_payment_list_invalid.xlsx").read_bytes()
    return File(BytesIO(content), name="pp_payment_list_invalid.xlsx")


class ImportExportPaymentPlanPaymentListTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        generate_delivery_mechanisms()
        create_afghanistan()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")
        country_origin = geo_models.Country.objects.filter(iso_code2="PL").first()

        if not Household.objects.all().count():
            for n in range(1, 4):
                create_household(
                    {"size": n, "address": "Lorem Ipsum", "country_origin": country_origin, "village": "TEST_VILLAGE"},
                )

        if ServiceProvider.objects.count() < 3:
            ServiceProviderFactory.create_batch(3)
        program = RealProgramFactory()
        cls.dm_cash = DeliveryMechanism.objects.get(code="cash")
        cls.dm_transfer = DeliveryMechanism.objects.get(code="transfer")
        cls.dm_atm_card = DeliveryMechanism.objects.get(code="atm_card")
        cls.payment_plan = PaymentPlanFactory(program=program, business_area=cls.business_area)
        cls.fsp_1 = FinancialServiceProviderFactory(
            name="Test FSP 1",
            communication_channel=FinancialServiceProvider.COMMUNICATION_CHANNEL_XLSX,
            vision_vendor_number=123456789,
        )
        cls.fsp_1.delivery_mechanisms.add(cls.dm_cash)
        FspXlsxTemplatePerDeliveryMechanismFactory(financial_service_provider=cls.fsp_1, delivery_mechanism=cls.dm_cash)
        DeliveryMechanismPerPaymentPlanFactory(
            payment_plan=cls.payment_plan,
            financial_service_provider=cls.fsp_1,
            delivery_mechanism=cls.dm_cash,
            delivery_mechanism_order=1,
        )
        program.households.set(Household.objects.all().values_list("id", flat=True))
        for household in program.households.all():
            PaymentFactory(
                parent=cls.payment_plan, household=household, financial_service_provider=cls.fsp_1, currency="PLN"
            )

        cls.user = UserFactory()
        cls.payment_plan = PaymentPlan.objects.all()[0]

        # set Lock status
        cls.payment_plan.status_lock()
        cls.payment_plan.save()

        create_payment_plan_snapshot_data(cls.payment_plan)

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

    def test_import_invalid_file(self) -> None:
        error_msg = [
            XlsxError(
                "Payment Plan - Payment List", "A2", "This payment id 123123 is not in Payment Plan Payment List"
            ),
        ]
        service = XlsxPaymentPlanImportService(self.payment_plan, self.xlsx_invalid_file)
        wb = service.open_workbook()
        # override imported sheet payment id
        wb.active["A3"].value = str(self.payment_plan.eligible_payments[1].unicef_id)

        service.validate()
        self.assertEqual(service.errors, error_msg)

    def test_import_invalid_file_with_unexpected_column(self) -> None:
        error_msg = XlsxError(sheet="Payment Plan - Payment List", coordinates="N3", message="Unexpected value")
        content = Path(
            f"{settings.TESTS_ROOT}/apps/payment/test_file/pp_payment_list_unexpected_column.xlsx"
        ).read_bytes()
        file = BytesIO(content)

        service = XlsxPaymentPlanImportService(self.payment_plan, file)
        service.open_workbook()
        service.validate()
        self.assertIn(error_msg, service.errors)

    @patch("hct_mis_api.apps.core.exchange_rates.api.ExchangeRateClientAPI.__init__")
    def test_import_valid_file(self, mock_parent_init: Any) -> None:
        mock_parent_init.return_value = None
        not_excluded_payments = self.payment_plan.eligible_payments.all()
        # override imported payment id
        payment_id_1 = str(not_excluded_payments[0].unicef_id)
        payment_id_2 = str(not_excluded_payments[1].unicef_id)
        payment_1 = not_excluded_payments[0]
        payment_2 = not_excluded_payments[1]

        service = XlsxPaymentPlanImportService(self.payment_plan, self.xlsx_valid_file)
        wb = service.open_workbook()

        wb.active["A2"].value = payment_id_1
        wb.active["A3"].value = payment_id_2

        service.validate()
        self.assertEqual(service.errors, [])

        with patch("hct_mis_api.apps.core.exchange_rates.api.ExchangeRateClientAPI.fetch_exchange_rates") as mock:
            mock.return_value = {}
            service.import_payment_list()
        payment_1.refresh_from_db()
        payment_2.refresh_from_db()

        self.assertEqual(to_decimal(wb.active["J2"].value), payment_1.entitlement_quantity)
        self.assertEqual(to_decimal(wb.active["J3"].value), payment_2.entitlement_quantity)

    def test_export_payment_plan_payment_list(self) -> None:
        payment = self.payment_plan.eligible_payments.order_by("unicef_id").first()
        # add national_id
        DocumentFactory(
            status=Document.STATUS_VALID,
            program=self.payment_plan.program,
            type__key=IDENTIFICATION_TYPE_NATIONAL_ID.lower(),
            document_number="Test_Number_National_Id_123",
            individual=payment.collector,
        )
        # remove old and create new snapshot with national_id document
        PaymentHouseholdSnapshot.objects.all().delete()
        self.assertEqual(payment.collector.documents.all().count(), 1)
        create_payment_plan_snapshot_data(self.payment_plan)
        export_service = XlsxPaymentPlanExportService(self.payment_plan)
        export_service.save_xlsx_file(self.user)

        self.assertTrue(self.payment_plan.has_export_file)

        wb = export_service.generate_workbook()

        self.assertEqual(wb.active["A2"].value, str(payment.unicef_id))
        self.assertEqual(wb.active["J2"].value, payment.entitlement_quantity)
        self.assertEqual(wb.active["K2"].value, payment.entitlement_quantity_usd)
        self.assertEqual(wb.active["E2"].value, "TEST_VILLAGE")
        self.assertEqual(wb.active["M1"].value, "national_id")
        self.assertEqual(wb.active["M2"].value, "Test_Number_National_Id_123")

    def test_export_payment_plan_payment_list_per_fsp(self) -> None:
        financial_service_provider1 = FinancialServiceProviderFactory()
        financial_service_provider1.delivery_mechanisms.add(self.dm_cash)
        FspXlsxTemplatePerDeliveryMechanismFactory(
            financial_service_provider=financial_service_provider1,
            delivery_mechanism=self.dm_cash,
        )
        financial_service_provider2 = FinancialServiceProviderFactory()
        financial_service_provider2.delivery_mechanisms.add(self.dm_transfer)
        FspXlsxTemplatePerDeliveryMechanismFactory(
            financial_service_provider=financial_service_provider2,
            delivery_mechanism=self.dm_transfer,
        )

        DeliveryMechanismPerPaymentPlanFactory(
            payment_plan=self.payment_plan,
            delivery_mechanism=self.dm_cash,
            financial_service_provider=financial_service_provider1,
            delivery_mechanism_order=2,
        )

        DeliveryMechanismPerPaymentPlanFactory(
            payment_plan=self.payment_plan,
            delivery_mechanism=self.dm_transfer,
            financial_service_provider=financial_service_provider2,
            delivery_mechanism_order=3,
        )
        self.payment_plan.status = PaymentPlan.Status.ACCEPTED
        self.payment_plan.save()

        payment = self.payment_plan.eligible_payments.first()
        self.assertEqual(payment.token_number, None)
        self.assertEqual(payment.order_number, None)

        export_service = XlsxPaymentPlanExportPerFspService(self.payment_plan)
        export_service.export_per_fsp(self.user)

        payment.refresh_from_db(fields=["token_number", "order_number"])
        self.assertEqual(len(str(payment.token_number)), 7)
        self.assertEqual(len(str(payment.order_number)), 9)

        self.assertTrue(self.payment_plan.has_export_file)
        self.assertIsNotNone(self.payment_plan.payment_list_export_file_link)
        self.assertTrue(
            self.payment_plan.export_file_per_fsp.file.name.startswith(
                f"payment_plan_payment_list_{self.payment_plan.unicef_id}"
            )
        )
        fsp_ids = self.payment_plan.delivery_mechanisms.values_list("financial_service_provider_id", flat=True)
        with zipfile.ZipFile(self.payment_plan.export_file_per_fsp.file, mode="r") as zip_file:  # type: ignore
            file_list = zip_file.namelist()
            self.assertEqual(len(fsp_ids), len(file_list))
            fsp_xlsx_template_per_delivery_mechanism_list = FspXlsxTemplatePerDeliveryMechanism.objects.filter(
                financial_service_provider_id__in=fsp_ids,
            )
            file_list_fsp = [
                f.replace(".xlsx", "").replace(f"payment_plan_payment_list_{self.payment_plan.unicef_id}_FSP_", "")
                for f in file_list
            ]
            for fsp_xlsx_template_per_delivery_mechanism in fsp_xlsx_template_per_delivery_mechanism_list:
                self.assertIn(
                    f"{fsp_xlsx_template_per_delivery_mechanism.financial_service_provider.name}_{fsp_xlsx_template_per_delivery_mechanism.delivery_mechanism}",
                    file_list_fsp,
                )

    @patch("hct_mis_api.apps.payment.models.PaymentPlanSplit.MIN_NO_OF_PAYMENTS_IN_CHUNK")
    def test_export_payment_plan_payment_list_per_split(self, min_no_of_payments_in_chunk_mock: Any) -> None:
        min_no_of_payments_in_chunk_mock.__get__ = mock.Mock(return_value=2)

        financial_service_provider1 = FinancialServiceProviderFactory()
        financial_service_provider1.delivery_mechanisms.add(self.dm_cash)
        FspXlsxTemplatePerDeliveryMechanismFactory(
            financial_service_provider=financial_service_provider1,
            delivery_mechanism=self.dm_cash,
        )
        DeliveryMechanismPerPaymentPlanFactory(
            payment_plan=self.payment_plan,
            delivery_mechanism=self.dm_cash,
            financial_service_provider=financial_service_provider1,
            delivery_mechanism_order=2,
        )

        self.payment_plan.status = PaymentPlan.Status.ACCEPTED
        self.payment_plan.save()

        payments = self.payment_plan.eligible_payments.all()
        self.assertEqual(payments.count(), 3)

        pp_service = PaymentPlanService(self.payment_plan)
        pp_service.split(PaymentPlanSplit.SplitType.BY_RECORDS, 2)

        export_service = XlsxPaymentPlanExportPerFspService(self.payment_plan)
        export_service.export_per_fsp(self.user)

        self.assertTrue(self.payment_plan.has_export_file)
        self.assertIsNotNone(self.payment_plan.payment_list_export_file_link)
        self.assertTrue(
            self.payment_plan.export_file_per_fsp.file.name.startswith(
                f"payment_plan_payment_list_{self.payment_plan.unicef_id}"
            )
        )
        splits_count = self.payment_plan.splits.count()
        self.assertEqual(splits_count, 2)
        with zipfile.ZipFile(self.payment_plan.export_file_per_fsp.file, mode="r") as zip_file:  # type: ignore
            file_list = zip_file.namelist()
            self.assertEqual(splits_count, len(file_list))

        # reexport
        pp_service.split(PaymentPlanSplit.SplitType.BY_COLLECTOR)

        export_service = XlsxPaymentPlanExportPerFspService(self.payment_plan)
        export_service.export_per_fsp(self.user)
        self.payment_plan.refresh_from_db()
        self.assertTrue(self.payment_plan.has_export_file)
        self.assertIsNotNone(self.payment_plan.payment_list_export_file_link)
        self.assertTrue(
            self.payment_plan.export_file_per_fsp.file.name.startswith(
                f"payment_plan_payment_list_{self.payment_plan.unicef_id}"
            )
        )
        splits_count = self.payment_plan.splits.count()
        self.assertEqual(splits_count, 3)
        with zipfile.ZipFile(self.payment_plan.export_file_per_fsp.file, mode="r") as zip_file:  # type: ignore
            file_list = zip_file.namelist()
            self.assertEqual(splits_count, len(file_list))

    def test_payment_row_bank_information(self) -> None:
        core_fields = [
            "account_holder_name",
            "bank_branch_name",
            "bank_name",
            "bank_account_number",
            "debit_card_number",
        ]
        export_service = XlsxPaymentPlanExportPerFspService(self.payment_plan)
        fsp_xlsx_template = FinancialServiceProviderXlsxTemplateFactory(core_fields=core_fields)
        headers = export_service.prepare_headers(fsp_xlsx_template)
        household, _ = create_household({"size": 1})
        primary = IndividualRoleInHousehold.objects.filter(role=ROLE_PRIMARY, household=household).first().individual
        BankAccountInfoFactory(
            individual=primary,
            account_holder_name="Kowalski",
            bank_branch_name="BranchJPMorgan",
            bank_name="JPMorgan",
            bank_account_number="362277220020615398848112903",
            debit_card_number="123",
        )
        payment = PaymentFactory(parent=self.payment_plan, household=household, collector=primary)
        # remove old and create new snapshot with bank account info
        PaymentHouseholdSnapshot.objects.all().delete()
        create_payment_plan_snapshot_data(self.payment_plan)

        account_holder_name_index = headers.index("account_holder_name")
        bank_branch_name_index = headers.index("bank_branch_name")
        bank_name_index = headers.index("bank_name")
        bank_account_number_index = headers.index("bank_account_number")
        debit_card_number_index = headers.index("debit_card_number")

        payment_row = export_service.get_payment_row(payment, fsp_xlsx_template)

        self.assertEqual(payment_row[account_holder_name_index], "Kowalski")
        self.assertEqual(payment_row[bank_branch_name_index], "BranchJPMorgan")
        self.assertEqual(payment_row[bank_name_index], "JPMorgan")
        self.assertEqual(payment_row[bank_account_number_index], "362277220020615398848112903")
        self.assertEqual(payment_row[debit_card_number_index], "123")

    def test_payment_row_flex_fields(self) -> None:
        core_fields = [
            "account_holder_name",
        ]
        decimal_flexible_attribute = FlexibleAttribute(
            type=FlexibleAttribute.DECIMAL,
            name="flex_decimal_i_f",
            associated_with=FlexibleAttribute.ASSOCIATED_WITH_INDIVIDUAL,
        )
        decimal_flexible_attribute.save()
        date_flexible_attribute = FlexibleAttribute(
            type=FlexibleAttribute.DECIMAL,
            name="flex_date_i_f",
            associated_with=FlexibleAttribute.ASSOCIATED_WITH_HOUSEHOLD,
        )
        date_flexible_attribute.save()
        flex_fields = [
            decimal_flexible_attribute.name,
            date_flexible_attribute.name,
        ]

        export_service = XlsxPaymentPlanExportPerFspService(self.payment_plan)
        fsp_xlsx_template = FinancialServiceProviderXlsxTemplateFactory(
            core_fields=core_fields, flex_fields=flex_fields
        )
        headers = export_service.prepare_headers(fsp_xlsx_template)
        household, _ = create_household({"size": 1})
        individual = household.primary_collector
        individual.flex_fields = {
            decimal_flexible_attribute.name: 123.45,
        }
        individual.save()
        household.flex_fields = {
            date_flexible_attribute.name: "2021-01-01",
        }
        household.save()
        payment = PaymentFactory(parent=self.payment_plan, household=household, collector=individual)
        decimal_flexible_attribute_index = headers.index(decimal_flexible_attribute.name)
        date_flexible_attribute_index = headers.index(date_flexible_attribute.name)

        # remove old and create new snapshot
        PaymentHouseholdSnapshot.objects.all().delete()
        create_payment_plan_snapshot_data(self.payment_plan)

        payment_row = export_service.get_payment_row(payment, fsp_xlsx_template)
        self.assertEqual(payment_row[decimal_flexible_attribute_index], 123.45)
        self.assertEqual(payment_row[date_flexible_attribute_index], "2021-01-01")

    def test_export_per_fsp_if_no_fsp_assigned_to_payment_plan(self) -> None:
        self.payment_plan.status = PaymentPlan.Status.ACCEPTED
        self.payment_plan.save()
        self.payment_plan.delivery_mechanisms.all().delete()

        self.assertEqual(self.payment_plan.delivery_mechanisms.count(), 0)

        export_service = XlsxPaymentPlanExportPerFspService(self.payment_plan)
        with self.assertRaises(GraphQLError) as e:
            export_service.export_per_fsp(self.user)
        self.assertEqual(
            e.exception.message,
            f"Not possible to generate export file. "
            f"There aren't any FSP(s) assigned to Payment Plan {self.payment_plan.unicef_id}.",
        )

        DeliveryMechanismPerPaymentPlanFactory(
            payment_plan=self.payment_plan,
            financial_service_provider=self.fsp_1,
            delivery_mechanism=self.dm_cash,
            delivery_mechanism_order=1,
        )
        # set generate_token_and_order_numbers to False
        export_service.payment_generate_token_and_order_numbers = False
        export_service.export_per_fsp(self.user)
        self.payment_plan.refresh_from_db()
        self.assertTrue(self.payment_plan.has_export_file)
        self.assertIsNotNone(self.payment_plan.payment_list_export_file_link)

    def test_export_payment_plan_per_fsp_with_people_program(self) -> None:
        # check with default program
        self.payment_plan.status = PaymentPlan.Status.ACCEPTED
        self.payment_plan.save()
        export_service = XlsxPaymentPlanExportPerFspService(self.payment_plan)
        export_service.export_per_fsp(self.user)
        self.assertFalse(self.payment_plan.program.is_social_worker_program)

        delivery_mechanism_per_payment_plan = self.payment_plan.delivery_mechanisms.first()
        fsp = delivery_mechanism_per_payment_plan.financial_service_provider
        _, ws_fsp = export_service.open_workbook(fsp.name)
        fsp_xlsx_template = export_service.get_template(fsp, delivery_mechanism_per_payment_plan.delivery_mechanism)
        template_column_list = export_service.prepare_headers(fsp_xlsx_template)
        self.assertEqual(
            len(template_column_list),
            len(FinancialServiceProviderXlsxTemplate.DEFAULT_COLUMNS) - 1,
            template_column_list,
        )  # - ind_id
        self.assertIn("household_id", template_column_list)
        self.assertIn("household_size", template_column_list)
        self.assertNotIn("individual_id", template_column_list)

        # create Program for People export
        program_sw = ProgramFactory(data_collecting_type__type=DataCollectingType.Type.SOCIAL)
        self.payment_plan.program = program_sw
        self.payment_plan.save()

        export_service = XlsxPaymentPlanExportPerFspService(self.payment_plan)
        export_service.export_per_fsp(self.user)

        self.payment_plan.refresh_from_db()
        self.assertTrue(self.payment_plan.has_export_file)
        self.assertTrue(self.payment_plan.program.is_social_worker_program)

        # add core fields
        fsp_xlsx_template.core_fields = ["age", "zip_code", "household_unicef_id", "individual_unicef_id"]
        fsp_xlsx_template.columns = fsp_xlsx_template.DEFAULT_COLUMNS
        fsp_xlsx_template.save()
        fsp_xlsx_template.refresh_from_db()

        _, ws_fsp = export_service.open_workbook(fsp.name)
        fsp_xlsx_template = export_service.get_template(fsp, delivery_mechanism_per_payment_plan.delivery_mechanism)

        template_column_list = export_service.prepare_headers(fsp_xlsx_template)
        fsp_xlsx_template.refresh_from_db()
        # remove for people 'household_unicef_id' core_field
        self.assertEqual(len(template_column_list), 29)  # DEFAULT_COLUMNS -hh_id and -hh_size +ind_id +3 core fields
        self.assertNotIn("household_id", template_column_list)
        self.assertNotIn("household_size", template_column_list)
        self.assertIn("individual_id", template_column_list)
        # check core fields
        self.assertListEqual(
            fsp_xlsx_template.core_fields, ["age", "zip_code", "household_unicef_id", "individual_unicef_id"]
        )
        self.assertIn("age", template_column_list)
        self.assertIn("zip_code", template_column_list)
        self.assertNotIn("household_unicef_id", template_column_list)
        self.assertIn("individual_unicef_id", template_column_list)

        # get_template error
        self.assertEqual(
            FspXlsxTemplatePerDeliveryMechanism.objects.filter(
                delivery_mechanism=self.dm_atm_card,
                financial_service_provider=self.fsp_1,
            ).count(),
            0,
        )
        export_service = XlsxPaymentPlanExportPerFspService(self.payment_plan)
        with self.assertRaises(GraphQLError) as e:
            export_service.get_template(self.fsp_1, self.dm_atm_card)
        self.assertEqual(
            e.exception.message,
            f"Not possible to generate export file. There isn't any FSP XLSX Template assigned to Payment "
            f"Plan {self.payment_plan.unicef_id} for FSP {self.fsp_1.name} and delivery "
            f"mechanism {DeliveryMechanismChoices.DELIVERY_TYPE_ATM_CARD}.",
        )

    def test_flex_fields_admin_visibility(self) -> None:
        user = User.objects.create_superuser(username="admin", password="password", email="admin@example.com")
        permission_list = [Permissions.PM_ADMIN_FINANCIAL_SERVICE_PROVIDER_UPDATE.name]
        role, created = Role.objects.update_or_create(name="LOL", defaults={"permissions": permission_list})
        user_role, _ = UserRole.objects.get_or_create(user=user, role=role, business_area=self.business_area)
        decimal_flexible_attribute = FlexibleAttribute(
            type=FlexibleAttribute.DECIMAL,
            name="flex_decimal_i_f",
            associated_with=FlexibleAttribute.ASSOCIATED_WITH_INDIVIDUAL,
        )
        decimal_flexible_attribute.save()
        date_flexible_attribute = FlexibleAttribute(
            type=FlexibleAttribute.DECIMAL,
            name="flex_date_i_f",
            associated_with=FlexibleAttribute.ASSOCIATED_WITH_INDIVIDUAL,
        )
        date_flexible_attribute.save()
        self.client.login(username="admin", password="password")
        instance = FinancialServiceProviderXlsxTemplate(flex_fields=[], name="Test FSP XLSX Template")
        instance.save()
        url = reverse("admin:payment_financialserviceproviderxlsxtemplate_change", args=[instance.pk])
        response: Any = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("flex_fields", response.context["adminform"].form.fields)
        self.assertIn(
            "flex_decimal_i_f",
            (name for name, _ in response.context["adminform"].form.fields["flex_fields"].choices),
        )
        self.assertIn(
            "flex_date_i_f",
            (name for name, _ in response.context["adminform"].form.fields["flex_fields"].choices),
        )

    def test_payment_row_get_flex_field_if_no_snapshot_data(self) -> None:
        flex_field = FlexibleAttribute(
            type=FlexibleAttribute.DECIMAL,
            name="flex_decimal_i_f",
            associated_with=FlexibleAttribute.ASSOCIATED_WITH_INDIVIDUAL,
        )
        flex_field.save()
        fsp_xlsx_template = FinancialServiceProviderXlsxTemplateFactory(flex_fields=[flex_field.name])
        export_service = XlsxPaymentPlanExportPerFspService(self.payment_plan)
        payment = PaymentFactory(parent=self.payment_plan)
        empty_payment_row = export_service.get_payment_row(payment, fsp_xlsx_template)
        for value in empty_payment_row:
            self.assertEqual(value, "")
