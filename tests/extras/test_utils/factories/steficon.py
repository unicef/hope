"""Steficon-related factories."""

from django.db.models import Max
import factory
from factory.django import DjangoModelFactory

from hope.models import Rule, RuleCommit


class RuleFactory(DjangoModelFactory):
    class Meta:
        model = Rule

    name = factory.Sequence(lambda n: f"Rule {n}")


class RuleCommitFactory(DjangoModelFactory):
    class Meta:
        model = RuleCommit

    rule = factory.SubFactory(RuleFactory)
    version = factory.LazyAttribute(
        lambda o: (RuleCommit.objects.filter(rule=o.rule).aggregate(Max("version"))["version__max"] or 0) + 1
    )
    affected_fields = ["definition"]
