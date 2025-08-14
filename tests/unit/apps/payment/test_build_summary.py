from django.test import TestCase

from extras.test_utils.factories.account import UserFactory
from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.payment import (
    PaymentPlanFactory,
    PaymentVerificationSummaryFactory,
    create_payment_verification_plan_with_status,
)
from extras.test_utils.factories.program import ProgramFactory

from hope.apps.geo.models import Area
from hope.apps.payment.models import (
    PaymentVerificationPlan,
    PaymentVerificationSummary,
    build_summary,
)


class TestBuildSummary(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.user = UserFactory.create()
        cls.business_area = create_afghanistan()

        cls.program = ProgramFactory(business_area=cls.business_area)
        cls.program.admin_areas.set(Area.objects.order_by("?")[:3])
        cls.payment_plan = PaymentPlanFactory(
            name="TEST",
            program_cycle=cls.program.cycles.first(),
            business_area=cls.business_area,
            created_by=cls.user,
        )
        PaymentVerificationSummaryFactory(payment_plan=cls.payment_plan)

    def test_status_pending_when_zero_verifications(self) -> None:
        build_summary(self.payment_plan)

        summary = self.payment_plan.payment_verification_summary

        self.assertEqual(summary.status, PaymentVerificationSummary.STATUS_PENDING)

    def test_status_active_when_at_least_one_active_verification(self) -> None:
        self._create_verification_with_status(PaymentVerificationPlan.STATUS_ACTIVE)

        build_summary(self.payment_plan)

        summary = self.payment_plan.payment_verification_summary
        self.assertEqual(summary.status, PaymentVerificationSummary.STATUS_ACTIVE)

    def test_status_finished_when_all_verifications_finished(self) -> None:
        self._create_verification_with_status(PaymentVerificationPlan.STATUS_FINISHED)

        build_summary(self.payment_plan)

        summary = self.payment_plan.payment_verification_summary
        self.assertEqual(summary.status, PaymentVerificationSummary.STATUS_FINISHED)

    def test_status_pending_when_add_and_removed_verification(self) -> None:
        payment_verification_plan = self._create_verification_with_status(PaymentVerificationPlan.STATUS_PENDING)
        payment_verification_plan.delete()

        build_summary(self.payment_plan)

        summary = self.payment_plan.payment_verification_summary
        self.assertEqual(summary.status, PaymentVerificationSummary.STATUS_PENDING)

    def test_query_number(self) -> None:
        with self.assertNumQueries(2):
            build_summary(self.payment_plan)

    def _create_verification_with_status(self, status: str) -> PaymentVerificationPlan:
        return create_payment_verification_plan_with_status(
            self.payment_plan,
            self.user,
            self.business_area,
            self.program,
            status,
        )
