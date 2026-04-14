from typing import Any

from hope.contrib.aurora.models import Registration
from hope.models import RegistrationDataImport


def create_task_for_processing_records(
    service: Any, registration: Registration, rdi: RegistrationDataImport | None, records_ids: list
) -> None:
    if celery_task := service.process_flex_records_async_task:
        celery_task(
            registration,
            rdi,
            records_ids,
        )
    else:
        raise NotImplementedError
