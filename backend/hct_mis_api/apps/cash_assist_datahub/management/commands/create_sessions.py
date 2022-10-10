from uuid import UUID

from django.core.management import BaseCommand

import hct_mis_api.apps.cash_assist_datahub.fixtures as ca_fixtures
import hct_mis_api.apps.payment.fixtures as payment_fixtures
from hct_mis_api.apps.cash_assist_datahub.models import Session
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.household.fixtures import create_household
from hct_mis_api.apps.program.fixtures import CashPlanFactory


class Command(BaseCommand):
    def handle(self, *args, **options):
        business_areas = BusinessArea.objects.all()
        some_business_area = business_areas.order_by("?").first()

        some_session = Session.objects.get_or_create(business_area=some_business_area.code, status=Session.STATUS_READY)

        service_provider_ca_id = UUID("00000000-0000-0000-0000-000000000000")
        cash_plan_ca_id = UUID("00000000-0000-0000-0000-000000000001")

        payment_fixtures.ServiceProviderFactory.create(ca_id=service_provider_ca_id)

        household, _ = create_household(
            {
                "size": 1,
                "residence_status": "HOST",
                "business_area": BusinessArea.objects.get(code=some_session.business_area),
                "total_cash_received": None,
                "total_cash_received_usd": None,
            },
        )
        ca_fixtures.PaymentRecordFactory.create(
            session=some_session,
            service_provider_ca_id=service_provider_ca_id,
            cash_plan_ca_id=cash_plan_ca_id,
            household_mis_id=household.id,
        )
        payment_fixtures.PaymentRecordFactory.create(
            household=household,
            delivered_quantity=1000,
            delivered_quantity_usd=2000,
        )

        CashPlanFactory.create(ca_id=cash_plan_ca_id)
