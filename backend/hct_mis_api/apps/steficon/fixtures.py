import factory

from hct_mis_api.apps.steficon.models import Rule


class RuleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Rule

    name = factory.Sequence(lambda n: "Rule %d" % n)
    definition = "result.value=Decimal('1.3')"
