from django.utils import timezone

import pytest
from extras.test_utils.factories.account import PartnerFactory
from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.geo import AreaFactory, AreaTypeFactory, CountryFactory
from extras.test_utils.factories.household import create_household
from extras.test_utils.factories.payment import (
    FinancialServiceProviderFactory,
    PaymentFactory,
    PaymentPlanFactory,
    generate_delivery_mechanisms,
)
from extras.test_utils.factories.program import ProgramFactory
from pytz import utc

from hct_mis_api.apps.geo.models import Area
from hct_mis_api.apps.household.models import Household
from hct_mis_api.apps.payment.models import DeliveryMechanism, Payment
from hct_mis_api.apps.payment.services.dashboard_service import (
    payment_verification_chart_query,
)
from hct_mis_api.apps.program.models import Program

pytestmark = pytest.mark.django_db()


class TestPaymentVerificationChartQuery:
    @pytest.fixture(autouse=True)
    def setUp(self) -> None:
        generate_delivery_mechanisms()
        self.dm_cash = DeliveryMechanism.objects.get(code="cash")
        self.dm_voucher = DeliveryMechanism.objects.get(code="voucher")
        PartnerFactory(name="UNICEF")
        fsp = FinancialServiceProviderFactory()

        business_area = create_afghanistan()
        num = 100

        country = CountryFactory(name=business_area.slug.capitalize())
        area_type = AreaTypeFactory(
            name="City",
            country=country,
            area_level=2,
        )
        admin_area1 = AreaFactory(
            name=f"{business_area.slug} city 1", area_type=area_type, p_code=f"{business_area.slug} 1"
        )
        admin_area2 = AreaFactory(
            name=f"{business_area.slug} city 2", area_type=area_type, p_code=f"{business_area.slug} 2"
        )
        admin_area3 = AreaFactory(
            name=f"{business_area.slug} city 3", area_type=area_type, p_code=f"{business_area.slug} 3"
        )

        program = ProgramFactory(
            name="Test Program",
            cash_plus=True,
            start_date=timezone.datetime(2000, 9, 10, tzinfo=utc).date(),
            end_date=timezone.datetime(2099, 10, 10, tzinfo=utc).date(),
        )

        household1, individuals1 = create_household(
            household_args={"size": 2, "business_area": business_area, "admin2": admin_area1, "program": program},
        )
        household2, individuals2 = create_household(
            household_args={"size": 2, "business_area": business_area, "admin2": admin_area2, "program": program},
        )
        household3, individuals3 = create_household(
            household_args={"size": 2, "business_area": business_area, "admin2": admin_area3, "program": program},
        )
        household4, individuals4 = create_household(
            household_args={"size": 2, "business_area": business_area, "admin2": admin_area1, "program": program},
        )
        household5, individuals5 = create_household(
            household_args={"size": 2, "business_area": business_area, "admin2": admin_area2, "program": program},
        )
        household6, individuals6 = create_household(
            household_args={"size": 2, "business_area": business_area, "admin2": admin_area3, "program": program},
        )

        payment_plan1 = PaymentPlanFactory(program_cycle=program.cycles.first(), business_area=business_area)
        PaymentFactory(
            parent=payment_plan1,
            delivery_date=timezone.datetime(2021, 10, 10, tzinfo=utc),
            household=household1,
            delivery_type=self.dm_cash,
            delivered_quantity=10 + num,
            delivered_quantity_usd=10 + num,
            status=Payment.STATUS_SUCCESS,
            business_area=business_area,
            currency="PLN",
        )
        PaymentFactory(
            parent=payment_plan1,
            delivery_date=timezone.datetime(2021, 10, 10, tzinfo=utc),
            household=household2,
            delivery_type=self.dm_voucher,
            delivered_quantity=20 + num,
            delivered_quantity_usd=20 + num,
            status=Payment.STATUS_SUCCESS,
            business_area=business_area,
            currency="PLN",
        )
        PaymentFactory(
            parent=payment_plan1,
            delivery_date=timezone.datetime(2021, 11, 10, tzinfo=utc),
            household=household3,
            delivery_type=self.dm_cash,
            delivered_quantity=30 + num,
            delivered_quantity_usd=30 + num,
            status=Payment.STATUS_ERROR,
            business_area=business_area,
            currency="PLN",
        )

        payment_plan2 = PaymentPlanFactory(program_cycle=program.cycles.first(), business_area=business_area)
        PaymentFactory(
            parent=payment_plan2,
            delivery_date=timezone.datetime(2021, 10, 10, tzinfo=utc),
            delivery_type=self.dm_cash,
            delivered_quantity=10 + num,
            delivered_quantity_usd=10 + num,
            status=Payment.STATUS_SUCCESS,
            business_area=business_area,
            household=household4,
            currency="PLN",
            financial_service_provider=fsp,
        )
        PaymentFactory(
            parent=payment_plan2,
            delivery_date=timezone.datetime(2021, 10, 10, tzinfo=utc),
            delivery_type=self.dm_voucher,
            delivered_quantity=20 + num,
            delivered_quantity_usd=20 + num,
            status=Payment.STATUS_SUCCESS,
            business_area=business_area,
            household=household5,
            currency="PLN",
            financial_service_provider=fsp,
        )
        PaymentFactory(
            parent=payment_plan2,
            delivery_date=timezone.datetime(2021, 11, 10, tzinfo=utc),
            delivery_type=self.dm_cash,
            delivered_quantity=30 + num,
            delivered_quantity_usd=30 + num,
            status=Payment.STATUS_ERROR,
            business_area=business_area,
            household=household6,
            currency="PLN",
            financial_service_provider=fsp,
        )

    def test_payment_verification_chart_query(self) -> None:
        program = Program.objects.get(name="Test Program")
        area = Area.objects.get(name="afghanistan city 1")
        response = payment_verification_chart_query(
            2021,
            "afghanistan",
            Household.CollectType.STANDARD.value,
            program.id,
            area.id,
        )

        assert response == {
            "average_sample_size": 0.0,
            "datasets": [
                {"data": [0], "label": "NOT RECEIVED"},
                {"data": [0], "label": "PENDING"},
                {"data": [0], "label": "RECEIVED"},
                {"data": [0], "label": "RECEIVED WITH ISSUES"},
            ],
            "labels": ["Payment Verification"],
            "number_of_records": 0,
        }
