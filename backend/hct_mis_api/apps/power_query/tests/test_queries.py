from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from hct_mis_api.apps.household.fixtures import HouseholdFactory

from ...account.fixtures import UserFactory
from ...household.models import Household
from ..models import Query


class TestBasicRule(TestCase):
    @classmethod
    def setUpTestData(self):
        self.household = HouseholdFactory()
        self.user = UserFactory()

    def test_execution(self):
        r = Query(
            name="All HH", owner=self.user, target=ContentType.objects.get_for_model(Household), code="qs=conn.all()"
        )
        r.execute()
