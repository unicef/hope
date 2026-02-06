"""Sanction list related factories."""

import factory
from factory.django import DjangoModelFactory

from hope.models import SanctionList


class SanctionListFactory(DjangoModelFactory):
    class Meta:
        model = SanctionList
        django_get_or_create = ("strategy",)

    name = factory.Sequence(lambda n: f"Sanction List {n}")
    strategy = "hope.apps.sanction_list.strategies.un.UNSanctionList"
