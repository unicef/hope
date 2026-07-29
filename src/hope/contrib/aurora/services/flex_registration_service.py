from hope.contrib.aurora.models import Registration
from hope.models import RegistrationDataImport


def create_task_for_processing_records(
    service: object, registration: Registration, rdi: RegistrationDataImport, records_ids: list
) -> None:
    if celery_task := getattr(service, "process_flex_records_task", None):
        celery_task(
            registration,
            rdi,
            records_ids,
        )
    else:
        raise NotImplementedError
