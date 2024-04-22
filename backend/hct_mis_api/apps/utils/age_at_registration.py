from typing import Optional, Union

from dateutil import parser
from dateutil.relativedelta import relativedelta

from hct_mis_api.apps.registration_data.models import (
    RegistrationDataImport,
    RegistrationDataImportDatahub,
)


def calculate_age_at_registration(
    rdi: Optional[Union[RegistrationDataImport, RegistrationDataImportDatahub]],
    birth_date: str,
) -> Optional[int]:
    try:
        return relativedelta(rdi.created_at.date(), parser.parse(birth_date).date()).years
    except Exception:
        return None
