"""Sanction list related factories."""

import factory
from factory.django import DjangoModelFactory

from hope.models import SanctionList
from hope.models.sanction_list_individual import SanctionListIndividual


class SanctionListFactory(DjangoModelFactory):
    class Meta:
        model = SanctionList
        django_get_or_create = ("strategy",)

    name = factory.Sequence(lambda n: f"Sanction List {n}")
    strategy = "hope.apps.sanction_list.strategies.un.UNSanctionList"


class SanctionListIndividualFactory(DjangoModelFactory):
    class Meta:
        model = SanctionListIndividual

    first_name = factory.Sequence(lambda n: f"First {n}")
    full_name = factory.LazyAttribute(lambda obj: f"{obj.first_name} Test")
    list_type = "UN"
    reference_number = factory.Sequence(lambda n: f"REF-{n}")
    data_id = factory.Sequence(lambda n: n + 1)
    version_num = 1
    sanction_list = factory.SubFactory(SanctionListFactory)
