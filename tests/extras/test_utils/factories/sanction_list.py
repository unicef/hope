"""Sanction list related factories."""

import factory
from factory.django import DjangoModelFactory

from hope.models import SanctionList, SanctionListIndividual


class SanctionListFactory(DjangoModelFactory):
    class Meta:
        model = SanctionList
        django_get_or_create = ("strategy",)

    name = factory.Sequence(lambda n: f"Sanction List {n}")
    strategy = "hope.apps.sanction_list.strategies.un.UNSanctionList"


class SanctionListIndividualFactory(DjangoModelFactory):
    class Meta:
        model = SanctionListIndividual

    sanction_list = factory.SubFactory(SanctionListFactory)
    data_id = factory.Sequence(lambda n: n + 1)
    version_num = 1
    first_name = factory.Sequence(lambda n: f"First{n}")
    full_name = factory.Sequence(lambda n: f"First{n} Last{n}")
    reference_number = factory.Sequence(lambda n: f"REF-{n}")
    list_type = factory.Sequence(lambda n: f"Type {n}")
