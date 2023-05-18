from typing import TYPE_CHECKING, Any, List

from strategy_field.utils import fqn

if TYPE_CHECKING:
    from uuid import UUID


def create_task_for_processing_records(service: Any, reg_id: "UUID", rdi_id: "UUID", records_ids: List) -> None:
    if celery_task := service.PROCESS_FLEX_RECORDS_TASK:
        celery_task.delay(reg_id, rdi_id, records_ids, fqn(service))
    else:
        raise NotImplementedError
