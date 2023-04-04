from typing import Any, Dict, List
from uuid import UUID

from hct_mis_api.apps.registration_datahub.services.sri_lanka_registration_service import (
    SriLankaRegistrationService,
)
from hct_mis_api.apps.registration_datahub.services.ukraine_registration_service import (
    UkraineRegistrationService,
)


def get_registration_to_rdi_service_map() -> Dict[int, Any]:
    return {
        2: UkraineRegistrationService,  # ukraine
        3: UkraineRegistrationService,  # ukraine
        17: SriLankaRegistrationService,  # sri lanka
        # 18: "czech republic",
        # 19: "czech republic",
    }


def create_task_for_processing_records(service: Any, rdi_id: "UUID", records_ids: List) -> None:
    if celery_task := service.PROCESS_FLEX_RECORDS_TASK:
        celery_task.delay(rdi_id, records_ids)
