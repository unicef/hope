from datetime import datetime
from uuid import UUID

import pytest
from dateutil.relativedelta import relativedelta

from page_object.payment_module.payment_module import PaymentModule

from hct_mis_api.apps.account.models import User
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.payment.models import PaymentPlan
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.targeting.fixtures import TargetingCriteriaFactory, TargetPopulationFactory
from hct_mis_api.apps.targeting.models import TargetPopulation

pytestmark = pytest.mark.django_db(transaction=True)

@pytest.mark.usefixtures("login")
class TestSmokePaymentModule:
    def test_smoke_payment_plan(self, pagePaymentModule: PaymentModule) -> None:
        program = Program.objects.first()
        targeting_criteria = TargetingCriteriaFactory()
        target_population = TargetPopulationFactory(
            program=program,
            status=TargetPopulation.STATUS_OPEN,
            targeting_criteria=targeting_criteria,
        )
        payment_plan = PaymentPlan.objects.update_or_create(
            pk=UUID("00000000-feed-beef-0000-00000badf00d"),
            business_area=BusinessArea.objects.filter(slug="afghanistan").first(),
            target_population=target_population,
            start_date=datetime.now() - relativedelta(months=1),
            end_date=datetime.now() + relativedelta(months=1),
            currency="USD",
            dispersion_start_date=datetime.now() - relativedelta(months=1),
            dispersion_end_date=datetime.now() + relativedelta(months=1),
            status_date=datetime.now(),
            created_by=User.objects.first(),
            program=program,
        )

        print(payment_plan)
