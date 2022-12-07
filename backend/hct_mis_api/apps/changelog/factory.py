import factory
from faker import Faker

from hct_mis_api.apps.changelog.models import Changelog

faker = Faker()


class ChangelogFactory(factory.DjangoModelFactory):
    class Meta:
        model = Changelog

    description = faker.paragraph(nb_sentences=5)
    version = faker.bothify(text="#.##.###")
    active = faker.boolean()
    date = faker.date_this_month()
