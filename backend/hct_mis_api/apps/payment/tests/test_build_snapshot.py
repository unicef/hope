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


class TestBuildSnapshot(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        pass


