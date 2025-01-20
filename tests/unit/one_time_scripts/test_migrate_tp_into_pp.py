from django.test import TestCase
from django.utils import timezone

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.accountability.fixtures import (
    CommunicationMessageFactory,
    SurveyFactory,
)
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.payment.fixtures import PaymentPlanFactory
from hct_mis_api.apps.payment.models import Payment, PaymentPlan
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.steficon.fixtures import RuleCommitFactory
from hct_mis_api.apps.targeting.fixtures import (
    TargetingCriteriaFactory,
    TargetingCriteriaRuleFactory,
    TargetPopulationFactory,
)
from hct_mis_api.apps.targeting.models import (
    TargetingCriteria,
    TargetingCriteriaRule,
    TargetPopulation,
)
from hct_mis_api.one_time_scripts.migrate_tp_into_pp import (
    create_payments_for_pending_payment_plans,
    migrate_tp_into_pp,
)


class MigrationTPIntoPPTest(TestCase):
    def setUp(cls) -> None:
        cls.business_area = create_afghanistan()
        cls.user = UserFactory()
        cls.program = ProgramFactory(name="Unit Test")
        cls.program_cycle = cls.program.cycles.first()

        # preparing PaymentPlan
        cls.targeting_criteria_for_preparing_pp = TargetingCriteriaFactory()
        cls.tp_for_preparing = TargetPopulationFactory(
            name="TP for Preparing PP",
            targeting_criteria=cls.targeting_criteria_for_preparing_pp,
            business_area=cls.business_area,
            created_by=cls.user,
            status=TargetPopulation.STATUS_ASSIGNED,
            build_status=TargetPopulation.BUILD_STATUS_OK,
            ca_id="ca_id test",
            ca_hash_id="ca_hash_id test",
            sent_to_datahub=True,
        )
        cls.preparing_payment_plan = PaymentPlanFactory(
            program_cycle=cls.program_cycle,
            created_by=cls.user,
            targeting_criteria=None,
            target_population=cls.tp_for_preparing,
            build_status=None,
            status=PaymentPlan.Status.PREPARING,
        )
        # tp_1
        cls.targeting_criteria_1_without_rule = TargetingCriteriaFactory(household_ids="HH-11", individual_ids="IND-11")
        cls.rule_commit = RuleCommitFactory()
        cls.time_now = timezone.now()
        cls.tp_1 = TargetPopulationFactory(
            name="TP without rule check all fields",
            targeting_criteria=cls.targeting_criteria_1_without_rule,
            business_area=cls.business_area,
            created_by=cls.user,
            status=TargetPopulation.STATUS_STEFICON_COMPLETED,
            change_date=cls.time_now,
            build_status=TargetPopulation.BUILD_STATUS_FAILED,
            built_at=cls.time_now,
            program_cycle=cls.program_cycle,
            steficon_rule=cls.rule_commit,
            steficon_applied_date=cls.time_now,
            vulnerability_score_min=123,
            vulnerability_score_max=999,
            excluded_ids="Test IND-123",
            exclusion_reason="Exclusion_reason",
            total_households_count=1,
            total_individuals_count=2,
            child_male_count=3,
            child_female_count=4,
            adult_male_count=5,
            adult_female_count=6,
        )
        # tp_2
        cls.targeting_criteria_2_with_rule = TargetingCriteriaFactory(household_ids="HH-22", individual_ids="IND-22")
        TargetingCriteriaRuleFactory(
            targeting_criteria=cls.targeting_criteria_2_with_rule, household_ids="", individual_ids=""
        )
        cls.tp_2 = TargetPopulationFactory(
            name="TP with rule",
            targeting_criteria=cls.targeting_criteria_2_with_rule,
            business_area=cls.business_area,
            created_by=cls.user,
            status=TargetPopulation.STATUS_LOCKED,
            build_status=TargetPopulation.BUILD_STATUS_OK,
        )

        # tp_3 with PaymentPlan
        cls.targeting_criteria_3 = TargetingCriteriaFactory()
        cls.tp_3 = TargetPopulationFactory(
            name="TP with Open PP",
            targeting_criteria=cls.targeting_criteria_3,
            business_area=cls.business_area,
            created_by=cls.user,
            status=TargetPopulation.STATUS_ASSIGNED,
            build_status=TargetPopulation.BUILD_STATUS_OK,
        )
        cls.payment_plan_2 = PaymentPlanFactory(
            program_cycle=cls.program_cycle,
            created_by=cls.user,
            targeting_criteria=None,
            status=PaymentPlan.Status.OPEN,
            target_population=cls.tp_3,
            build_status=None,
        )
        # tp_4 with PaymentPlan
        cls.targeting_criteria_4 = TargetingCriteriaFactory()
        cls.tp_4 = TargetPopulationFactory(
            name="TP with Finished PP",
            targeting_criteria=cls.targeting_criteria_4,
            business_area=cls.business_area,
            created_by=cls.user,
            status=TargetPopulation.STATUS_ASSIGNED,
            build_status=TargetPopulation.BUILD_STATUS_OK,
        )
        cls.payment_plan_3 = PaymentPlanFactory(
            program_cycle=cls.program_cycle,
            created_by=cls.user,
            targeting_criteria=None,
            status=PaymentPlan.Status.FINISHED,
            target_population=cls.tp_4,
            build_status=None,
        )
        # create Tps for all other statuses
        for tp_status in [
            TargetPopulation.STATUS_STEFICON_WAIT,
            TargetPopulation.STATUS_STEFICON_RUN,
            TargetPopulation.STATUS_STEFICON_COMPLETED,
            TargetPopulation.STATUS_STEFICON_ERROR,
            TargetPopulation.STATUS_PROCESSING,
            TargetPopulation.STATUS_SENDING_TO_CASH_ASSIST,
            TargetPopulation.STATUS_READY_FOR_CASH_ASSIST,
            TargetPopulation.STATUS_READY_FOR_PAYMENT_MODULE,
        ]:
            TargetPopulationFactory(
                name=f"TP for status {tp_status}",
                targeting_criteria=TargetingCriteriaFactory(),
                business_area=cls.business_area,
                created_by=cls.user,
                status=tp_status,
                build_status=TargetPopulation.BUILD_STATUS_OK,
            )
        # removed TP
        removed_tp = TargetPopulationFactory(
            name="Removed TP",
            targeting_criteria=TargetingCriteriaFactory(),
            business_area=cls.business_area,
            created_by=cls.user,
            status=TargetPopulation.STATUS_ASSIGNED,
            build_status=TargetPopulation.BUILD_STATUS_OK,
            is_removed=True,
        )

        # create Message & Survey
        # tp with PP
        cls.message_1 = CommunicationMessageFactory(
            title="For TP with Open PP",
            business_area=cls.business_area,
            target_population=cls.tp_3,
            created_by=cls.user,
        )
        # tp without PP
        cls.message_2 = CommunicationMessageFactory(
            title="222",
            business_area=cls.business_area,
            target_population=cls.tp_1,
            created_by=cls.user,
        )
        # tp with PP
        cls.survey_1 = SurveyFactory(target_population=cls.tp_4, created_by=cls.user)
        # tp without PP
        cls.survey_2 = SurveyFactory(target_population=cls.tp_2, created_by=cls.user)
        # just for test add survey with removed tp
        cls.survey_without_pp = SurveyFactory(target_population=removed_tp, created_by=cls.user)

    def test_migrate_tp_into_pp(self) -> None:
        self.assertEqual(TargetPopulation.all_objects.all().count(), 14)
        self.assertEqual(TargetingCriteriaRule.objects.all().count(), 1)
        self.assertEqual(TargetingCriteria.objects.all().count(), 14)

        self.assertEqual(PaymentPlan.all_objects.count(), 3)
        self.assertEqual(Payment.objects.filter(parent=self.preparing_payment_plan).count(), 0)

        self.assertIsNone(self.message_1.payment_plan)
        self.assertIsNone(self.message_2.payment_plan)
        self.assertIsNone(self.survey_1.payment_plan)
        self.assertIsNone(self.survey_2.payment_plan)
        self.assertIsNone(self.survey_without_pp.payment_plan)

        migrate_tp_into_pp()
        create_payments_for_pending_payment_plans()

        self.assertEqual(TargetPopulation.all_objects.all().count(), 14)
        self.assertEqual(TargetingCriteriaRule.objects.all().count(), 2)  # new Rule created and migrated hh ind ids
        self.assertEqual(TargetingCriteria.objects.all().count(), 14)

        self.assertEqual(PaymentPlan.all_objects.count(), 13)
        # not copy TP is_removed=True
        self.assertFalse(PaymentPlan.objects.filter(name="Removed TP").exists())

        self.assertEqual(Payment.objects.filter(parent=self.preparing_payment_plan).count(), 0)

        self.preparing_payment_plan.refresh_from_db()
        self.assertEqual(self.preparing_payment_plan.status, PaymentPlan.Status.OPEN)
        self.assertEqual(self.preparing_payment_plan.build_status, PaymentPlan.BuildStatus.BUILD_STATUS_OK)
        self.assertEqual(self.preparing_payment_plan.name, "TP for Preparing PP")
        self.assertEqual(
            str(self.preparing_payment_plan.targeting_criteria_id), str(self.targeting_criteria_for_preparing_pp.pk)
        )
        # check internal data json
        self.assertEqual(
            self.preparing_payment_plan.internal_data.get("target_population_id"), str(self.tp_for_preparing.pk)
        )
        self.assertEqual(self.preparing_payment_plan.internal_data.get("ca_id"), self.tp_for_preparing.ca_id)
        self.assertEqual(self.preparing_payment_plan.internal_data.get("ca_hash_id"), self.tp_for_preparing.ca_hash_id)
        self.assertEqual(
            self.preparing_payment_plan.internal_data.get("sent_to_datahub"), str(self.tp_for_preparing.sent_to_datahub)
        )

        first_rule_for_targeting_criteria_1_without_rule = self.targeting_criteria_1_without_rule.get_rules().first()
        self.assertEqual(first_rule_for_targeting_criteria_1_without_rule.household_ids, "HH-11")
        self.assertEqual(first_rule_for_targeting_criteria_1_without_rule.individual_ids, "IND-11")

        first_rule_for_targeting_criteria_2_with_rule = self.targeting_criteria_2_with_rule.get_rules().first()
        self.assertEqual(first_rule_for_targeting_criteria_2_with_rule.household_ids, "HH-22")
        self.assertEqual(first_rule_for_targeting_criteria_2_with_rule.individual_ids, "IND-22")

        # check all migrated fields
        new_pp = PaymentPlan.objects.get(name="TP without rule check all fields")
        self.assertEqual(new_pp.status, PaymentPlan.Status.TP_OPEN)
        self.assertEqual(new_pp.created_by, self.user)
        self.assertEqual(new_pp.build_status, PaymentPlan.BuildStatus.BUILD_STATUS_FAILED)
        self.assertEqual(new_pp.program_cycle, self.program_cycle)
        self.assertEqual(new_pp.business_area, self.business_area)
        self.assertEqual(new_pp.steficon_rule_targeting, self.rule_commit)
        self.assertEqual(new_pp.steficon_targeting_applied_date, self.time_now)
        self.assertEqual(new_pp.vulnerability_score_min, 123)
        self.assertEqual(new_pp.vulnerability_score_max, 999)
        self.assertEqual(new_pp.excluded_ids, "Test IND-123")
        self.assertEqual(new_pp.exclusion_reason, "Exclusion_reason")
        self.assertEqual(new_pp.total_households_count, 1)
        self.assertEqual(new_pp.total_individuals_count, 2)
        self.assertEqual(new_pp.male_children_count, 3)
        self.assertEqual(new_pp.female_children_count, 4)
        self.assertEqual(new_pp.male_adults_count, 5)
        self.assertEqual(new_pp.female_adults_count, 6)

        # check Message & Survey
        self.message_1.refresh_from_db()
        self.message_2.refresh_from_db()
        self.survey_1.refresh_from_db()
        self.survey_2.refresh_from_db()
        self.survey_without_pp.refresh_from_db()
        self.assertEqual(self.message_1.payment_plan, self.payment_plan_2)
        self.assertEqual(self.message_2.payment_plan.internal_data["target_population_id"], str(self.tp_1.pk))
        self.assertEqual(self.survey_1.payment_plan, self.payment_plan_3)
        self.assertEqual(self.survey_2.payment_plan.internal_data["target_population_id"], str(self.tp_2.pk))
        self.assertIsNone(self.survey_without_pp.payment_plan)
