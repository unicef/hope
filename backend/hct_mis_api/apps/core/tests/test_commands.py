from django.core.management import call_command

from hct_mis_api.apps.core.base_test_case import BaseElasticSearchTestCase


class TestCommands(BaseElasticSearchTestCase):
    databases = "__all__"

    def test_initdemo(self):
        try:
            call_command("initdemo", "--skip-drop")
        except Exception as e:
            self.fail(e)
