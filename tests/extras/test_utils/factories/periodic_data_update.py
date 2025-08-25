import factory
from extras.test_utils.factories.account import UserFactory
from extras.test_utils.factories.program import ProgramFactory
from factory.django import DjangoModelFactory
from faker import Faker

from models.core import BusinessArea
from models.periodic_data_update import (
    PeriodicDataUpdateTemplate,
    PeriodicDataUpdateUpload,
)

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
