from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from hct_mis_api.apps.household.fixtures import HouseholdFactory

from ...household.models import Household
from ..models import Query


class TestBasicRule(TestCase):
    @classmethod
    def setUpTestData(self):
        self.household = HouseholdFactory.build()

    def test_execution(self):
        r = Query(name="All HH", target=ContentType.objects.get_for_model(Household), code="qs=conn.all()")
        r.execute()
