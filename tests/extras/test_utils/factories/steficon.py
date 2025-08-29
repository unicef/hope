import factory
from factory.django import DjangoModelFactory

from hope.models.business_area import BusinessArea
from hope.models.rule import Rule, RuleCommit


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


def generate_rule_formulas() -> None:
    afghanistan = BusinessArea.objects.get(slug="afghanistan")
    rule_1 = RuleFactory(
        name="Test Formula for Targeting 011",
        definition="result.value=211",
        description="",
        language="python",
        type="TARGETING",
        flags={"individual_data_needed": False},
    )
    rule_1.allowed_business_areas.set([afghanistan])
    RuleCommitFactory(rule=rule_1, definition="result.value=222", language="python")
    rule_2 = RuleFactory(
        name="Test Formula for Targeting 022",
        definition="result.value=233",
        description="",
        language="python",
        type="TARGETING",
        flags={"individual_data_needed": False},
    )
    rule_2.allowed_business_areas.set([afghanistan])
    RuleCommitFactory(rule=rule_2, definition="result.value=255", language="python", version=11)
    rule_3 = RuleFactory(
        name="Test Formula for Payment Plan 033",
        definition="result.value=210",
        description="",
        language="python",
        type="PAYMENT_PLAN",
        flags={"individual_data_needed": False},
    )
    rule_3.allowed_business_areas.set([afghanistan])
    RuleCommitFactory(rule=rule_3, definition="result.value=212", language="python", version=22)
    rule_4 = RuleFactory(
        name="Test Formula for Payment Plan 044",
        definition="result.value=244",
        description="",
        language="python",
        type="PAYMENT_PLAN",
        flags={"individual_data_needed": False},
    )
    rule_4.allowed_business_areas.set([afghanistan])
    RuleCommitFactory(rule=rule_4, definition="result.value=244", language="python", version=33)
