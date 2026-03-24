import zipfile
from unittest.mock import MagicMock

import pytest

from hope.apps.payment.xlsx.xlsx_payment_plan_export_per_fsp_service import XlsxPaymentPlanExportPerFspService

pytestmark = pytest.mark.django_db


@pytest.fixture
def mock_service():
    service = XlsxPaymentPlanExportPerFspService.__new__(XlsxPaymentPlanExportPerFspService)
    service.payment_plan = MagicMock()
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
