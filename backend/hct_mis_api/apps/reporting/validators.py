import logging
from typing import Any

from django.core.exceptions import ValidationError

from hct_mis_api.apps.core.validators import BaseValidator
from hct_mis_api.apps.reporting.models import Report

logger = logging.getLogger(__name__)


class ReportValidator(BaseValidator):
    @classmethod
    def validate_report_type_filters(cls, *args: Any, **kwargs: Any) -> None:
        report_data = kwargs.get("report_data")
        report_type = report_data.get("report_type")
        if report_type not in dict(Report.REPORT_TYPES):
            logger.error("Wrong report type")
            raise ValidationError("Wrong report type")
