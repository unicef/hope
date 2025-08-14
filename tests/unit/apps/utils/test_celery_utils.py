from django.test import TestCase

from hope.apps.utils.celery_utils import format_tasks


class TestCeleryUtils(TestCase):
    def test_format_tasks(self) -> None:
        tasks_dict = {
            "celery@high-priority-hope-celery-worker-6b77cc79b8-9wp5h": [],
            "celery@low-priority-hope-celery-worker-6b77cc79b8-9wp5h": [
                {
                    "eta": "2023-09-19T00:01:00.647778+00:00",
                    "priority": 6,
                    "request": {
                        "acknowledged": False,
                        "args": [],
                        "delivery_info": {
                            "exchange": "",
                            "priority": 0,
                            "redelivered": False,
                            "routing_key": "default",
                        },
                        "hostname": "celery@low-priority-hope-celery-worker-6b77cc79b8-9wp5h",
                        "id": "aa993de4-0353-44b9-a512-a700ced30a51",
                        "kwargs": {},
                        "name": "hope.apps.sanction_list.celery_tasks.sync_sanction_list_task",
                        "time_start": None,
                        "type": "hope.apps.sanction_list.celery_tasks.sync_sanction_list_task",
                        "worker_pid": None,
                    },
                },
                {
                    "acknowledged": False,
                    "args": [],
                    "delivery_info": {"exchange": "", "priority": 0, "redelivered": False, "routing_key": "default"},
                    "hostname": "celery@low-priority-hope-celery-worker-6b77cc79b8-9wp5h",
                    "id": "aa993de4-0353-44b9-a512-a700ced30a51",
                    "kwargs": {},
                    "name": "hope.apps.sanction_list.celery_tasks.sync_sanction_list_task",
                    "time_start": None,
                    "type": "hope.apps.sanction_list.celery_tasks.sync_sanction_list_task",
                    "worker_pid": None,
                },
            ],
        }
        formatted_tasks = list(format_tasks(tasks_dict, "queued"))

        self.assertEqual(len(formatted_tasks), 2)

        expected_payload = [
            {
                "id": "aa993de4-0353-44b9-a512-a700ced30a51",
                "name": "hope.apps.sanction_list.celery_tasks.sync_sanction_list_task",
                "args": [],
                "kwargs": {},
                "status": "queued",
            },
            {
                "id": "aa993de4-0353-44b9-a512-a700ced30a51",
                "name": "hope.apps.sanction_list.celery_tasks.sync_sanction_list_task",
                "args": [],
                "kwargs": {},
                "status": "queued",
            },
        ]
        self.assertEqual(formatted_tasks, expected_payload)
