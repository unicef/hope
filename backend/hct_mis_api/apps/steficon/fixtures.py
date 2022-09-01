import factory

from hct_mis_api.apps.steficon.models import Rule, RuleCommit


class RuleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Rule

    name = factory.Sequence(lambda n: "Rule %d" % n)
    definition = "result.value=Decimal('1.3')"
    enabled = True
    deprecated = False


class RuleCommitFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = RuleCommit

    rule = factory.SubFactory(RuleFactory)
    version = factory.Sequence(lambda n: n)
    affected_fields = ["value"]
    is_release = True
