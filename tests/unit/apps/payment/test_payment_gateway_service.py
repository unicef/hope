from decimal import Decimal
import json
import os
from typing import Any
from unittest import mock
from unittest.mock import Mock, patch

import pytest

from extras.test_utils.factories.account import UserFactory
from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.household import (
    HouseholdFactory,
    IndividualFactory,
    IndividualRoleInHouseholdFactory,
)
from extras.test_utils.factories.payment import (
    AccountFactory,
    FinancialServiceProviderFactory,
    PaymentFactory,
    PaymentPlanFactory,
    generate_delivery_mechanisms,
)
from hope.apps.core.base_test_case import BaseTestCase
from hope.apps.payment.celery_tasks import (
    periodic_sync_payment_gateway_delivery_mechanisms,
)
from hope.apps.payment.services.payment_gateway import (
    AccountTypeData,
    AddRecordsResponseData,
    DeliveryMechanismData,
    FspData,
    PaymentGatewayAPI,
    PaymentGatewayService,
    PaymentInstructionData,
    PaymentInstructionStatus,
    PaymentRecordData,
)
from hope.apps.payment.services.payment_household_snapshot_service import (
    create_payment_plan_snapshot_data,
)
from hope.models.account_type import AccountType
from hope.models.business_area import BusinessArea
from hope.models.delivery_mechanism import DeliveryMechanism
from hope.models.financial_institution import FinancialInstitution
from hope.models.financial_institution_mapping import FinancialInstitutionMapping
from hope.models.financial_service_provider import FinancialServiceProvider
from hope.models.fsp_name_mapping import FspNameMapping
from hope.models.household import ROLE_PRIMARY
from hope.models.payment import Payment
from hope.models.payment_household_snapshot import PaymentHouseholdSnapshot
from hope.models.payment_plan import PaymentPlan
from hope.models.payment_plan_split import PaymentPlanSplit


@pytest.fixture(autouse=True)
def mock_payment_gateway_env_vars() -> None:
    with mock.patch.dict(
        os.environ,
        {"PAYMENT_GATEWAY_API_KEY": "TEST", "PAYMENT_GATEWAY_API_URL": "TEST"},
    ):
        yield


def normalize(data: Any) -> dict:
    return json.loads(json.dumps(data))


