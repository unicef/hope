from django.core.management import call_command
from django.test import TestCase


class TestCommands(TestCase):
    databases = "__all__"

    def test_initdemo(self):
        try:
            call_command("initdemo", "--skip-drop")
        except Exception as e:
            self.fail(e)
