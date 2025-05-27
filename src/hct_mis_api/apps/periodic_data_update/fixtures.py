import factory
from factory.django import DjangoModelFactory
from faker import Faker

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.periodic_data_update.models import (
    PeriodicDataUpdateTemplate,
    PeriodicDataUpdateUpload,
)
from hct_mis_api.apps.program.fixtures import ProgramFactory

fake = Faker()


class PeriodicDataUpdateTemplateFactory(DjangoModelFactory):
    class Meta:
        model = PeriodicDataUpdateTemplate

    created_by = factory.SubFactory(UserFactory)
    status = factory.fuzzy.FuzzyChoice([choice[0] for choice in PeriodicDataUpdateTemplate.Status.choices])
    business_area = factory.LazyAttribute(lambda o: BusinessArea.objects.first())
    program = factory.SubFactory(ProgramFactory)
    number_of_records = fake.random_int(min=1, max=100)
    rounds_data = factory.LazyAttribute(
        lambda _: [
            {
                "field": fake.sentence(nb_words=3),
                "round": fake.random_int(min=1, max=10),
                "round_name": fake.sentence(nb_words=3),
                "number_of_records": fake.random_int(min=1, max=100),
            }
            for _ in range(2)
        ]
    )
    filters = {}


class PeriodicDataUpdateUploadFactory(DjangoModelFactory):
    class Meta:
        model = PeriodicDataUpdateUpload

    created_by = factory.SubFactory(UserFactory)
    status = factory.fuzzy.FuzzyChoice([choice[0] for choice in PeriodicDataUpdateUpload.Status.choices])
    template = factory.SubFactory(PeriodicDataUpdateTemplateFactory)
