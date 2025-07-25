import factory
from factory.django import DjangoModelFactory
from pytz import utc

from hct_mis_api.apps.sanction_list.models import SanctionList, SanctionListIndividual


class SanctionListFactory(DjangoModelFactory):
    name = factory.Sequence(lambda n: f"Sanction List {n}")
    strategy = "hct_mis_api.apps.sanction_list.strategies.un.UNSanctionList"

    class Meta:
        model = SanctionList
        django_get_or_create = ("name",)


class SanctionListIndividualFactory(DjangoModelFactory):
    sanction_list = factory.SubFactory(SanctionListFactory)

    data_id = factory.Faker("random_int")
    version_num = 1
    first_name = factory.Faker("first_name")
    full_name = f"{factory.Faker('first_name')} {factory.Faker('last_name')}"
    reference_number = factory.Faker("word")
    listed_on = factory.Faker("date_time_this_decade", before_now=False, after_now=True, tzinfo=utc)
    comments = factory.Faker("sentence", nb_words=20)
    designation = factory.Faker("sentence", nb_words=2)
    list_type = factory.Faker("sentence", nb_words=2)
    street = factory.Faker("sentence", nb_words=2)
    city = factory.Faker("sentence", nb_words=2)
    state_province = factory.Faker("sentence", nb_words=2)
    address_note = factory.Faker("sentence", nb_words=2)
    country_of_birth = None

    class Meta:
        model = SanctionListIndividual
