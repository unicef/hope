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
from hct_mis_api.apps.payment.celery_tasks import (
    periodic_sync_payment_gateway_delivery_mechanisms,
)
from hct_mis_api.apps.payment.fixtures import (
    DeliveryMechanismDataFactory,
    DeliveryMechanismPerPaymentPlanFactory,
    FinancialServiceProviderFactory,
    PaymentFactory,
    PaymentPlanFactory,
    generate_delivery_mechanisms,
)
from hct_mis_api.apps.payment.models import (
    DeliveryMechanism,
    FinancialServiceProvider,
    Payment,
    PaymentHouseholdSnapshot,
    PaymentPlan,
    PaymentPlanSplit,
)
from hct_mis_api.apps.payment.services.payment_gateway import (
    AddRecordsResponseData,
    DeliveryMechanismData,
    DeliveryMechanismDataRequirements,
    FspData,
    PaymentGatewayAPI,
    PaymentGatewayService,
    PaymentInstructionStatus,
    PaymentRecordData,
)
from hct_mis_api.apps.payment.services.payment_household_snapshot_service import (
    create_payment_plan_snapshot_data,
)


@pytest.fixture(autouse=True)
def mock_payment_gateway_env_vars() -> None:
    with mock.patch.dict(os.environ, {"PAYMENT_GATEWAY_API_KEY": "TEST", "PAYMENT_GATEWAY_API_URL": "TEST"}):
        yield


