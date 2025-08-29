from factory.django import DjangoModelFactory
import factory.fuzzy
from faker import Faker
from pytz import utc

from hope.models.business_area import BusinessArea
from hope.contrib.vision.models import FundsCommitment

fake = Faker()


class FundsCommitmentFactory(DjangoModelFactory):
    class Meta:
        model = FundsCommitment

    rec_serial_number = factory.fuzzy.FuzzyInteger(1000, 99999999)
    funds_commitment_item = factory.LazyFunction(lambda: f"{fake.random_int(min=1, max=999):03d}")

    office = factory.LazyAttribute(lambda o: BusinessArea.objects.first())
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
