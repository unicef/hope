import factory
from factory.django import DjangoModelFactory

from hct_mis_api.apps.account.fixtures import BusinessAreaFactory
from hct_mis_api.apps.dashboard.models import DashReport


class DashReportFactory(DjangoModelFactory):
    class Meta:
        model = DashReport

    business_area = factory.SubFactory(BusinessAreaFactory)
    file = factory.django.FileField(filename="test_report.json")
    status = DashReport.COMPLETED