class TestPaymentGatewayService(APITestCase):
    databases = ("default",)

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        create_afghanistan()
        generate_delivery_mechanisms()
        cls.dm_cash_over_the_counter = DeliveryMechanism.objects.get(code="cash_over_the_counter")
        cls.dm_transfer = DeliveryMechanism.objects.get(code="transfer")
        cls.dm_mobile_money = DeliveryMechanism.objects.get(code="mobile_money")
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")
        cls.user = UserFactory.create()

        cls.pp = PaymentPlanFactory(
            program__cycle__start_date=timezone.datetime(2021, 6, 10, tzinfo=utc).date(),
            program__cycle__end_date=timezone.datetime(2021, 7, 10, tzinfo=utc).date(),
            status=PaymentPlan.Status.ACCEPTED,
        )
        cls.pg_fsp = FinancialServiceProviderFactory(
            name="Western Union",
            communication_channel=FinancialServiceProvider.COMMUNICATION_CHANNEL_API,
            payment_gateway_id="123",
        )
        cls.pg_fsp.delivery_mechanisms.add(cls.dm_cash_over_the_counter)
        cls.dm = DeliveryMechanismPerPaymentPlanFactory(
            payment_plan=cls.pp,
            financial_service_provider=cls.pg_fsp,
            delivery_mechanism=cls.dm_cash_over_the_counter,
            sent_to_payment_gateway=False,
        )
        cls.payments = []
        for _ in range(2):
            collector = IndividualFactory(
                household=None,
                flex_fields={
                    "service_provider_code_i_f": "123456789",
                },
            )
            hh = HouseholdFactory(head_of_household=collector)
            collector.household = hh
            collector.save()
            IndividualRoleInHouseholdFactory(household=hh, individual=collector, role=ROLE_PRIMARY)
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

        create_payment_plan_snapshot_data(cls.pp)

    @mock.patch("hct_mis_api.apps.payment.models.PaymentPlan.get_exchange_rate", return_value=2.0)
    @mock.patch(
        "hct_mis_api.apps.payment.services.payment_gateway.PaymentGatewayAPI.get_records_for_payment_instruction"
    )
    @mock.patch("hct_mis_api.apps.payment.services.payment_gateway.get_quantity_in_usd", return_value=100.00)
    def test_sync_records_for_split(
        self, get_quantity_in_usd_mock: Any, get_records_for_payment_instruction_mock: Any, get_exchange_rate_mock: Any
    ) -> None:
        self.dm.sent_to_payment_gateway = True
        self.dm.save()

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
    def test_sync_records(self, get_records_for_payment_instruction_mock: Any, get_exchange_rate_mock: Any) -> None:
        for _ in range(2):
            collector = IndividualFactory(household=None)
            hoh = IndividualFactory(household=None)
            hh = HouseholdFactory(head_of_household=hoh)
            IndividualRoleInHouseholdFactory(household=hh, individual=hoh, role=ROLE_PRIMARY)
            IndividualFactory.create_batch(2, household=hh)
            self.payments.append(
                PaymentFactory(
                    parent=self.pp,
                    household=hh,
                    status=Payment.STATUS_PENDING,
                    currency="PLN",
                    collector=collector,
                    delivered_quantity=None,
                    delivered_quantity_usd=None,
                    financial_service_provider=self.pg_fsp,
                )
            )

        self.dm.sent_to_payment_gateway = True
        self.dm.save()

        get_records_for_payment_instruction_mock.return_value = [
            PaymentRecordData(
                id=1,
                remote_id=str(self.payments[0].id),
                created="2023-10-10",
                modified="2023-10-11",
                record_code="1",
                parent="1",
                status="ERROR",
                auth_code="1",
                fsp_code="1",
                message="Error",
            ),
            PaymentRecordData(
                id=2,
                remote_id=str(self.payments[1].id),
                created="2023-10-10",
                modified="2023-10-11",
                record_code="2",
                parent="2",
                status="ERROR",
                auth_code="2",
                fsp_code="2",
                payout_amount=1.23,
            ),
            PaymentRecordData(
                id=3,
                remote_id=str(self.payments[2].id),
                created="2023-10-10",
                modified="2023-10-11",
                record_code="3",
                parent="3",
                status="CANCELLED",
                auth_code="3",
                fsp_code="3",
            ),
            PaymentRecordData(
                id=4,
                remote_id=str(self.payments[3].id),
                created="2023-10-10",
                modified="2023-10-11",
                record_code="4",
                parent="4",
                status="REFUND",
                auth_code="4",
                fsp_code="4",
            ),
        ]

        pg_service = PaymentGatewayService()
        pg_service.api.get_records_for_payment_instruction = get_records_for_payment_instruction_mock  # type: ignore

        pg_service.sync_records()
        assert get_records_for_payment_instruction_mock.call_count == 1
        self.pp.refresh_from_db()
        self.payments[0].refresh_from_db()
        self.payments[1].refresh_from_db()
        self.payments[2].refresh_from_db()
        self.payments[3].refresh_from_db()
        assert self.payments[0].status == Payment.STATUS_ERROR
        assert self.payments[1].status == Payment.STATUS_ERROR
        assert self.payments[2].status == Payment.STATUS_MANUALLY_CANCELLED
        assert self.payments[3].status == Payment.STATUS_NOT_DISTRIBUTED
        assert self.payments[3].delivered_quantity == Decimal(0.0)
        assert self.payments[3].delivered_quantity_usd == Decimal(0.0)
        assert self.payments[3].status == Payment.STATUS_NOT_DISTRIBUTED
        assert self.payments[0].reason_for_unsuccessful_payment == "Error"
        assert self.payments[1].reason_for_unsuccessful_payment == "Delivered amount: 1.23"
        assert self.payments[2].reason_for_unsuccessful_payment == "Unknown error"
        assert self.pp.is_reconciled

    @mock.patch("hct_mis_api.apps.payment.models.PaymentPlan.get_exchange_rate", return_value=2.0)
    @mock.patch(
        "hct_mis_api.apps.payment.services.payment_gateway.PaymentGatewayAPI.get_records_for_payment_instruction"
    )
    @mock.patch("hct_mis_api.apps.payment.services.payment_gateway.get_quantity_in_usd", return_value=100.00)
    def test_sync_records_error_messages(
        self, get_quantity_in_usd_mock: Any, get_records_for_payment_instruction_mock: Any, get_exchange_rate_mock: Any
    ) -> None:
        self.dm.sent_to_payment_gateway = True
        self.dm.save()

        get_records_for_payment_instruction_mock.return_value = [
            PaymentRecordData(
                id=1,
                remote_id=str(self.payments[0].id),
                created="2023-10-10",
                modified="2023-10-11",
                record_code="1",
                parent="1",
                status="PENDING",
                auth_code="1",
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
        self.pp.refresh_from_db()
        self.payments[0].refresh_from_db()
        self.payments[1].refresh_from_db()
        assert self.payments[0].status == Payment.STATUS_SENT_TO_PG
        assert self.payments[0].fsp_auth_code == "1"
        assert self.payments[0].delivered_quantity is None
        assert self.payments[1].status == Payment.STATUS_DISTRIBUTION_PARTIAL
        assert self.payments[1].fsp_auth_code == "2"
        assert self.payments[1].delivered_quantity == self.payments[1].entitlement_quantity - Decimal(10.00)
        assert self.pp.is_reconciled is False

        get_records_for_payment_instruction_mock.return_value = [
            PaymentRecordData(
                id=1,
                remote_id=str(self.payments[0].id),
                created="2023-10-10",
                modified="2023-10-11",
                record_code="1",
                parent="1",
                status="TRANSFERRED_TO_BENEFICIARY",
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
                auth_code="2",
                payout_amount=float(self.payments[1].entitlement_quantity) - 10.00,
                fsp_code="2",
            ),
        ]

        get_records_for_payment_instruction_mock.reset_mock()
        pg_service.sync_records()
        assert get_records_for_payment_instruction_mock.call_count == 1
        self.payments[0].refresh_from_db()
        self.payments[1].refresh_from_db()
        assert self.payments[0].status == Payment.STATUS_DISTRIBUTION_SUCCESS
        assert self.payments[0].delivered_quantity == self.payments[0].entitlement_quantity
        assert self.payments[1].status == Payment.STATUS_DISTRIBUTION_PARTIAL
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
            auth_code="1",
            payout_amount=float(self.payments[0].entitlement_quantity),
            fsp_code="1",
        )
        self.assertEqual(p.get_hope_status(self.payments[0].entitlement_quantity), Payment.STATUS_DISTRIBUTION_SUCCESS)
        self.assertEqual(p.get_hope_status(Decimal(1000000.00)), Payment.STATUS_DISTRIBUTION_PARTIAL)

        p.payout_amount = None
        self.assertEqual(p.get_hope_status(Decimal(1000000.00)), Payment.STATUS_ERROR)

        p.payout_amount = float(self.payments[0].entitlement_quantity)
        p.status = "NOT EXISTING STATUS"
        self.assertEqual(p.get_hope_status(Decimal(1000000.00)), Payment.STATUS_ERROR)

    @mock.patch(
        "hct_mis_api.apps.payment.services.payment_gateway.PaymentGatewayAPI.add_records_to_payment_instruction"
    )
    @mock.patch("hct_mis_api.apps.payment.services.payment_gateway.PaymentGatewayAPI.change_payment_instruction_status")
    def test_add_records_to_payment_instructions_for_split(
        self, change_payment_instruction_status_mock: Any, add_records_to_payment_instruction_mock: Any
    ) -> None:
        pp_split_1 = PaymentPlanSplit.objects.create(
            payment_plan=self.pp,
            split_type=PaymentPlanSplit.SplitType.BY_COLLECTOR,
            chunks_no=1,
            order=0,
            sent_to_payment_gateway=False,
        )
        pp_split_2 = PaymentPlanSplit.objects.create(
            payment_plan=self.pp,
            split_type=PaymentPlanSplit.SplitType.BY_COLLECTOR,
            chunks_no=1,
            order=1,
            sent_to_payment_gateway=False,
        )
        pp_split_1.payments.add(self.payments[0])
        pp_split_2.payments.add(self.payments[1])
        add_records_to_payment_instruction_mock.return_value = AddRecordsResponseData(
            remote_id="1",
            records={"1": self.payments[0].id, "2": self.payments[1].id},
            errors=None,
        )

        change_payment_instruction_status_mock.side_effect = [
            PaymentInstructionStatus.CLOSED.value,
            PaymentInstructionStatus.READY.value,
            PaymentInstructionStatus.CLOSED.value,
            PaymentInstructionStatus.READY.value,
        ]
        pg_service = PaymentGatewayService()
        pg_service.api.add_records_to_payment_instruction_mock = add_records_to_payment_instruction_mock
        pg_service.add_records_to_payment_instructions(self.pp)

        pp_split_1.refresh_from_db()
        pp_split_2.refresh_from_db()
        self.payments[0].refresh_from_db()
        self.payments[1].refresh_from_db()

        self.assertEqual(pp_split_1.sent_to_payment_gateway, True)
        self.assertEqual(pp_split_2.sent_to_payment_gateway, True)
        self.assertEqual(change_payment_instruction_status_mock.call_count, 4)
        self.assertEqual(self.payments[0].status, Payment.STATUS_SENT_TO_PG)
        self.assertEqual(self.payments[1].status, Payment.STATUS_SENT_TO_PG)

    @mock.patch(
        "hct_mis_api.apps.payment.services.payment_gateway.PaymentGatewayAPI.add_records_to_payment_instruction"
    )
    def test_add_records_to_payment_instructions_for_split_error(
        self, add_records_to_payment_instruction_mock: Any
    ) -> None:
        pp_split_1 = PaymentPlanSplit.objects.create(
            payment_plan=self.pp,
            split_type=PaymentPlanSplit.SplitType.BY_COLLECTOR,
            chunks_no=1,
            order=0,
            sent_to_payment_gateway=False,
        )
        pp_split_2 = PaymentPlanSplit.objects.create(
            payment_plan=self.pp,
            split_type=PaymentPlanSplit.SplitType.BY_COLLECTOR,
            chunks_no=1,
            order=1,
            sent_to_payment_gateway=False,
        )
        pp_split_1.payments.add(self.payments[0])
        pp_split_2.payments.add(self.payments[1])
        add_records_to_payment_instruction_mock.return_value = AddRecordsResponseData(
            remote_id="1",
            records=None,
            errors={"0": "Error", "1": "Error"},
        )
        pg_service = PaymentGatewayService()
        pg_service.api.add_records_to_payment_instruction_mock = add_records_to_payment_instruction_mock
        pg_service.add_records_to_payment_instructions(self.pp)

        pp_split_1.refresh_from_db()
        pp_split_2.refresh_from_db()
        self.payments[0].refresh_from_db()
        self.payments[1].refresh_from_db()

        self.assertEqual(pp_split_1.sent_to_payment_gateway, False)
        self.assertEqual(pp_split_2.sent_to_payment_gateway, False)
        self.assertEqual(self.payments[0].status, Payment.STATUS_ERROR)
        self.assertEqual(self.payments[1].status, Payment.STATUS_ERROR)
        self.assertEqual(self.payments[0].reason_for_unsuccessful_payment, "Error")
        self.assertEqual(self.payments[1].reason_for_unsuccessful_payment, "Error")

    @mock.patch(
        "hct_mis_api.apps.payment.services.payment_gateway.PaymentGatewayAPI.add_records_to_payment_instruction"
    )
    @mock.patch("hct_mis_api.apps.payment.services.payment_gateway.PaymentGatewayAPI.change_payment_instruction_status")
    def test_add_records_to_payment_instructions(
        self, change_payment_instruction_status_mock: Any, add_records_to_payment_instruction_mock: Any
    ) -> None:
        add_records_to_payment_instruction_mock.return_value = AddRecordsResponseData(
            remote_id="1",
            records={"1": self.payments[0].id, "2": self.payments[1].id},
            errors=None,
        )
        change_payment_instruction_status_mock.side_effect = [
            PaymentInstructionStatus.CLOSED.value,
            PaymentInstructionStatus.READY.value,
        ]
        pg_service = PaymentGatewayService()
        pg_service.api.add_records_to_payment_instruction_mock = add_records_to_payment_instruction_mock
        pg_service.add_records_to_payment_instructions(self.pp)

        self.pp.refresh_from_db()
        self.payments[0].refresh_from_db()
        self.payments[1].refresh_from_db()

        self.assertEqual(self.pp.delivery_mechanisms.first().sent_to_payment_gateway, True)
        self.assertEqual(change_payment_instruction_status_mock.call_count, 2)
        self.assertEqual(self.payments[0].status, Payment.STATUS_SENT_TO_PG)
        self.assertEqual(self.payments[1].status, Payment.STATUS_SENT_TO_PG)

    @mock.patch(
        "hct_mis_api.apps.payment.services.payment_gateway.PaymentGatewayAPI.add_records_to_payment_instruction"
    )
    def test_add_records_to_payment_instructions_error(self, add_records_to_payment_instruction_mock: Any) -> None:
        add_records_to_payment_instruction_mock.return_value = AddRecordsResponseData(
            remote_id="1",
            records=None,
            errors={"0": "Error", "1": "Error"},
        )
        pg_service = PaymentGatewayService()
        pg_service.api.add_records_to_payment_instruction_mock = add_records_to_payment_instruction_mock
        pg_service.add_records_to_payment_instructions(self.pp)

        self.payments[0].refresh_from_db()
        self.payments[1].refresh_from_db()

        self.assertEqual(self.pp.delivery_mechanisms.first().sent_to_payment_gateway, False)
        self.assertEqual(self.payments[0].status, Payment.STATUS_ERROR)
        self.assertEqual(self.payments[1].status, Payment.STATUS_ERROR)
        self.assertEqual(self.payments[0].reason_for_unsuccessful_payment, "Error")
        self.assertEqual(self.payments[1].reason_for_unsuccessful_payment, "Error")

    @mock.patch("hct_mis_api.apps.payment.services.payment_gateway.PaymentGatewayAPI._post")
    def test_api_add_records_to_payment_instruction(self, post_mock: Any) -> None:
        post_mock.return_value = {
            "remote_id": "123",
            "records": {
                "1": self.payments[0].id,
            },
            "errors": None,
        }, 200

        self.dm.delivery_mechanism = self.dm_cash_over_the_counter
        self.dm.save()
        PaymentGatewayAPI().add_records_to_payment_instruction([self.payments[0]], "123")
        post_mock.assert_called_once_with(
            "payment_instructions/123/add_records/",
            [
                {
                    "remote_id": str(self.payments[0].id),
                    "record_code": self.payments[0].unicef_id,
                    "payload": {
                        "amount": str(self.payments[0].entitlement_quantity),
                        "phone_no": str(self.payments[0].collector.phone_no),
                        "last_name": self.payments[0].collector.family_name,
                        "first_name": self.payments[0].collector.given_name,
                        "full_name": self.payments[0].collector.full_name,
                        "destination_currency": self.payments[0].currency,
                    },
                    "extra_data": {},
                }
            ],
            validate_response=True,
        )

        post_mock.reset_mock()
        self.payments[0].delivery_type = self.dm_mobile_money
        self.payments[0].save()
        PaymentGatewayAPI().add_records_to_payment_instruction([self.payments[0]], "123")
        post_mock.assert_called_once_with(
            "payment_instructions/123/add_records/",
            [
                {
                    "remote_id": str(self.payments[0].id),
                    "record_code": self.payments[0].unicef_id,
                    "payload": {
                        "amount": str(self.payments[0].entitlement_quantity),
                        "phone_no": str(self.payments[0].collector.phone_no),
                        "last_name": self.payments[0].collector.family_name,
                        "first_name": self.payments[0].collector.given_name,
                        "full_name": self.payments[0].collector.full_name,
                        "destination_currency": self.payments[0].currency,
                        "service_provider_code": self.payments[0].collector.flex_fields["service_provider_code_i_f"],
                    },
                    "extra_data": {},
                }
            ],
            validate_response=True,
        )

    @mock.patch("hct_mis_api.apps.payment.services.payment_gateway.PaymentGatewayAPI._post")
    def test_api_add_records_to_payment_instruction_wallet_integration(self, post_mock: Any) -> None:
        post_mock.return_value = {
            "remote_id": "123",
            "records": {
                "1": self.payments[0].id,
            },
            "errors": None,
        }, 200

        primary_collector = self.payments[0].collector

        DeliveryMechanismDataFactory(
            individual=primary_collector,
            delivery_mechanism=self.dm_mobile_money,
            data={
                "service_provider_code__mobile_money": "ABC",
                "delivery_phone_number__mobile_money": "123456789",
                "provider__mobile_money": "Provider",
            },
        )
        self.payments[0].delivery_type = self.dm_mobile_money
        self.payments[0].save()

        # remove old and create new snapshot
        PaymentHouseholdSnapshot.objects.all().delete()
        self.assertEqual(PaymentHouseholdSnapshot.objects.count(), 0)
        self.assertEqual(Payment.objects.count(), 2)

        create_payment_plan_snapshot_data(self.payments[0].parent)
        self.assertEqual(PaymentHouseholdSnapshot.objects.count(), 2)
        self.payments[0].refresh_from_db()

        PaymentGatewayAPI().add_records_to_payment_instruction([self.payments[0]], "123")
        post_mock.assert_called_once_with(
            "payment_instructions/123/add_records/",
            [
                {
                    "remote_id": str(self.payments[0].id),
                    "record_code": self.payments[0].unicef_id,
                    "payload": {
                        "amount": str(self.payments[0].entitlement_quantity),
                        "phone_no": str(primary_collector.phone_no),
                        "last_name": primary_collector.family_name,
                        "first_name": primary_collector.given_name,
                        "full_name": primary_collector.full_name,
                        "destination_currency": self.payments[0].currency,
                        "service_provider_code__mobile_money": "ABC",
                        "delivery_phone_number__mobile_money": "123456789",
                        "provider__mobile_money": "Provider",
                    },
                    "extra_data": {},
                }
            ],
            validate_response=True,
        )

    @mock.patch("hct_mis_api.apps.payment.services.payment_gateway.PaymentGatewayAPI._post")
    def test_api_add_records_to_payment_instruction_validation_error(self, post_mock: Any) -> None:
        payment = self.payments[0]
        payment.entitlement_quantity = None
        payment.collector.flex_fields = {}
        payment.save()
        payment.collector.save()
        with self.assertRaisesMessage(
            PaymentGatewayAPI.PaymentGatewayAPIException,
            "{'amount': [ErrorDetail(string='This field may not be null.', code='null')]}",
        ):
            PaymentGatewayAPI().add_records_to_payment_instruction([payment], "123")

    @mock.patch("hct_mis_api.apps.payment.services.payment_gateway.PaymentGatewayAPI.get_delivery_mechanisms")
    def test_sync_delivery_mechanisms(self, get_delivery_mechanisms_mock: Any) -> None:
        assert DeliveryMechanism.objects.all().count() == 16

        dm_cash = DeliveryMechanism.objects.get(code="cash")
        dm_cash.is_active = False
        dm_cash.save()

        get_delivery_mechanisms_mock.return_value = [
            DeliveryMechanismData(
                id=33,
                code="new_dm",
                name="New DM",
                requirements=DeliveryMechanismDataRequirements(
                    required_fields=["required_field"],
                    optional_fields=[
                        "full_name",
                    ],
                    unique_fields=[],
                ),
                transfer_type="CASH",
            ),
            DeliveryMechanismData(
                id=2,
                code="cash",
                name="Cash",
                requirements=DeliveryMechanismDataRequirements(
                    required_fields=["new_required_field"],
                    optional_fields=[
                        "full_name",
                        "new_optional_field",
                    ],
                    unique_fields=["new_unique_field"],
                ),
                transfer_type="CASH",
            ),
        ]

        pg_service = PaymentGatewayService()
        pg_service.api.get_delivery_mechanisms = get_delivery_mechanisms_mock  # type: ignore

        pg_service.sync_delivery_mechanisms()
        dm_cash = DeliveryMechanism.objects.get(code="cash")
        assert dm_cash.is_active
        assert dm_cash.required_fields == ["new_required_field"]
        assert dm_cash.optional_fields == ["full_name", "new_optional_field"]
        assert dm_cash.unique_fields == ["new_unique_field"]

        dm_new = DeliveryMechanism.objects.get(code="new_dm")
        assert dm_new.is_active

    @mock.patch("hct_mis_api.apps.payment.services.payment_gateway.PaymentGatewayAPI.get_fsps")
    def test_sync_fsps(self, get_fsps_mock: Any) -> None:
        assert FinancialServiceProvider.objects.all().count() == 1

        assert self.pg_fsp.name == "Western Union"
        assert self.pg_fsp.payment_gateway_id == "123"
        assert list(self.pg_fsp.delivery_mechanisms.values_list("code", flat=True)) == ["cash_over_the_counter"]

        self.dm_cash_over_the_counter.payment_gateway_id = "555"
        self.dm_cash_over_the_counter.save()
        self.dm_transfer.payment_gateway_id = "666"
        self.dm_transfer.save()

        get_fsps_mock.return_value = [
            FspData(
                id=33,
                remote_id="33",
                name="New FSP",
                vision_vendor_number="33",
                configs=[
                    {
                        "id": 21,
                        "key": "key21",
                        "delivery_mechanism": self.dm_cash_over_the_counter.payment_gateway_id,
                        "delivery_mechanism_name": self.dm_cash_over_the_counter.name,
                        "label": "label21",
                    },
                    {
                        "id": 22,
                        "key": "key22",
                        "delivery_mechanism": self.dm_transfer.payment_gateway_id,
                        "delivery_mechanism_name": self.dm_transfer.name,
                        "label": "label22",
                    },
                ],
            ),
            FspData(
                id=123,
                remote_id="123",
                name="Western Union",
                vision_vendor_number="123",
                configs=[
                    {
                        "id": 23,
                        "key": "key23",
                        "delivery_mechanism": self.dm_transfer.payment_gateway_id,
                        "delivery_mechanism_name": self.dm_transfer.name,
                        "label": "label23",
                    },
                ],
            ),
        ]

        pg_service = PaymentGatewayService()
        pg_service.api.get_fsps = get_fsps_mock  # type: ignore

        pg_service.sync_fsps()

        self.pg_fsp.refresh_from_db()
        assert self.pg_fsp.name == "Western Union"
        assert self.pg_fsp.payment_gateway_id == "123"
        assert list(self.pg_fsp.delivery_mechanisms.values_list("code", flat=True)) == ["transfer"]  # updated

        fsp_new = FinancialServiceProvider.objects.get(name="New FSP")
        assert fsp_new.payment_gateway_id == "33"
        assert list(fsp_new.delivery_mechanisms.values_list("code", flat=True)) == ["cash_over_the_counter", "transfer"]

    @mock.patch("hct_mis_api.apps.payment.services.payment_gateway.PaymentGatewayService.sync_delivery_mechanisms")
    def test_periodic_sync_payment_gateway_delivery_mechanisms(self, sync_delivery_mechanisms_mock: Any) -> None:
        periodic_sync_payment_gateway_delivery_mechanisms()
        assert sync_delivery_mechanisms_mock.call_count == 1
