from typing import Any

from dateutil import parser
from dateutil.relativedelta import relativedelta


def calculate_age_at_registration(
    created_at: Any,
    birth_date: str,
) -> int | None:
    try:
        return relativedelta(created_at.date(), parser.parse(birth_date).date()).years
    except ValueError:
        return None
