from typing import Any, Optional

from dateutil import parser
from dateutil.relativedelta import relativedelta


def calculate_age_at_registration(
    created_at: Any,
    birth_date: str,
) -> Optional[int]:
    try:
        return relativedelta(created_at.date(), parser.parse(birth_date).date()).years
    except Exception:
        return None
