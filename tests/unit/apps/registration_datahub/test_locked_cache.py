from threading import Thread
import time

from django.test import TestCase

from hope.apps.registration_datahub.celery_tasks import locked_cache


class DummyClass:
    def __init__(self) -> None:
        self._executed = False

    def __call__(self, delay: int = 0) -> None:
        with locked_cache("function_with_delay") as locked:
            if not locked:
                return
            time.sleep(delay)
            self._executed = True


class TestLockedCache(TestCase):
    def test_locked_cache(self) -> None:
        dummy_class1 = DummyClass()
        dummy_class2 = DummyClass()
        thread1 = Thread(target=dummy_class1, args=(5,))
        thread1.start()
        time.sleep(1)
        thread2 = Thread(target=dummy_class2, args=(5,))
        thread2.start()

        threads = [thread1, thread2]

        for thread in threads:
            thread.join()

        assert dummy_class1._executed
        assert not dummy_class2._executed
