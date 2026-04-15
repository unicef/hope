from datetime import datetime

from dateutil import parser
from dateutil.relativedelta import relativedelta


def calculate_age_at_registration(
    created_at: datetime,
    birth_date: str,
) -> int | None:
    try:
        calculated_age_years = relativedelta(created_at.date(), parser.parse(birth_date).date()).years
        # return None if age is less then 0
        if calculated_age_years < 0:
            return None
        return calculated_age_years
    except ValueError:
        return None
