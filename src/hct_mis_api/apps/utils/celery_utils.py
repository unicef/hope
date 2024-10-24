from typing import Any, Optional


class CeleryConnectionException(Exception):
    pass


def is_celery_working(celery_app: Any) -> bool:
    return bool(celery_app.control.ping())


def format_task(task: dict, status: str) -> dict:
    if "request" in task:
        task = task["request"]
    return {
        "id": task["id"],
        "name": task["name"],
        "args": task["args"],
        "kwargs": task["kwargs"],
        "status": status,
    }


def format_tasks(tasks_dict: dict, status: str) -> list:
    for tasks_list in tasks_dict.values():
        for task in tasks_list:
            yield format_task(task, status)


def get_worker_tasks(
    celery_app: Any,
) -> list:
    all_tasks = []
    try:
        i = celery_app.control.inspect()
        all_tasks.extend(format_tasks(i.active(), "active"))
        all_tasks.extend(format_tasks(i.reserved(), "queued"))
        all_tasks.extend(format_tasks(i.scheduled(), "queued"))
        return all_tasks
    except (ValueError, AttributeError):
        return get_worker_tasks(celery_app)


def get_all_celery_tasks(queue_name: str) -> list:
    import base64
    import json

    from hct_mis_api.apps.core.celery import app as celery_app

    all_tasks = []

    if not is_celery_working(celery_app):
        raise CeleryConnectionException

    with celery_app.pool.acquire(block=True) as conn:
        tasks = None
        while tasks is None:
            tasks = conn.default_channel.client.lrange(queue_name, 0, -1)
        for task in tasks:
            j = json.loads(task)
            body = json.loads(base64.b64decode(j["body"]))
            all_tasks.append(
                {
                    "name": j["headers"]["task"],
                    "args": body[0],
                    "kwargs": body[1],
                    "status": "queued",
                }
            )
        all_tasks.extend(get_worker_tasks(celery_app))
    return all_tasks


def get_task_in_queue_or_running(
    name: str, all_celery_tasks: Optional[list] = None, args: Optional[list] = None, kwargs: Optional[dict] = None
) -> Optional[dict]:
    if all_celery_tasks is None:
        all_celery_tasks = get_all_celery_tasks("default")
    for task in all_celery_tasks:
        if task["name"] != name:
            continue
        if args is not None:
            if len(args) != len(task.get("args", [])):
                continue
            if not all(a == b for a, b in zip(args, task.get("args", []))):
                continue
        if kwargs is not None:
            if not all(task.get("kwargs", {}).get(key) == value for key, value in kwargs.items()):
                continue
        return task

    return None
