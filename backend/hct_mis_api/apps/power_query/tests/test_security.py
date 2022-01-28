from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase, override_settings

from .fixtures import QueryFactory


@override_settings(POWER_QUERY_DB_ALIAS="default")
class TestPowerQuery(TestCase):
    databases = ["default"]

    def test_deletion_not_allowed(self):
        query = QueryFactory(
            code="result=conn.all().delete()",
            target=ContentType.objects.filter(app_label="auth", model="permission").first(),
        )
        result, debug_info = query.execute()
        self.assertEqual(result[0], Permission.objects.count())
        self.assertTrue(Permission.objects.exists())

    def test_update_not_allowed(self):
        query = QueryFactory(
            code="result=conn.filter(codename='add_group').update(codename='---')",
            target=ContentType.objects.filter(app_label="auth", model="permission").first(),
        )
        result, debug_info = query.execute()
        self.assertEqual(result, 1)
        self.assertFalse(Permission.objects.filter(codename="---").exists())

    def test_print(self):
        query = QueryFactory(
            code="""
print("abc")
""",
            target=ContentType.objects.filter(app_label="auth", model="permission").first(),
        )
        result, debug_info = query.execute()
        self.assertEqual(debug_info["stdout"], ["abc"])
