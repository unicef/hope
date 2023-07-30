from typing import Dict, Optional, Union

from dateutil import parser
from dateutil.relativedelta import relativedelta

from hct_mis_api.apps.registration_data.models import RegistrationDataImport
from hct_mis_api.apps.registration_datahub.models import (
    DiiaIndividual,
    ImportedIndividual,
    RegistrationDataImportDatahub,
)


def calculate_age_at_registration(
    rdi: Optional[Union[RegistrationDataImport, RegistrationDataImportDatahub, DiiaIndividual]],
    individual_data: Union[ImportedIndividual, Dict],
) -> Optional[int]:
    if isinstance(individual_data, (ImportedIndividual, DiiaIndividual)):
        birth_date = individual_data.birth_date
    else:
        birth_date = individual_data.get("birth_date")

    try:
        return relativedelta(rdi.created_at.date(), parser.parse(birth_date).date()).years
    except Exception:
        return None
