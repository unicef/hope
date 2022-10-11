from django.test import TestCase

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.geo.models import Area
from hct_mis_api.apps.payment.fixtures import (
    CashPlanFactory,
    create_payment_verification_plan_with_status,
)
from hct_mis_api.apps.payment.models import (
    PaymentVerificationPlan,
    PaymentVerificationSummary,
    build_summary,
)
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.targeting.fixtures import (
    TargetingCriteriaFactory,
    TargetPopulationFactory,
)


class TestBuildSummary(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory.create()
        cls.business_area = create_afghanistan()

        cls.program = ProgramFactory(business_area=cls.business_area)
        cls.program.admin_areas.set(Area.objects.order_by("?")[:3])
        cls.target_population = TargetPopulationFactory(
            created_by=cls.user,
            targeting_criteria=TargetingCriteriaFactory(),
            business_area=cls.business_area,
        )
        cls.cash_plan = CashPlanFactory(
            name="TEST",
            program=cls.program,
            business_area=cls.business_area,
        )

    def test_status_pending_when_zero_verifications(self):
        build_summary(self.cash_plan)

        summary = PaymentVerificationSummary.objects.get(payment_plan=self.cash_plan)

        self.assertEqual(summary.status, PaymentVerificationSummary.STATUS_PENDING)

    def test_status_active_when_at_least_one_active_verification(self):
        self._create_verification_with_status(PaymentVerificationPlan.STATUS_ACTIVE)

        build_summary(self.cash_plan)

        summary = PaymentVerificationSummary.objects.get(payment_plan=self.cash_plan)
        self.assertEqual(summary.status, PaymentVerificationSummary.STATUS_ACTIVE)

    def test_status_finished_when_all_verifications_finished(self):
        self._create_verification_with_status(PaymentVerificationPlan.STATUS_FINISHED)

        build_summary(self.cash_plan)

        summary = PaymentVerificationSummary.objects.get(payment_plan=self.cash_plan)
        self.assertEqual(summary.status, PaymentVerificationSummary.STATUS_FINISHED)

    def test_status_pending_when_add_and_removed_verification(self):
        payment_verification_plan = self._create_verification_with_status(PaymentVerificationPlan.STATUS_PENDING)
        payment_verification_plan.delete()

        build_summary(self.cash_plan)

        summary = PaymentVerificationSummary.objects.get(payment_plan=self.cash_plan)
        self.assertEqual(summary.status, PaymentVerificationSummary.STATUS_PENDING)

    def test_query_number(self):
        with self.assertNumQueries(3):
            build_summary(self.cash_plan)

    def _create_verification_with_status(self, status):
        return create_payment_verification_plan_with_status(
            self.cash_plan,
            self.user,
            self.business_area,
            self.program,
            self.target_population,
            status,
        )
