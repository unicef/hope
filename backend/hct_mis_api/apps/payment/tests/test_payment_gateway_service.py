import os
from decimal import Decimal
from typing import Any
from unittest import mock

from django.utils import timezone

import pytest
from pytz import utc

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.household.fixtures import (
    HouseholdFactory,
    IndividualFactory,
    IndividualRoleInHouseholdFactory,
)
from hct_mis_api.apps.household.models import ROLE_PRIMARY
from hct_mis_api.apps.payment.delivery_mechanisms import DeliveryMechanismChoices
from hct_mis_api.apps.payment.fixtures import (
    DeliveryMechanismPerPaymentPlanFactory,
    FinancialServiceProviderFactory,
    PaymentFactory,
    PaymentPlanFactory,
)
from hct_mis_api.apps.payment.models import (
    FinancialServiceProvider,
    Payment,
    PaymentPlan,
    PaymentPlanSplit,
)
from hct_mis_api.apps.payment.services.payment_gateway import (
    PaymentGatewayAPI,
    PaymentGatewayService,
    PaymentRecordData,
)


@pytest.fixture(autouse=True)
def mock_payment_gateway_env_vars() -> None:
    with mock.patch.dict(os.environ, {"PAYMENT_GATEWAY_API_KEY": "TEST", "PAYMENT_GATEWAY_API_URL": "TEST"}):
        yield


