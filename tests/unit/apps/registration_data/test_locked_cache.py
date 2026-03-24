from threading import Thread
import time

import pytest

from hope.apps.registration_data.celery_tasks import locked_cache


@pytest.fixture
def execution_flags() -> dict:
    return {"first": False, "second": False}


def test_locked_cache(execution_flags: dict) -> None:
    def worker(flag_key: str, delay: int) -> None:
        with locked_cache("function_with_delay") as locked:
            if not locked:
                return
            time.sleep(delay)
            execution_flags[flag_key] = True

    thread1 = Thread(target=worker, args=("first", 1))
    thread1.start()
    time.sleep(0.2)
    thread2 = Thread(target=worker, args=("second", 1))
    thread2.start()

    thread1.join()
    thread2.join()

    assert execution_flags["first"]
    assert not execution_flags["second"]
