import datetime as dt
import random
from typing import List

import factory
from account.fixtures import UserFactory
from core.utils import JSONFactory
from factory import fuzzy
from household.fixtures import HouseholdFactory
from household.fixtures import IndividualFactory
from household.models import Individual
from registration_data.fixtures import RegistrationDataImportFactory
from targeting.models import TargetPopulation
from targeting.models import TargetRule

_BATCH_SIZE = 5
_HOUSEHOLDS = []

for _ in range(_BATCH_SIZE):
    individual = IndividualFactory.create()
    registration_data_import_id = RegistrationDataImportFactory.create()
    _HOUSEHOLDS.append(
        HouseholdFactory.create(
            registration_data_import_id=registration_data_import_id,
            representative=individual,
            head_of_household=individual,
        )
    )


class TargetPopulationFactory(factory.DjangoModelFactory):
    class Meta:
        model = TargetPopulation

    name = factory.Faker(
        "sentence", nb_words=6, variable_nb_words=True, ext_word_list=None,
    )
    created_by = factory.SubFactory(UserFactory)
    created_at = factory.Faker(
        "date_time_this_decade", before_now=False, after_now=True
    )
    last_edited_at = factory.LazyAttribute(
        lambda t: t.created_at + dt.timedelta(days=random.randint(600, 10000))
    )
    status = factory.fuzzy.FuzzyChoice(
        TargetPopulation.STATE_CHOICES, getter=lambda x: x[0],
    )

    @factory.post_generation
    def households(self, create, extracted, **kwargs):
        if not create:
            self.households.add(*_HOUSEHOLDS)

        if extracted:
            for household in extracted:
                self.households.add(household)

    @factory.post_generation
    def target_rules(self, create, extracted, **kwargs):
        if not create:
            target_rules = []
            for target_rule, rule_dict in zip(
                TargetRuleFactory.create_batch(_BATCH_SIZE),
                TargetRuleFactory.generate_target_rules_dict(),
            ):
                target_rule.flex_rules = rule_dict["flex_rules"]
                target_rule.core_rules = rule_dict["core_rules"]
                target_rule.save()
                target_rules.append(target_rule)
            self.target_rules.add(*target_rules)

        if extracted:
            for target_rule in extracted:
                self.target_rules.add(target_rule)


class TargetRuleFactory(factory.DjangoModelFactory):
    class Meta:
        model = TargetRule

    flex_rules = factory.Dict(
        {
            "age_min": fuzzy.FuzzyInteger(1, 10),
            "age_max": fuzzy.FuzzyInteger(11, 120),
        },
        dict_factory=JSONFactory,
    )
    core_rules = factory.Dict(
        {
            "intake_group": factory.Faker(
                "sentence",
                nb_words=6,
                variable_nb_words=True,
                ext_word_list=None,
            ),
            "sex": fuzzy.FuzzyChoice(
                Individual.SEX_CHOICE, getter=lambda x: x[0]
            ),
            "num_individuals_min": fuzzy.FuzzyInteger(1, 2),
            "num_individuals_max": fuzzy.FuzzyInteger(3, 20),
        },
        dict_factory=JSONFactory,
    )
    target_population = factory.SubFactory(TargetPopulationFactory)

    @classmethod
    def generate_target_rules_dict(cls, households = None) -> List[dict]:
        households = households or _HOUSEHOLDS
        today = dt.datetime.now().today()
        get_age = lambda year: today.year - year
        return [
            {
                "flex_rules": {
                    "age_min": get_age(household.representative.dob.year),
                    "age_max": get_age(household.representative.dob.year),
                },
                "core_rules": {
                    "intake_group": household.registration_data_import_id.name,
                    "sex": household.head_of_household.sex,
                    "num_individuals_min": household.family_size,
                    "num_individuals_max": household.family_size,
                },
            }
            for household in households
        ]