class TestPaymentGatewayService(APITestCase):
    databases = ("default",)

    @classmethod
    def setUpTestData(cls) -> None:
        create_afghanistan()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")
        cls.user = UserFactory.create()

        cls.pp = PaymentPlanFactory(
            start_date=timezone.datetime(2021, 6, 10, tzinfo=utc),
            end_date=timezone.datetime(2021, 7, 10, tzinfo=utc),
            status=PaymentPlan.Status.ACCEPTED,
        )
        cls.pg_fsp = FinancialServiceProviderFactory(
            name="Western Union",
            delivery_mechanisms=[
                DeliveryMechanismChoices.DELIVERY_TYPE_CASH_OVER_THE_COUNTER,
            ],
            communication_channel=FinancialServiceProvider.COMMUNICATION_CHANNEL_API,
            payment_gateway_id="123",
        )
        cls.dm = DeliveryMechanismPerPaymentPlanFactory(
            payment_plan=cls.pp,
            financial_service_provider=cls.pg_fsp,
            delivery_mechanism=DeliveryMechanismChoices.DELIVERY_TYPE_CASH_OVER_THE_COUNTER,
            sent_to_payment_gateway=True,
        )
        cls.payments = []
        for _ in range(2):
            collector = IndividualFactory(household=None)
            hoh = IndividualFactory(household=None)
            hh = HouseholdFactory(head_of_household=hoh)
            IndividualRoleInHouseholdFactory(household=hh, individual=hoh, role=ROLE_PRIMARY)
            IndividualFactory.create_batch(2, household=hh)
            cls.payments.append(
                PaymentFactory(
                    parent=cls.pp,
                    household=hh,
                    status=Payment.STATUS_PENDING,
                    currency="PLN",
                    collector=collector,
                    delivered_quantity=None,
                    delivered_quantity_usd=None,
                    financial_service_provider=cls.pg_fsp,
                )
            )

    @mock.patch("hct_mis_api.apps.payment.models.PaymentPlan.get_exchange_rate", return_value=2.0)
    @mock.patch(
        "hct_mis_api.apps.payment.services.payment_gateway.PaymentGatewayAPI.get_records_for_payment_instruction"
    )
    @mock.patch("hct_mis_api.apps.payment.services.payment_gateway.get_quantity_in_usd", return_value=100.00)
    def test_sync_records_for_split(
        self, get_quantity_in_usd_mock: Any, get_records_for_payment_instruction_mock: Any, get_exchange_rate_mock: Any
    ) -> None:
        pp_split_1 = PaymentPlanSplit.objects.create(
            payment_plan=self.pp,
            split_type=PaymentPlanSplit.SplitType.BY_COLLECTOR,
            chunks_no=1,
            order=0,
            sent_to_payment_gateway=True,
        )
        pp_split_2 = PaymentPlanSplit.objects.create(
            payment_plan=self.pp,
            split_type=PaymentPlanSplit.SplitType.BY_COLLECTOR,
            chunks_no=1,
            order=1,
            sent_to_payment_gateway=True,
        )
        pp_split_1.payments.add(self.payments[0])
        pp_split_2.payments.add(self.payments[1])

        get_records_for_payment_instruction_mock.return_value = [
            PaymentRecordData(
                id=1,
                remote_id=str(self.payments[0].id),
                created="2023-10-10",
                modified="2023-10-11",
                record_code="1",
                parent="1",
                status="TRANSFERRED_TO_BENEFICIARY",
                hope_status=Payment.STATUS_DISTRIBUTION_SUCCESS,
                auth_code="1",
                payout_amount=float(self.payments[0].entitlement_quantity),
                fsp_code="1",
            ),
        ]

        pg_service = PaymentGatewayService()
        pg_service.api.get_records_for_payment_instruction = get_records_for_payment_instruction_mock  # type: ignore

        pg_service.sync_records()
        assert get_records_for_payment_instruction_mock.call_count == 2
        self.payments[0].refresh_from_db()
        assert self.payments[0].status == Payment.STATUS_DISTRIBUTION_SUCCESS
        assert self.payments[0].fsp_auth_code == "1"
        assert self.payments[0].delivered_quantity == self.payments[0].entitlement_quantity
        assert self.payments[0].delivered_quantity_usd == 100.0

        get_records_for_payment_instruction_mock.return_value = [
            PaymentRecordData(
                id=2,
                remote_id=str(self.payments[1].id),
                created="2023-10-10",
                modified="2023-10-11",
                record_code="2",
                parent="2",
                status="ERROR",
                hope_status=Payment.STATUS_ERROR,
                auth_code="2",
                payout_amount=0.0,
                fsp_code="2",
                message="Error",
            ),
        ]

        get_records_for_payment_instruction_mock.reset_mock()
        pg_service.sync_records()
        assert get_records_for_payment_instruction_mock.call_count == 1  # only for the second split/payment
        self.payments[1].refresh_from_db()
        assert self.payments[1].status == Payment.STATUS_ERROR
        assert self.payments[1].fsp_auth_code == "2"
        assert self.payments[1].delivered_quantity is None
        assert self.payments[1].reason_for_unsuccessful_payment == "Error"

        # pp is reconciled at this point
        get_records_for_payment_instruction_mock.reset_mock()
        pg_service.sync_records()
        assert get_records_for_payment_instruction_mock.call_count == 0

    @mock.patch("hct_mis_api.apps.payment.models.PaymentPlan.get_exchange_rate", return_value=2.0)
    @mock.patch(
        "hct_mis_api.apps.payment.services.payment_gateway.PaymentGatewayAPI.get_records_for_payment_instruction"
    )
    @mock.patch("hct_mis_api.apps.payment.services.payment_gateway.get_quantity_in_usd", return_value=100.00)
    def test_sync_records(
        self, get_quantity_in_usd_mock: Any, get_records_for_payment_instruction_mock: Any, get_exchange_rate_mock: Any
    ) -> None:
        get_records_for_payment_instruction_mock.return_value = [
            PaymentRecordData(
                id=1,
                remote_id=str(self.payments[0].id),
                created="2023-10-10",
                modified="2023-10-11",
                record_code="1",
                parent="1",
                status="TRANSFERRED_TO_BENEFICIARY",
                hope_status=Payment.STATUS_DISTRIBUTION_SUCCESS,
                auth_code="1",
                payout_amount=float(self.payments[0].entitlement_quantity),
                fsp_code="1",
            ),
            PaymentRecordData(
                id=2,
                remote_id=str(self.payments[1].id),
                created="2023-10-10",
                modified="2023-10-11",
                record_code="2",
                parent="2",
                status="TRANSFERRED_TO_BENEFICIARY",
                hope_status=Payment.STATUS_DISTRIBUTION_SUCCESS,
                auth_code="2",
                payout_amount=float(self.payments[1].entitlement_quantity) - 10.00,
                fsp_code="2",
            ),
        ]

        pg_service = PaymentGatewayService()
        pg_service.api.get_records_for_payment_instruction = get_records_for_payment_instruction_mock  # type: ignore

        assert self.pp.splits.exists() is False
        assert self.pp.is_reconciled is False

        pg_service.sync_records()
        assert get_records_for_payment_instruction_mock.call_count == 1
        self.payments[0].refresh_from_db()
        self.payments[1].refresh_from_db()
        assert self.payments[0].status == Payment.STATUS_DISTRIBUTION_SUCCESS
        assert self.payments[0].fsp_auth_code == "1"
        assert self.payments[0].delivered_quantity == self.payments[0].entitlement_quantity
        assert self.payments[1].status == Payment.STATUS_DISTRIBUTION_PARTIAL
        assert self.payments[1].fsp_auth_code == "2"
        assert self.payments[1].delivered_quantity == self.payments[1].entitlement_quantity - Decimal(10.00)

        # pp is reconciled at this point
        get_records_for_payment_instruction_mock.reset_mock()
        pg_service.sync_records()
        assert get_records_for_payment_instruction_mock.call_count == 0

    def test_get_hope_status(self) -> None:
        p = PaymentRecordData(
            id=1,
            remote_id=str(self.payments[0].id),
            created="2023-10-10",
            modified="2023-10-11",
            record_code="1",
            parent="1",
            status="TRANSFERRED_TO_BENEFICIARY",
            hope_status=Payment.STATUS_DISTRIBUTION_SUCCESS,
            auth_code="1",
            payout_amount=float(self.payments[0].entitlement_quantity),
            fsp_code="1",
        )
        self.assertEqual(p.get_hope_status(self.payments[0].entitlement_quantity), Payment.STATUS_DISTRIBUTION_SUCCESS)
        self.assertEqual(p.get_hope_status(Decimal(1000000.00)), Payment.STATUS_DISTRIBUTION_PARTIAL)

        with self.assertRaisesMessage(PaymentGatewayAPI.PaymentGatewayAPIException, "Invalid delivered_quantity"):
            p.payout_amount = None
            p.get_hope_status(Decimal(1000000.00))

        with self.assertRaisesMessage(PaymentGatewayAPI.PaymentGatewayAPIException, "Invalid Payment status"):
            p.payout_amount = float(self.payments[0].entitlement_quantity)
            p.status = "NOT EXISTING STATUS"
            p.get_hope_status(Decimal(1000000.00))
