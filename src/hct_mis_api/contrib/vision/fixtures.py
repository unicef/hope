import factory.fuzzy
from factory.django import DjangoModelFactory
from pytz import utc

from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.contrib.vision.models import FundsCommitment


class FundsCommitmentFactory(DjangoModelFactory):
    class Meta:
        model = FundsCommitment

    rec_serial_number = factory.fuzzy.FuzzyInteger(1000, 99999999)
    business_area = factory.LazyAttribute(lambda o: BusinessArea.objects.first().cash_assist_code)
    document_type = "DO"
    currency_code = factory.Faker("currency_code")

    total_open_amount_local = factory.fuzzy.FuzzyDecimal(100.0, 10000.0)
    total_open_amount_usd = factory.fuzzy.FuzzyDecimal(100.0, 10000.0)
    update_date = factory.Faker(
        "date_time_this_decade",
        before_now=True,
        after_now=False,
        tzinfo=utc,
    )
