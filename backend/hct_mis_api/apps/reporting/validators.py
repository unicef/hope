import logging
from typing import Dict, List

from django.core.exceptions import ValidationError

from hct_mis_api.apps.core.validators import CommonValidator
from hct_mis_api.apps.reporting.models import Report

logger = logging.getLogger(__name__)


class ReportValidator(CommonValidator):
    VALID_FILTERS: Dict[int, List[str]] = {
        Report.INDIVIDUALS: ["admin_area"],
        Report.HOUSEHOLD_DEMOGRAPHICS: ["admin_area"],
        Report.CASH_PLAN_VERIFICATION: ["program"],
        Report.PAYMENTS: ["admin_area"],
        Report.PAYMENT_VERIFICATION: ["program"],
        Report.CASH_PLAN: ["program"],
        Report.PROGRAM: [],
        Report.INDIVIDUALS_AND_PAYMENT: ["admin_area", "program"],
        Report.GRIEVANCES: [],
    }

    @classmethod
    def validate_report_type_filters(cls, *args, **kwargs):
        report_data = kwargs.get("report_data")
        report_type = report_data.get("report_type")
        if report_type not in dict(Report.REPORT_TYPES):
            logger.error("Wrong report type")
            raise ValidationError("Wrong report type")
        if "admin_area" not in ReportValidator.VALID_FILTERS[report_type]:
            report_data.pop("admin_area", None)
        if "program" not in ReportValidator.VALID_FILTERS[report_type]:
            report_data.pop("program", None)
