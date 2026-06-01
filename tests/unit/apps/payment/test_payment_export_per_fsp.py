from unittest.mock import MagicMock
import zipfile

import pytest

from hope.apps.payment.xlsx.xlsx_payment_plan_delivery_export_service import XlsxPaymentPlanDeliveryExportService

pytestmark = pytest.mark.django_db


@pytest.fixture
def mock_service():
    service = XlsxPaymentPlanDeliveryExportService.__new__(XlsxPaymentPlanDeliveryExportService)
    service.payment_plan = MagicMock()
    splits = service.payment_plan.splits.all.return_value.order_by.return_value
    splits.__iter__ = lambda self: iter([MagicMock()])
    splits.count.return_value = 1
    return service


def test_create_workbooks_per_split_raises_value_error_when_fsp_is_none(mock_service):
    mock_service.payment_plan.financial_service_provider = None
    mock_service.payment_plan.delivery_mechanism = MagicMock()

    zip_buf = MagicMock(spec=zipfile.ZipFile)

    with pytest.raises(ValueError, match="FSP must be set"):
        mock_service.create_workbooks_per_split(zip_file=zip_buf)


def test_create_workbooks_per_split_raises_value_error_when_delivery_mechanism_is_none(mock_service):
    mock_service.payment_plan.financial_service_provider = MagicMock()
    mock_service.payment_plan.delivery_mechanism = None

    zip_buf = MagicMock(spec=zipfile.ZipFile)

    with pytest.raises(ValueError, match="Delivery mechanism must be set"):
        mock_service.create_workbooks_per_split(zip_file=zip_buf)


def test_create_workbooks_per_split_raises_value_error_when_template_is_none(mock_service):
    mock_service.payment_plan.financial_service_provider = MagicMock()
    mock_service.payment_plan.delivery_mechanism = MagicMock()
    mock_service.open_workbook = MagicMock(return_value=(MagicMock(), MagicMock()))
    mock_service.get_template = MagicMock(return_value=None)

    with pytest.raises(ValueError, match="FSP XLSX template not found"):
        mock_service.create_workbooks_per_split(zip_file=MagicMock(spec=zipfile.ZipFile))