class TestPaymentGatewayService(BaseTestCase):
    databases = ("default",)

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        create_afghanistan()
        cls.pg_fsp = FinancialServiceProviderFactory(
            name="Western Union",
            communication_channel=FinancialServiceProvider.COMMUNICATION_CHANNEL_API,
            payment_gateway_id="123",
        )
        generate_delivery_mechanisms()
        cls.dm_cash_over_the_counter = DeliveryMechanism.objects.get(code="cash_over_the_counter")
        cls.dm_transfer = DeliveryMechanism.objects.get(code="transfer")
        cls.dm_mobile_money = DeliveryMechanism.objects.get(code="mobile_money")
        cls.dm_transfer_to_account = DeliveryMechanism.objects.get(code="transfer_to_account")
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")
        cls.user = UserFactory.create()
        cls.pg_fsp.delivery_mechanisms.add(cls.dm_cash_over_the_counter)

        cls.pp = PaymentPlanFactory(
            status=PaymentPlan.Status.ACCEPTED,
            created_by=cls.user,
            financial_service_provider=cls.pg_fsp,
            delivery_mechanism=cls.dm_cash_over_the_counter,
        )
        cls.pp_split_1 = PaymentPlanSplit.objects.create(
            payment_plan=cls.pp,
            split_type=PaymentPlanSplit.SplitType.BY_COLLECTOR,
            chunks_no=1,
            order=0,
            sent_to_payment_gateway=False,
        )
        cls.pp_split_2 = PaymentPlanSplit.objects.create(
            payment_plan=cls.pp,
            split_type=PaymentPlanSplit.SplitType.BY_COLLECTOR,
            chunks_no=1,
            order=1,
            sent_to_payment_gateway=False,
        )
        collector1 = IndividualFactory(
            household=None,
            flex_fields={
                "service_provider_code_i_f": "123456789",
            },
        )
        hh1 = HouseholdFactory(head_of_household=collector1)
        collector1.household = hh1
        collector1.save()
        IndividualRoleInHouseholdFactory(household=hh1, individual=collector1, role=ROLE_PRIMARY)
        IndividualFactory.create_batch(2, household=hh1)

        collector2 = IndividualFactory(
            household=None,
            flex_fields={
                "service_provider_code_i_f": "123456789",
            },
        )
        hh2 = HouseholdFactory(head_of_household=collector2)
        collector2.household = hh2
        collector2.save()
        IndividualRoleInHouseholdFactory(household=hh2, individual=collector2, role=ROLE_PRIMARY)
        IndividualFactory.create_batch(2, household=hh2)
        cls.payments = [
            PaymentFactory(
                parent=cls.pp,
                parent_split=cls.pp_split_1,
                household=hh1,
                status=Payment.STATUS_PENDING,
                currency="PLN",
                collector=collector1,
                delivered_quantity=None,
                delivered_quantity_usd=None,
                financial_service_provider=cls.pg_fsp,
                delivery_type=cls.dm_transfer,
            ),
            PaymentFactory(
                parent=cls.pp,
                parent_split=cls.pp_split_2,
                household=hh2,
                status=Payment.STATUS_PENDING,
                currency="PLN",
                collector=collector2,
                delivered_quantity=None,
                delivered_quantity_usd=None,
                financial_service_provider=cls.pg_fsp,
                delivery_type=cls.dm_transfer,
            ),
        ]
        create_payment_plan_snapshot_data(cls.pp)

    @mock.patch(
        "hope.apps.payment.services.payment_gateway.PaymentGatewayAPI.change_payment_instruction_status",
        return_value="FINALIZED",
    )
    @mock.patch("hope.apps.payment.models.PaymentPlan.get_exchange_rate", return_value=2.0)
    @mock.patch("hope.apps.payment.services.payment_gateway.PaymentGatewayAPI.get_records_for_payment_instruction")
    @mock.patch(
        "hope.apps.payment.services.payment_gateway.get_quantity_in_usd",
        return_value=100.00,
    )
    def test_sync_records_for_split(
        self,
        get_quantity_in_usd_mock: Any,
        get_records_for_payment_instruction_mock: Any,
        get_exchange_rate_mock: Any,
        change_payment_instruction_status_mock: Any,
    ) -> None:
        self.pp_split_1.sent_to_payment_gateway = True
        self.pp_split_2.sent_to_payment_gateway = True
        self.pp_split_1.save()
        self.pp_split_2.save()

        get_records_for_payment_instruction_mock.side_effect = [
            [
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
            ],
            [
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
            ],
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

        self.payments[1].refresh_from_db()
        assert self.payments[1].status == Payment.STATUS_ERROR
        assert self.payments[1].fsp_auth_code == "2"
        assert self.payments[1].delivered_quantity is None
        assert self.payments[1].reason_for_unsuccessful_payment == "Error"

        # pp is reconciled at this point
        get_records_for_payment_instruction_mock.reset_mock()
        pg_service.sync_records()
        assert get_records_for_payment_instruction_mock.call_count == 0

        assert change_payment_instruction_status_mock.call_count == 2
        self.pp.refresh_from_db()
        assert self.pp.status == PaymentPlan.Status.FINISHED

    @mock.patch(
        "hope.apps.payment.services.payment_gateway.PaymentGatewayAPI.change_payment_instruction_status",
        return_value="FINALIZED",
    )
    @mock.patch("hope.apps.payment.models.PaymentPlan.get_exchange_rate", return_value=2.0)
    @mock.patch("hope.apps.payment.services.payment_gateway.PaymentGatewayAPI.get_records_for_payment_instruction")
    @mock.patch(
        "hope.apps.payment.services.payment_gateway.get_quantity_in_usd",
        return_value=100.00,
    )
    def test_sync_records_error_messages(
        self,
        get_quantity_in_usd_mock: Any,
        get_records_for_payment_instruction_mock: Any,
        get_exchange_rate_mock: Any,
        change_payment_instruction_status_mock: Any,
    ) -> None:
        self.pp_split_1.sent_to_payment_gateway = True
        self.pp_split_2.sent_to_payment_gateway = True
        self.pp_split_1.save()
        self.pp_split_2.save()

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

        assert self.pp.splits.exists() is True
        assert self.pp.is_reconciled is False

        pg_service.sync_records()
        assert get_records_for_payment_instruction_mock.call_count == 2
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
        assert change_payment_instruction_status_mock.call_count == 0

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
        assert change_payment_instruction_status_mock.call_count == 2

    @mock.patch(
        "hope.apps.payment.services.payment_gateway.PaymentGatewayAPI.change_payment_instruction_status",
        return_value="FINALIZED",
    )
    @mock.patch("hope.apps.payment.models.PaymentPlan.get_exchange_rate", return_value=2.0)
    @mock.patch("hope.apps.payment.services.payment_gateway.PaymentGatewayAPI.get_records_for_payment_instruction")
    @mock.patch(
        "hope.apps.payment.services.payment_gateway.get_quantity_in_usd",
        return_value=100.00,
    )
    def test_sync_payment_plan(
        self,
        get_quantity_in_usd_mock: Any,
        get_records_for_payment_instruction_mock: Any,
        get_exchange_rate_mock: Any,
        change_payment_instruction_status_mock: Any,
    ) -> None:
        self.pp_split_1.sent_to_payment_gateway = True
        self.pp_split_2.sent_to_payment_gateway = True
        self.pp_split_1.save()
        self.pp_split_2.save()

        self.payments[0].status = Payment.STATUS_ERROR
        self.payments[1].status = Payment.STATUS_DISTRIBUTION_SUCCESS
        self.payments[0].save()
        self.payments[1].save()

        get_records_for_payment_instruction_mock.side_effect = [
            [
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
                )
            ],
            [
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
            ],
        ]

        pg_service = PaymentGatewayService()
        pg_service.api.get_records_for_payment_instruction = get_records_for_payment_instruction_mock  # type: ignore

        pg_service.sync_payment_plan(self.pp)
        assert get_records_for_payment_instruction_mock.call_count == 2
        self.payments[0].refresh_from_db()
        assert self.payments[0].status == Payment.STATUS_DISTRIBUTION_SUCCESS
        assert self.payments[0].fsp_auth_code == "1"
        assert self.payments[0].delivered_quantity == self.payments[0].entitlement_quantity
        assert self.payments[0].delivered_quantity_usd == 100.0

        self.payments[1].refresh_from_db()
        assert self.payments[1].status == Payment.STATUS_ERROR
        assert self.payments[1].fsp_auth_code == "2"
        assert self.payments[1].delivered_quantity is None
        assert self.payments[1].reason_for_unsuccessful_payment == "Error"

        self.pp.refresh_from_db()
        assert self.pp.status == PaymentPlan.Status.FINISHED

    @mock.patch("hope.apps.payment.models.PaymentPlan.get_exchange_rate", return_value=2.0)
    @mock.patch("hope.apps.payment.services.payment_gateway.PaymentGatewayAPI.get_record")
    @mock.patch(
        "hope.apps.payment.services.payment_gateway.get_quantity_in_usd",
        return_value=100.00,
    )
    def test_sync_record(
        self,
        get_quantity_in_usd_mock: Any,
        get_record_mock: Any,
        get_exchange_rate_mock: Any,
    ) -> None:
        self.payments[0].status = Payment.STATUS_ERROR
        self.payments[0].save()

        get_record_mock.side_effect = [
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
            )
        ]

        pg_service = PaymentGatewayService()
        pg_service.api.get_record = get_record_mock  # type: ignore

        pg_service.sync_record(self.payments[0])
        assert get_record_mock.call_count == 1
        self.payments[0].refresh_from_db()
        assert self.payments[0].status == Payment.STATUS_DISTRIBUTION_SUCCESS
        assert self.payments[0].fsp_auth_code == "1"
        assert self.payments[0].delivered_quantity == self.payments[0].entitlement_quantity
        assert self.payments[0].delivered_quantity_usd == 100.0

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
        assert p.get_hope_status(self.payments[0].entitlement_quantity) == Payment.STATUS_DISTRIBUTION_SUCCESS
        assert p.get_hope_status(Decimal(1000000.00)) == Payment.STATUS_DISTRIBUTION_PARTIAL

        p.payout_amount = None
        assert p.get_hope_status(Decimal(1000000.00)) == Payment.STATUS_ERROR

        p.payout_amount = float(self.payments[0].entitlement_quantity)
        p.status = "NOT EXISTING STATUS"
        assert p.get_hope_status(Decimal(1000000.00)) == Payment.STATUS_ERROR

    @mock.patch("hope.apps.payment.services.payment_gateway.PaymentGatewayAPI.add_records_to_payment_instruction")
    @mock.patch("hope.apps.payment.services.payment_gateway.PaymentGatewayAPI.change_payment_instruction_status")
    def test_add_records_to_payment_instructions_for_split(
        self,
        change_payment_instruction_status_mock: Any,
        add_records_to_payment_instruction_mock: Any,
    ) -> None:
        self.pp_split_1.sent_to_payment_gateway = False
        self.pp_split_2.sent_to_payment_gateway = False
        self.pp_split_1.save()
        self.pp_split_2.save()

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
            PaymentInstructionStatus.FINALIZED.value,
            PaymentInstructionStatus.FINALIZED.value,
        ]
        pg_service = PaymentGatewayService()
        pg_service.api.add_records_to_payment_instruction_mock = add_records_to_payment_instruction_mock
        pg_service.add_records_to_payment_instructions(self.pp)

        self.pp_split_1.refresh_from_db()
        self.pp_split_2.refresh_from_db()
        self.payments[0].refresh_from_db()
        self.payments[1].refresh_from_db()

        assert self.pp_split_1.sent_to_payment_gateway
        assert self.pp_split_2.sent_to_payment_gateway
        assert change_payment_instruction_status_mock.call_count == 4
        assert self.payments[0].status == Payment.STATUS_SENT_TO_PG
        assert self.payments[1].status == Payment.STATUS_SENT_TO_PG

    @mock.patch("hope.apps.payment.services.payment_gateway.PaymentGatewayAPI.add_records_to_payment_instruction")
    @mock.patch("hope.apps.payment.services.payment_gateway.PaymentGatewayAPI.change_payment_instruction_status")
    def test_add_records_to_payment_instructions_for_split_error(
        self,
        change_payment_instruction_status_mock: Any,
        add_records_to_payment_instruction_mock: Any,
    ) -> None:
        self.pp_split_1.sent_to_payment_gateway = False
        self.pp_split_2.sent_to_payment_gateway = False
        self.pp_split_1.save()
        self.pp_split_2.save()

        change_payment_instruction_status_mock.side_effect = [
            PaymentInstructionStatus.CLOSED.value,
            PaymentInstructionStatus.READY.value,
            PaymentInstructionStatus.CLOSED.value,
            PaymentInstructionStatus.READY.value,
        ]

        add_records_to_payment_instruction_mock.return_value = AddRecordsResponseData(
            remote_id="1",
            records=None,
            errors={"0": "Error", "1": "Error"},
        )
        pg_service = PaymentGatewayService()
        pg_service.api.add_records_to_payment_instruction_mock = add_records_to_payment_instruction_mock
        pg_service.add_records_to_payment_instructions(self.pp)

        self.pp_split_1.refresh_from_db()
        self.pp_split_2.refresh_from_db()
        self.payments[0].refresh_from_db()
        self.payments[1].refresh_from_db()

        assert self.pp_split_1.sent_to_payment_gateway is False
        assert self.pp_split_2.sent_to_payment_gateway is False
        assert self.payments[0].status == Payment.STATUS_ERROR
        assert self.payments[1].status == Payment.STATUS_ERROR
        assert self.payments[0].reason_for_unsuccessful_payment == "Error"
        assert self.payments[1].reason_for_unsuccessful_payment == "Error"

    @mock.patch("hope.apps.payment.services.payment_gateway.PaymentGatewayAPI._post")
    def test_api_add_records_to_payment_instruction(self, post_mock: Any) -> None:
        post_mock.return_value = (
            {
                "remote_id": "123",
                "records": {
                    "1": self.payments[0].id,
                },
                "errors": None,
            },
            200,
        )

        self.pp.delivery_mechanism = self.dm_cash_over_the_counter
        self.pp.save()
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
                        "middle_name": self.payments[0].collector.middle_name,
                        "first_name": self.payments[0].collector.given_name,
                        "full_name": self.payments[0].collector.full_name,
                        "destination_currency": self.payments[0].currency,
                        "delivery_mechanism": "transfer",
                        "account_type": "bank",
                    },
                    "extra_data": self.payments[0].household_snapshot.snapshot_data,
                }
            ],
            validate_response=True,
        )

    @mock.patch("hope.apps.payment.services.payment_gateway.PaymentGatewayAPI._post")
    def test_api_add_records_to_payment_instruction_wallet_integration_mobile(self, post_mock: Any) -> None:
        post_mock.return_value = (
            {
                "remote_id": "123",
                "records": {
                    "1": self.payments[0].id,
                },
                "errors": None,
            },
            200,
        )

        primary_collector = self.payments[0].collector
        fi = FinancialInstitution.objects.create(type=FinancialInstitution.FinancialInstitutionType.TELCO, name="ABC")
        AccountFactory(
            individual=primary_collector,
            data={
                "number": "123456789",
                "provider": "Provider",
                "service_provider_code": "CBA",
            },
            account_type=AccountType.objects.get(key="mobile"),
            financial_institution=fi,
        )
        self.payments[0].delivery_type = self.dm_mobile_money
        self.payments[0].save()

        # remove old and create new snapshot
        PaymentHouseholdSnapshot.objects.all().delete()
        assert PaymentHouseholdSnapshot.objects.count() == 0
        assert Payment.objects.count() == 2

        create_payment_plan_snapshot_data(self.payments[0].parent)
        assert PaymentHouseholdSnapshot.objects.count() == 2
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
                        "middle_name": primary_collector.middle_name,
                        "first_name": primary_collector.given_name,
                        "full_name": primary_collector.full_name,
                        "destination_currency": self.payments[0].currency,
                        "delivery_mechanism": "mobile_money",
                        "account_type": "mobile",
                        "account": {
                            "service_provider_code": "CBA",
                            "number": "123456789",
                            "provider": "Provider",
                            "financial_institution": str(fi.id),
                        },
                    },
                    "extra_data": self.payments[0].household_snapshot.snapshot_data,
                }
            ],
            validate_response=True,
        )

    @mock.patch("hope.apps.payment.services.payment_gateway.PaymentGatewayAPI._post")
    def test_api_add_records_to_payment_instruction_wallet_integration_bank(self, post_mock: Any) -> None:
        uba_fsp = FinancialServiceProvider.objects.get(name="United Bank for Africa - Nigeria")

        post_mock.return_value = (
            {
                "remote_id": "123",
                "records": {
                    "1": self.payments[0].id,
                },
                "errors": None,
            },
            200,
        )

        primary_collector = self.payments[0].collector

        AccountFactory(
            number="123",
            individual=primary_collector,
            account_type=self.dm_transfer_to_account.account_type,
            data={
                "number": "123",
                "name": "ABC",
                "code": "456",
            },
        )
        self.payments[0].delivery_type = self.dm_transfer_to_account
        self.payments[0].save()

        # remove old and create new snapshot
        PaymentHouseholdSnapshot.objects.all().delete()
        assert PaymentHouseholdSnapshot.objects.count() == 0
        assert Payment.objects.count() == 2

        create_payment_plan_snapshot_data(self.payments[0].parent)
        assert PaymentHouseholdSnapshot.objects.count() == 2
        self.payments[0].refresh_from_db()

        # no mapping, different payment fsp
        with self.assertRaisesMessage(
            Exception,
            f"No Financial Institution Mapping found for"
            f" financial_institution_code 456,"
            f" fsp {self.payments[0].financial_service_provider},"
            f" payment {self.payments[0].id},"
            f" collector {self.payments[0].collector}.",
        ):
            PaymentGatewayAPI().add_records_to_payment_instruction([self.payments[0]], "123")
            post_mock.reset_mock()

        # no mapping, payment fsp is uba
        self.payments[0].financial_service_provider = uba_fsp
        self.payments[0].save()
        PaymentHouseholdSnapshot.objects.all().delete()
        create_payment_plan_snapshot_data(self.payments[0].parent)
        self.payments[0].refresh_from_db()
        self.payments[0].collector.refresh_from_db()
        self.payments[0].household_snapshot.refresh_from_db()

        expected_payload = {
            "amount": str(self.payments[0].entitlement_quantity),
            "phone_no": str(primary_collector.phone_no),
            "last_name": primary_collector.family_name,
            "middle_name": primary_collector.middle_name,
            "first_name": primary_collector.given_name,
            "full_name": primary_collector.full_name,
            "destination_currency": self.payments[0].currency,
            "delivery_mechanism": "transfer_to_account",
            "account_type": "bank",
            "account": {
                "number": "123",
                "name": "ABC",
                "code": "456",
                "service_provider_code": "456",
            },
        }
        expected_body = {
            "remote_id": str(self.payments[0].id),
            "record_code": self.payments[0].unicef_id,
            "payload": expected_payload,
            "extra_data": self.payments[0].household_snapshot.snapshot_data,
        }
        PaymentGatewayAPI().add_records_to_payment_instruction([self.payments[0]], "123")
        actual_args, actual_kwargs = post_mock.call_args
        assert actual_args[0] == "payment_instructions/123/add_records/"
        assert normalize(actual_args[1][0]) == normalize(expected_body)
        assert actual_kwargs["validate_response"] is True

        post_mock.reset_mock()

        # mapping exists, payment fsp is not uba, remap to correct code
        self.payments[0].financial_service_provider = self.pg_fsp
        self.payments[0].save()

        financial_institution = FinancialInstitution.objects.create(
            name="BANK1",
            type=FinancialInstitution.FinancialInstitutionType.BANK,
        )
        FinancialInstitutionMapping.objects.create(
            financial_institution=financial_institution,
            financial_service_provider=uba_fsp,
            code="456",
        )
        FinancialInstitutionMapping.objects.create(
            financial_institution=financial_institution,
            financial_service_provider=self.pg_fsp,
            code="789",
        )

        PaymentHouseholdSnapshot.objects.all().delete()
        create_payment_plan_snapshot_data(self.payments[0].parent)
        self.payments[0].refresh_from_db()
        self.payments[0].collector.refresh_from_db()
        self.payments[0].household_snapshot.refresh_from_db()
        for account in self.payments[0].collector.accounts.all():
            account.refresh_from_db()

        PaymentGatewayAPI().add_records_to_payment_instruction([self.payments[0]], "123")
        expected_payload["account"]["code"] = "456"
        expected_payload["account"]["service_provider_code"] = "789"
        # update 'extra_data' with new snapshot_data
        expected_body["extra_data"] = self.payments[0].household_snapshot.snapshot_data

        actual_args, actual_kwargs = post_mock.call_args
        assert actual_args[0] == "payment_instructions/123/add_records/"
        assert normalize(actual_args[1][0]) == normalize(expected_body)
        assert actual_kwargs["validate_response"] is True
        post_mock.reset_mock()

    @mock.patch("hope.apps.payment.services.payment_gateway.PaymentGatewayAPI._post")
    def test_api_add_records_to_payment_instruction_validation_error(self, post_mock: Any) -> None:
        payment = self.payments[0]
        payment.entitlement_quantity = None
        payment.collector.flex_fields = {}
        payment.save()
        payment.collector.save()
        with self.assertRaisesMessage(
            PaymentGatewayAPI.PaymentGatewayAPIError,
            "{'amount': [ErrorDetail(string='This field may not be null.', code='null')]}",
        ):
            PaymentGatewayAPI().add_records_to_payment_instruction([payment], "123")

    @mock.patch("hope.apps.payment.services.payment_gateway.PaymentGatewayAPI._post")
    def test_api_add_records_to_payment_instruction_no_snapshot(self, post_mock: Any) -> None:
        payment = self.payments[0]
        payment.household_snapshot.delete()
        payment.refresh_from_db()

        post_mock.return_value = (
            {
                "remote_id": "123",
                "records": {
                    "1": payment.id,
                },
                "errors": None,
            },
            200,
        )

        with self.assertRaisesMessage(
            PaymentGatewayAPI.PaymentGatewayAPIError,
            f"Not found snapshot for Payment {payment.unicef_id}",
        ):
            PaymentGatewayAPI().add_records_to_payment_instruction([payment], "123")

    @mock.patch("hope.apps.payment.services.payment_gateway.PaymentGatewayAPI._get")
    def test_api_get_fsps(self, get_mock: Any) -> None:
        get_mock.return_value = (
            [
                {
                    "id": "123",
                    "remote_id": "123",
                    "name": "123",
                    "vendor_number": "123",
                    "configs": [
                        {
                            "id": "123",
                            "key": "123",
                            "delivery_mechanism": "123",
                            "delivery_mechanism_name": "123",
                            "label": "123",
                            "required_fields": ["123", "123"],
                        }
                    ],
                }
            ],
            200,
        )

        response_data = PaymentGatewayAPI().get_fsps()
        assert isinstance(response_data[0], FspData)

    @mock.patch("hope.apps.payment.services.payment_gateway.PaymentGatewayAPI._get")
    def test_api_get_account_types(self, get_mock: Any) -> None:
        get_mock.return_value = (
            [
                {
                    "id": "123",
                    "key": "123",
                    "label": "123",
                    "unique_fields": ["123"],
                }
            ],
            200,
        )

        response_data = PaymentGatewayAPI().get_account_types()
        assert isinstance(response_data[0], AccountTypeData)

    @mock.patch("hope.apps.payment.services.payment_gateway.PaymentGatewayAPI._post")
    def test_api_create_payment_instruction(self, post_mock: Any) -> None:
        post_mock.return_value = (
            {
                "remote_id": "123",
                "external_code": "123",
                "status": "123",
                "fsp": "123",
                "system": "123",
                "payload": "123",
            },
            200,
        )

        response_data = PaymentGatewayAPI().create_payment_instruction({})
        assert isinstance(response_data, PaymentInstructionData)

    @mock.patch("hope.apps.payment.services.payment_gateway.PaymentGatewayAPI._get")
    def test_api_get_record(self, get_mock: Any) -> None:
        get_mock.return_value = (
            [
                {
                    "id": "123",
                    "remote_id": "123",
                    "created": "123",
                    "modified": "123",
                    "parent": "123",
                    "status": "PENDING",
                    "auth_code": "123",
                    "record_code": "123",
                    "fsp_code": "123",
                }
            ],
            200,
        )

        response_data = PaymentGatewayAPI().get_record("123")
        assert isinstance(response_data, PaymentRecordData)

    @mock.patch("hope.apps.payment.services.payment_gateway.PaymentGatewayAPI._post")
    def test_api_change_payment_instruction_status(self, post_mock: Any) -> None:
        s = Mock()
        bad_status = "bad_status"
        s.value = bad_status
        with pytest.raises(
            PaymentGatewayAPI.PaymentGatewayAPIError, match="Can't set invalid Payment Instruction status:"
        ):
            PaymentGatewayAPI().change_payment_instruction_status(
                s,
                "123",
            )

        post_mock.return_value = {"status": "ABORTED"}, 200
        response = PaymentGatewayAPI().change_payment_instruction_status(
            PaymentInstructionStatus.ABORTED,
            "123",
        )
        assert response == "ABORTED"

    @mock.patch("hope.apps.payment.services.payment_gateway.PaymentGatewayAPI.get_delivery_mechanisms")
    def test_sync_delivery_mechanisms(self, get_delivery_mechanisms_mock: Any) -> None:
        assert DeliveryMechanism.objects.all().count() == 14

        dm_cash = DeliveryMechanism.objects.get(code="cash")
        dm_cash.is_active = False
        dm_cash.payment_gateway_id = 2
        dm_cash.save()

        get_delivery_mechanisms_mock.return_value = [
            DeliveryMechanismData(
                id=33,
                code="new_dm",
                name="New DM",
                transfer_type="CASH",
                account_type="123",
            ),
            DeliveryMechanismData(id=2, code="cash", name="Cash", transfer_type="CASH", account_type="123"),
        ]

        pg_service = PaymentGatewayService()
        pg_service.api.get_delivery_mechanisms = get_delivery_mechanisms_mock  # type: ignore

        pg_service.sync_delivery_mechanisms()
        dm_cash = DeliveryMechanism.objects.get(code="cash")
        assert dm_cash.is_active
        assert dm_cash.account_type.key == "bank"

        dm_new = DeliveryMechanism.objects.get(code="new_dm")
        assert dm_new.is_active
        assert dm_new.payment_gateway_id == "33"

    @mock.patch("hope.apps.payment.services.payment_gateway.PaymentGatewayAPI.get_fsps")
    def test_sync_fsps(self, get_fsps_mock: Any) -> None:
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
                vendor_number="33",
                configs=[
                    {
                        "id": 21,
                        "key": "key21",
                        "delivery_mechanism": self.dm_cash_over_the_counter.payment_gateway_id,
                        "delivery_mechanism_name": self.dm_cash_over_the_counter.code,
                        "label": "label21",
                        "required_fields": ["field1", "field2"],
                    },
                    {
                        "id": 22,
                        "key": "key22",
                        "delivery_mechanism": self.dm_transfer.payment_gateway_id,
                        "delivery_mechanism_name": self.dm_transfer.code,
                        "label": "label22",
                        "required_fields": ["field3", "field4"],
                    },
                ],
            ),
            FspData(
                id=123,
                remote_id="123",
                name="Western Union",
                vendor_number="123",
                configs=[
                    {
                        "id": 23,
                        "key": "key23",
                        "delivery_mechanism": self.dm_transfer.payment_gateway_id,
                        "delivery_mechanism_name": self.dm_transfer.code,
                        "label": "label23",
                        "required_fields": ["field3", "field4"],
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
        assert list(fsp_new.delivery_mechanisms.values_list("code", flat=True)) == [
            "cash_over_the_counter",
            "transfer",
        ]

        assert FspNameMapping.objects.count() == 6
        fsp_name_mapping = FspNameMapping.objects.get(external_name="field1")
        assert fsp_name_mapping.fsp == fsp_new
        assert fsp_name_mapping.hope_name == "field1"
        assert fsp_name_mapping.source == FspNameMapping.SourceModel.ACCOUNT

    @mock.patch("hope.apps.payment.services.payment_gateway.PaymentGatewayService.sync_delivery_mechanisms")
    def test_periodic_sync_payment_gateway_delivery_mechanisms(self, sync_delivery_mechanisms_mock: Any) -> None:
        periodic_sync_payment_gateway_delivery_mechanisms()
        assert sync_delivery_mechanisms_mock.call_count == 1

    @mock.patch("hope.apps.payment.services.payment_gateway.PaymentGatewayAPI.get_record")
    @mock.patch("hope.apps.payment.services.payment_gateway.PaymentGatewayAPI.add_records_to_payment_instruction")
    @mock.patch("hope.apps.payment.services.payment_gateway.PaymentGatewayAPI.change_payment_instruction_status")
    def test_add_missing_records_to_payment_instructions(
        self,
        get_record_mock: Any,
        add_records_to_payment_instruction_mock: Any,
        change_payment_instruction_status_mock: Any,
    ) -> None:
        get_record_mock.side_effect = [
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
            None,  # second Record not in PG
        ]
        pg_service = PaymentGatewayService()
        pg_service.api.get_record = get_record_mock  # type: ignore
        change_payment_instruction_status_mock.side_effect = [
            PaymentInstructionStatus.CLOSED.value,
            PaymentInstructionStatus.READY.value,
        ]
        add_records_to_payment_instruction_mock.return_value = AddRecordsResponseData(
            remote_id="1",
            records=None,
            errors={"0": "Error", "1": "Error"},
        )

        with patch.object(pg_service.api, "add_records_to_payment_instruction") as mock_add_records:
            pg_service.api.add_records_to_payment_instruction_mock = add_records_to_payment_instruction_mock

            pg_service.add_missing_records_to_payment_instructions(self.pp)
            # got one payment not in PaymentGateway -> self.payments[1]
            assert get_record_mock.call_count == 2

            # check call arguments
            called_payments, called_split = (
                mock_add_records.call_args[0][0],
                mock_add_records.call_args[0][1],
            )
            assert called_payments == list(Payment.objects.filter(pk=self.payments[1].pk))
            assert called_split == self.pp_split_2.pk
