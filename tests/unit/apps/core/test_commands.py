from io import StringIO
from unittest import mock

from django.core.management import call_command
from django.test import TestCase
import pytest

pytestmark = pytest.mark.usefixtures("django_elasticsearch_setup")


@pytest.mark.elasticsearch
class TestCommands(TestCase):
    databases = "__all__"

    def test_initdemo(self) -> None:
        try:
            with mock.patch("sys.stdout", new=StringIO()):
                call_command("initdemo", "--skip-drop")
        except Exception as e:
            self.fail(e)
