"""Changelog-related factories."""

import datetime

import factory
from factory.django import DjangoModelFactory

from hope.models import Changelog


class ChangelogFactory(DjangoModelFactory):
    class Meta:
        model = Changelog

    description = factory.Sequence(lambda n: f"Changelog description {n}")
    version = factory.Sequence(lambda n: f"1.0.{n}")
    active = False
    date = factory.LazyFunction(datetime.date.today)
