import factory
from extras.test_utils.factories.account import UserFactory
from extras.test_utils.factories.program import ProgramFactory
from factory.django import DjangoModelFactory
from faker import Faker

from hope.apps.core.models import BusinessArea
from hope.apps.periodic_data_update.models import (
    PDUXlsxTemplate,
    PDUXlsxUpload,
)

fake = Faker()


class PDUXlsxTemplateFactory(DjangoModelFactory):
    class Meta:
        model = PDUXlsxTemplate

    created_by = factory.SubFactory(UserFactory)
    status = factory.fuzzy.FuzzyChoice([choice[0] for choice in PDUXlsxTemplate.Status.choices])
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


class PDUXlsxUploadFactory(DjangoModelFactory):
    class Meta:
        model = PDUXlsxUpload

    created_by = factory.SubFactory(UserFactory)
    status = factory.fuzzy.FuzzyChoice([choice[0] for choice in PDUXlsxUpload.Status.choices])
    template = factory.SubFactory(PDUXlsxTemplateFactory)
