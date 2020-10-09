from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.test import TestCase

from core.models import BusinessArea
from household.fixtures import create_household
from household.models import Household, Individual, FEMALE, MALE
from targeting.models import TargetingCriteriaRuleFilter, TargetingCriteria, TargetingCriteriaRule


class TestIndividualSubcriteria(TestCase):
    def setUp(self):
        call_command("loadflexfieldsattributes")
        call_command("loadbusinessareas")
        business_area = BusinessArea.objects.first()
        (household, individuals) = create_household(
            {
                "size": 2,
                "business_area": business_area,
            }
        )
        individuals[0].sex = FEMALE
        individuals[1].sex = MALE
        individuals[1].marital_status = "MARRIED"
        self.household_targeted = household
        (household, individuals) = create_household(
            {
                "size": 1,
                "business_area": business_area,
            },
            {"sex": FEMALE},
        )
        self.not_targeted_household = household

    def test_all_individuals_are_female(self):
        query = Household.objects.all()
        tc =TargetingCriteria()
        tc.save()
        tcr = TargetingCriteriaRule()
        tcr.targeting_criteria= tc
        tcr.save()
        ruleFilter =TargetingIndividualSubcriteriaRuleFilter(targeting_criteria_rule=tcr)

        self.assertEqual(query.count(), 1)
        self.assertEqual(query.first().id, self.household_targeted.id)
