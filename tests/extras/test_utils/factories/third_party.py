"""Factories for third-party app models."""

from django.contrib.auth.models import Group
import factory
from factory.django import DjangoModelFactory
from flags.models import FlagState


class GroupFactory(DjangoModelFactory):
    class Meta:
        model = Group
        django_get_or_create = ("name",)

    name = factory.Sequence(lambda n: f"Group {n}")


class FlagStateFactory(DjangoModelFactory):
    class Meta:
        model = FlagState
        django_get_or_create = ("name", "condition", "value")

    name = "IS_ROOT"
    condition = "boolean"
    value = "True"
    required = False
