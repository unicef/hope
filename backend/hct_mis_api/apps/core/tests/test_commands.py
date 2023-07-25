from io import StringIO
from unittest import mock

from django.core.management import call_command

from hct_mis_api.apps.core.base_test_case import BaseElasticSearchTestCase
from hct_mis_api.conftest import disabled_locally_test


@disabled_locally_test
class TestCommands(BaseElasticSearchTestCase):
    databases = "__all__"

    def test_initdemo(self) -> None:
        try:
            with mock.patch("sys.stdout", new=StringIO()):
                call_command("initdemo", "--skip-drop")
        except Exception as e:
            self.fail(e)
