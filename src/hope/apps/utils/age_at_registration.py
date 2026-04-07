from datetime import datetime

from dateutil import parser
from dateutil.relativedelta import relativedelta


def calculate_age_at_registration(
    created_at: datetime,
    birth_date: str,
) -> int | None:
    try:
        birth_date_parsed = parser.parse(birth_date).date()
        created_at_date = created_at.date()
        # return None if B_Day is future date
        if birth_date_parsed > created_at_date:
            return None
        return relativedelta(created_at_date, birth_date_parsed).years
    except ValueError:
        return None
