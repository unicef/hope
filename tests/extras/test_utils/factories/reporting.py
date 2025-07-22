from datetime import timedelta
from random import randint

import factory
from extras.test_utils.factories.account import UserFactory
from factory import fuzzy
from factory.django import DjangoModelFactory
from pytz import utc

from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.reporting.models import DashboardReport, Report


class ReportFactory(DjangoModelFactory):
    class Meta:
        model = Report

    business_area = factory.LazyAttribute(lambda o: BusinessArea.objects.first())
    status = fuzzy.FuzzyChoice(
        Report.STATUSES,
        getter=lambda c: c[0],
    )
    date_from = factory.Faker(
        "date_time_this_decade",
        before_now=True,
        after_now=False,
        tzinfo=utc,
    )
    date_to = factory.LazyAttribute(lambda o: o.date_from + timedelta(days=randint(60, 1000)))
    report_type = fuzzy.FuzzyChoice(
        Report.REPORT_TYPES,
        getter=lambda c: c[0],
    )
    created_by = factory.SubFactory(UserFactory)


class DashboardReportFactory(DjangoModelFactory):
    class Meta:
        model = DashboardReport

    business_area = factory.LazyAttribute(lambda o: BusinessArea.objects.first())
    created_by = factory.SubFactory(UserFactory)
    status = fuzzy.FuzzyChoice(DashboardReport.STATUSES, getter=lambda c: c[0])
    report_type = fuzzy.FuzzyChoice(DashboardReport.REPORT_TYPES, getter=lambda c: [c[0]])
