"""Factories for third-party app models."""

from django.contrib.auth.models import Group
import factory
from factory.django import DjangoModelFactory


class GroupFactory(DjangoModelFactory):
    class Meta:
        model = Group
        django_get_or_create = ("name",)

    name = factory.Sequence(lambda n: f"Group {n}")
