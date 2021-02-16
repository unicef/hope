from datetime import timedelta
from random import randint

import factory
from factory import fuzzy
from pytz import utc

from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.reporting.models import Report


class ReportFactory(factory.DjangoModelFactory):
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
