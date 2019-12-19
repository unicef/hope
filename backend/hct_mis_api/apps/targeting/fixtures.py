import json

import factory

from account.fixtures import UserFactory
from household.fixtures import HouseholdFactory
from targeting.models import TargetPopulation


class TargetPopulationFactory(factory.DjangoModelFactory):

    class Meta:
        model = TargetPopulation

    name = factory.Faker(
        'sentence',
        nb_words=6,
        variable_nb_words=True,
        ext_word_list=None,
    )
    created_by = factory.SubFactory(UserFactory)
    rules = json.loads('{"example": 123}')
    households = factory.RelatedFactory(HouseholdFactory)
