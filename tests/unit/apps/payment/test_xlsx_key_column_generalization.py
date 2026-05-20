from hope.apps.payment.xlsx.xlsx_payment_plan_base_service import XlsxPaymentPlanBaseService
from hope.apps.payment.xlsx.xlsx_payment_plan_export_service import XlsxPaymentPlanExportService
from hope.apps.payment.xlsx.xlsx_payment_plan_import_service import XlsxPaymentPlanImportService
from hope.apps.payment.xlsx.xlsx_top_up_template_export_service import XlsxTopUpTemplateExportService


def test_base_service_arrange_default_act_inspect_assert_key_column_is_payment_id():
    assert XlsxPaymentPlanBaseService.KEY_COLUMN == "payment_id"


def test_payment_plan_export_service_arrange_default_act_inspect_assert_key_column_unchanged():
    assert XlsxPaymentPlanExportService.KEY_COLUMN == "payment_id"


def test_payment_plan_import_service_arrange_default_act_inspect_assert_key_column_unchanged():
    assert XlsxPaymentPlanImportService.KEY_COLUMN == "payment_id"


def test_payment_plan_export_service_arrange_default_act_inspect_assert_headers_start_with_payment_id():
    assert XlsxPaymentPlanExportService.HEADERS[0] == "payment_id"


def test_top_up_template_service_arrange_override_act_inspect_assert_key_column_is_household_unicef_id():
    assert XlsxTopUpTemplateExportService.KEY_COLUMN == "household_unicef_id"


def test_top_up_template_service_arrange_override_act_inspect_assert_headers_start_with_household_unicef_id():
    assert XlsxTopUpTemplateExportService.HEADERS[0] == "household_unicef_id"


def test_top_up_template_service_arrange_override_act_inspect_assert_payment_id_not_in_headers():
    assert "payment_id" not in XlsxTopUpTemplateExportService.HEADERS
