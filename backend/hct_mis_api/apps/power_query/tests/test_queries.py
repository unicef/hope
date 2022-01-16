from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from ...account.fixtures import UserFactory
from ...account.models import User
from ..models import Query


class TestBasicRule(TestCase):
    @classmethod
    def setUpTestData(self):
        self.user = UserFactory()

    def test_execution(self):
        r = Query(name="All HH", owner=self.user, target=ContentType.objects.get_for_model(User), code="qs=conn.all()")
        r.execute()
