import factory
from factory.django import DjangoModelFactory

from hct_mis_api.apps.steficon.models import Rule, RuleCommit


class RuleFactory(DjangoModelFactory):
    class Meta:
        model = Rule

    name = factory.Sequence(lambda n: "Rule %d" % n)
    definition = "result.value=Decimal('1.3')"
    enabled = True
    deprecated = False


class RuleCommitFactory(DjangoModelFactory):
    class Meta:
        model = RuleCommit

    rule = factory.SubFactory(RuleFactory)
    version = factory.Sequence(lambda n: n)
    affected_fields = ["value"]
    is_release = True
    enabled = True
    definition = "result.value=Decimal('1.3')"
