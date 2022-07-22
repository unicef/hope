from uuid import UUID
from django.core.management import BaseCommand

import hct_mis_api.apps.payment.fixtures as payment_fixtures
import hct_mis_api.apps.cash_assist_datahub.fixtures as ca_fixtures

from hct_mis_api.apps.household.models import Individual
from hct_mis_api.apps.household.models import Household
from hct_mis_api.apps.program.fixtures import CashPlanFactory
from hct_mis_api.apps.program.models import CashPlan
from hct_mis_api.apps.payment.models import ServiceProvider
from hct_mis_api.apps.cash_assist_datahub.models import Session, PaymentRecord
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.household.fixtures import create_household


class Command(BaseCommand):
    def handle(self, *args, **options):
        business_areas = BusinessArea.objects.all()[:1]
        print(f"Business areas present: {len(business_areas)}")

        Session.objects.all().delete()
        for business_area in business_areas:
            Session.objects.get_or_create(business_area=business_area.code, status=Session.STATUS_READY)
        print(f"Sessions: {Session.objects.count()}")

        service_provider_ca_id = UUID("00000000-0000-0000-0000-000000000000")
        cash_plan_ca_id = UUID("00000000-0000-0000-0000-000000000001")

        session = Session.objects.order_by("?").first()
        ServiceProvider.objects.all().delete()
        payment_fixtures.ServiceProviderFactory.create(ca_id=service_provider_ca_id)
        print(f"Service providers: {ServiceProvider.objects.count()}")

        PaymentRecord.objects.all().delete()
        Household.objects.all().delete()
        Individual.objects.all().delete()
        for session in Session.objects.all():
            household, _ = create_household(
                {
                    "size": 1,
                    "residence_status": "HOST",
                    "business_area": BusinessArea.objects.get(code=session.business_area),
                    "total_cash_received": None,
                    "total_cash_received_usd": None,
                },
            )
            ca_fixtures.PaymentRecordFactory.create(
                session=session,
                service_provider_ca_id=service_provider_ca_id,
                cash_plan_ca_id=cash_plan_ca_id,
                household_mis_id=household.id,
            )
            payment_fixtures.PaymentRecordFactory.create(
                household=household,
                delivered_quantity=1000,
                delivered_quantity_usd=2000,
            )

        print(f"Payment records: {PaymentRecord.objects.count()}")
        print(f"Households: {Household.objects.count()}")
        print(f"Individuals: {Individual.objects.count()}")

        CashPlan.objects.all().delete()
        CashPlanFactory.create(ca_id=cash_plan_ca_id)
        print(f"Cash plans: {CashPlan.objects.count()}")
