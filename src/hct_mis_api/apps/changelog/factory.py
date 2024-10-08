from factory.django import DjangoModelFactory
from faker import Faker

from hct_mis_api.apps.changelog.models import Changelog

faker = Faker()


class ChangelogFactory(DjangoModelFactory):
    class Meta:
        model = Changelog

    description = faker.paragraph(nb_sentences=5)
    version = faker.bothify(text="#.##.###")
    active = faker.boolean()
    date = faker.date_this_month()
