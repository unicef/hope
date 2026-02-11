from decimal import Decimal
import json
import os
import re
from typing import Any
from unittest import mock
from unittest.mock import Mock, patch

import pytest

from extras.test_utils.factories.account import UserFactory
from extras.test_utils.factories.geo import CountryFactory
from extras.test_utils.factories.household import HouseholdFactory, IndividualFactory
from extras.test_utils.factories.payment import (
    AccountFactory,
    AccountTypeFactory,
    DeliveryMechanismFactory,
    FinancialServiceProviderFactory,
    PaymentFactory,
    PaymentPlanFactory,
    PaymentPlanSplitFactory,
)
from extras.test_utils.factories.program import ProgramCycleFactory
from hope.apps.payment.celery_tasks import periodic_sync_payment_gateway_delivery_mechanisms
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
    PaymentSerializer,
)
from hope.apps.payment.services.payment_household_snapshot_service import create_payment_plan_snapshot_data
from hope.models import (
    DeliveryMechanism,
    FinancialInstitution,
    FinancialInstitutionMapping,
    FinancialServiceProvider,
    FspNameMapping,
    Payment,
    PaymentHouseholdSnapshot,
    PaymentPlan,
    PaymentPlanSplit,
)
from hope.models.utils import MergeStatusModel

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def mock_payment_gateway_env_vars() -> None:
    with mock.patch.dict(
        os.environ,
        {"PAYMENT_GATEWAY_API_KEY": "TEST", "PAYMENT_GATEWAY_API_URL": "TEST"},
    ):
        yield


def normalize(data: Any) -> dict:
    return json.loads(json.dumps(data))


@pytest.fixture
def user():
    return UserFactory()


@pytest.fixture
def program_cycle():
    return ProgramCycleFactory()


@pytest.fixture
def account_types():
    bank = AccountTypeFactory(key="bank", label="Bank", payment_gateway_id="123")
    mobile = AccountTypeFactory(key="mobile", label="Mobile", payment_gateway_id="456")
    return {"bank": bank, "mobile": mobile}


@pytest.fixture
def delivery_mechanisms(account_types):
    dm_cash_over_the_counter = DeliveryMechanismFactory(
        code="cash_over_the_counter",
        name="Cash OTC",
        payment_gateway_id="555",
    )
    dm_transfer = DeliveryMechanismFactory(
        code="transfer",
        name="Transfer",
        payment_gateway_id="666",
        account_type=account_types["bank"],
    )
    dm_mobile_money = DeliveryMechanismFactory(
        code="mobile_money",
        name="Mobile Money",
        payment_gateway_id="777",
        account_type=account_types["mobile"],
    )
    dm_transfer_to_account = DeliveryMechanismFactory(
        code="transfer_to_account",
        name="Transfer to Account",
        payment_gateway_id="888",
        account_type=account_types["bank"],
    )
    dm_cash = DeliveryMechanismFactory(
        code="cash",
        name="Cash",
        payment_gateway_id="2",
    )
    return {
        "cash_over_the_counter": dm_cash_over_the_counter,
        "transfer": dm_transfer,
        "mobile_money": dm_mobile_money,
        "transfer_to_account": dm_transfer_to_account,
        "cash": dm_cash,
    }


@pytest.fixture
def pg_fsp(delivery_mechanisms):
    fsp = FinancialServiceProviderFactory(
        name="Western Union",
        communication_channel=FinancialServiceProvider.COMMUNICATION_CHANNEL_API,
        payment_gateway_id="123",
    )
    fsp.delivery_mechanisms.add(delivery_mechanisms["cash_over_the_counter"])
    return fsp


@pytest.fixture
def uba_fsp():
    return FinancialServiceProviderFactory(
        name="United Bank for Africa - Nigeria",
        communication_channel=FinancialServiceProvider.COMMUNICATION_CHANNEL_API,
        payment_gateway_id="999",
    )


@pytest.fixture
def payment_plan(user, program_cycle, pg_fsp, delivery_mechanisms):
    return PaymentPlanFactory(
        status=PaymentPlan.Status.ACCEPTED,
        created_by=user,
        financial_service_provider=pg_fsp,
        delivery_mechanism=delivery_mechanisms["cash_over_the_counter"],
        program_cycle=program_cycle,
        exchange_rate=Decimal("2.0"),
    )


@pytest.fixture
def payment_plan_splits(payment_plan):
    split_1 = PaymentPlanSplitFactory(
        payment_plan=payment_plan,
        split_type=PaymentPlanSplit.SplitType.BY_COLLECTOR,
        chunks_no=1,
        order=0,
        sent_to_payment_gateway=False,
    )
    split_2 = PaymentPlanSplitFactory(
        payment_plan=payment_plan,
        split_type=PaymentPlanSplit.SplitType.BY_COLLECTOR,
        chunks_no=1,
        order=1,
        sent_to_payment_gateway=False,
    )
    return [split_1, split_2]


@pytest.fixture
def collectors_and_households(program_cycle):
    program = program_cycle.program
    collectors = []
    households = []
    for _ in range(2):
        collector = IndividualFactory(
            household=None,
            program=program,
            flex_fields={
                "service_provider_code_i_f": "123456789",
            },
        )
        household = HouseholdFactory(
            head_of_household=collector,
            program=program,
            registration_data_import=collector.registration_data_import,
        )
        IndividualFactory.create_batch(
            2,
            household=household,
            program=program,
            registration_data_import=household.registration_data_import,
        )
        collectors.append(collector)
        households.append(household)
    return {"collectors": collectors, "households": households}


@pytest.fixture
def payment_gateway_setup(
    payment_plan,
    payment_plan_splits,
    collectors_and_households,
    delivery_mechanisms,
    pg_fsp,
):
    split_1, split_2 = payment_plan_splits
    collector_1, collector_2 = collectors_and_households["collectors"]
    household_1, household_2 = collectors_and_households["households"]

    payments = [
        PaymentFactory(
            parent=payment_plan,
            parent_split=split_1,
            household=household_1,
            status=Payment.STATUS_PENDING,
            currency="PLN",
            collector=collector_1,
            head_of_household=household_1.head_of_household,
            delivered_quantity=None,
            delivered_quantity_usd=None,
            financial_service_provider=pg_fsp,
            delivery_type=delivery_mechanisms["transfer"],
            entitlement_quantity=Decimal("100.00"),
            entitlement_quantity_usd=Decimal("50.00"),
        ),
        PaymentFactory(
            parent=payment_plan,
            parent_split=split_2,
            household=household_2,
            status=Payment.STATUS_PENDING,
            currency="PLN",
            collector=collector_2,
            head_of_household=household_2.head_of_household,
            delivered_quantity=None,
            delivered_quantity_usd=None,
            financial_service_provider=pg_fsp,
            delivery_type=delivery_mechanisms["transfer"],
            entitlement_quantity=Decimal("100.00"),
            entitlement_quantity_usd=Decimal("50.00"),
        ),
    ]

    create_payment_plan_snapshot_data(payment_plan)
    for payment in payments:
        payment.refresh_from_db()

    return {
        "payment_plan": payment_plan,
        "splits": payment_plan_splits,
        "payments": payments,
        "fsp": pg_fsp,
        "delivery_mechanisms": delivery_mechanisms,
        "collectors": collectors_and_households["collectors"],
        "households": collectors_and_households["households"],
    }


@mock.patch(
    "hope.apps.payment.services.payment_gateway.PaymentGatewayAPI.change_payment_instruction_status",
    return_value="FINALIZED",
)
@mock.patch("hope.models.payment_plan.PaymentPlan.get_exchange_rate", return_value=2.0)
@mock.patch("hope.apps.payment.services.payment_gateway.PaymentGatewayAPI.get_records_for_payment_instruction")
@mock.patch(
    "hope.apps.payment.services.payment_gateway.get_quantity_in_usd",
    return_value=100.00,
)
def test_sync_records_for_split(
    get_quantity_in_usd_mock: Any,
    get_records_for_payment_instruction_mock: Any,
    get_exchange_rate_mock: Any,
    change_payment_instruction_status_mock: Any,
    payment_gateway_setup: dict,
) -> None:
    split_1, split_2 = payment_gateway_setup["splits"]
    payments = payment_gateway_setup["payments"]
    payment_plan = payment_gateway_setup["payment_plan"]

    split_1.sent_to_payment_gateway = True
    split_2.sent_to_payment_gateway = True
    split_1.save()
    split_2.save()

    get_records_for_payment_instruction_mock.side_effect = [
        [
            PaymentRecordData(
                id=1,
                remote_id=str(payments[0].id),
                created="2023-10-10",
                modified="2023-10-11",
                record_code="1",
                parent="1",
                status="TRANSFERRED_TO_BENEFICIARY",
                auth_code="1",
                payout_amount=float(payments[0].entitlement_quantity),
                fsp_code="1",
            ),
        ],
        [
            PaymentRecordData(
                id=2,
                remote_id=str(payments[1].id),
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
    payments[0].refresh_from_db()
    assert payments[0].status == Payment.STATUS_DISTRIBUTION_SUCCESS
    assert payments[0].fsp_auth_code == "1"
    assert payments[0].delivered_quantity == payments[0].entitlement_quantity
    assert payments[0].delivered_quantity_usd == 100.0

    payments[1].refresh_from_db()
    assert payments[1].status == Payment.STATUS_ERROR
    assert payments[1].fsp_auth_code == "2"
    assert payments[1].delivered_quantity is None
    assert payments[1].reason_for_unsuccessful_payment == "Error"

    get_records_for_payment_instruction_mock.reset_mock()
    pg_service.sync_records()
    assert get_records_for_payment_instruction_mock.call_count == 0

    assert change_payment_instruction_status_mock.call_count == 2
    payment_plan.refresh_from_db()
    assert payment_plan.status == PaymentPlan.Status.FINISHED


@mock.patch(
    "hope.apps.payment.services.payment_gateway.PaymentGatewayAPI.change_payment_instruction_status",
    return_value="FINALIZED",
)
@mock.patch("hope.models.payment_plan.PaymentPlan.get_exchange_rate", return_value=2.0)
@mock.patch("hope.apps.payment.services.payment_gateway.PaymentGatewayAPI.get_records_for_payment_instruction")
@mock.patch(
    "hope.apps.payment.services.payment_gateway.get_quantity_in_usd",
    return_value=100.00,
)
def test_sync_records_error_messages(
    get_quantity_in_usd_mock: Any,
    get_records_for_payment_instruction_mock: Any,
    get_exchange_rate_mock: Any,
    change_payment_instruction_status_mock: Any,
    payment_gateway_setup: dict,
) -> None:
    split_1, split_2 = payment_gateway_setup["splits"]
    payments = payment_gateway_setup["payments"]
    payment_plan = payment_gateway_setup["payment_plan"]

    split_1.sent_to_payment_gateway = True
    split_2.sent_to_payment_gateway = True
    split_1.save()
    split_2.save()

    get_records_for_payment_instruction_mock.return_value = [
        PaymentRecordData(
            id=1,
            remote_id=str(payments[0].id),
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
            remote_id=str(payments[1].id),
            created="2023-10-10",
            modified="2023-10-11",
            record_code="2",
            parent="2",
            status="TRANSFERRED_TO_BENEFICIARY",
            auth_code="2",
            payout_amount=float(payments[1].entitlement_quantity) - 10.00,
            fsp_code="2",
        ),
    ]

    pg_service = PaymentGatewayService()
    pg_service.api.get_records_for_payment_instruction = get_records_for_payment_instruction_mock  # type: ignore

    assert payment_plan.splits.exists() is True
    assert payment_plan.is_reconciled is False

    pg_service.sync_records()
    assert get_records_for_payment_instruction_mock.call_count == 2
    payment_plan.refresh_from_db()
    payments[0].refresh_from_db()
    payments[1].refresh_from_db()
    assert payments[0].status == Payment.STATUS_SENT_TO_PG
    assert payments[0].fsp_auth_code == "1"
    assert payments[0].delivered_quantity is None
    assert payments[1].status == Payment.STATUS_DISTRIBUTION_PARTIAL
    assert payments[1].fsp_auth_code == "2"
    assert payments[1].delivered_quantity == payments[1].entitlement_quantity - Decimal(10.00)
    assert payment_plan.is_reconciled is False
    assert change_payment_instruction_status_mock.call_count == 0

    get_records_for_payment_instruction_mock.return_value = [
        PaymentRecordData(
            id=1,
            remote_id=str(payments[0].id),
            created="2023-10-10",
            modified="2023-10-11",
            record_code="1",
            parent="1",
            status="TRANSFERRED_TO_BENEFICIARY",
            auth_code="1",
            payout_amount=float(payments[0].entitlement_quantity),
            fsp_code="1",
        ),
        PaymentRecordData(
            id=2,
            remote_id=str(payments[1].id),
            created="2023-10-10",
            modified="2023-10-11",
            record_code="2",
            parent="2",
            status="TRANSFERRED_TO_BENEFICIARY",
            auth_code="2",
            payout_amount=float(payments[1].entitlement_quantity) - 10.00,
            fsp_code="2",
        ),
    ]

    get_records_for_payment_instruction_mock.reset_mock()
    pg_service.sync_records()
    assert get_records_for_payment_instruction_mock.call_count == 1
    payments[0].refresh_from_db()
    payments[1].refresh_from_db()
    assert payments[0].status == Payment.STATUS_DISTRIBUTION_SUCCESS
    assert payments[0].delivered_quantity == payments[0].entitlement_quantity
    assert payments[1].status == Payment.STATUS_DISTRIBUTION_PARTIAL
    assert payments[1].delivered_quantity == payments[1].entitlement_quantity - Decimal(10.00)

    get_records_for_payment_instruction_mock.reset_mock()
    pg_service.sync_records()
    assert get_records_for_payment_instruction_mock.call_count == 0
    assert change_payment_instruction_status_mock.call_count == 2


@mock.patch(
    "hope.apps.payment.services.payment_gateway.PaymentGatewayAPI.change_payment_instruction_status",
    return_value="FINALIZED",
)
@mock.patch("hope.models.payment_plan.PaymentPlan.get_exchange_rate", return_value=2.0)
@mock.patch("hope.apps.payment.services.payment_gateway.PaymentGatewayAPI.get_records_for_payment_instruction")
@mock.patch(
    "hope.apps.payment.services.payment_gateway.get_quantity_in_usd",
    return_value=100.00,
)
def test_sync_payment_plan(
    get_quantity_in_usd_mock: Any,
    get_records_for_payment_instruction_mock: Any,
    get_exchange_rate_mock: Any,
    change_payment_instruction_status_mock: Any,
    payment_gateway_setup: dict,
) -> None:
    split_1, split_2 = payment_gateway_setup["splits"]
    payments = payment_gateway_setup["payments"]
    payment_plan = payment_gateway_setup["payment_plan"]

    split_1.sent_to_payment_gateway = True
    split_2.sent_to_payment_gateway = True
    split_1.save()
    split_2.save()

    payments[0].status = Payment.STATUS_ERROR
    payments[1].status = Payment.STATUS_DISTRIBUTION_SUCCESS
    payments[0].save()
    payments[1].save()

    get_records_for_payment_instruction_mock.side_effect = [
        [
            PaymentRecordData(
                id=1,
                remote_id=str(payments[0].id),
                created="2023-10-10",
                modified="2023-10-11",
                record_code="1",
                parent="1",
                status="TRANSFERRED_TO_BENEFICIARY",
                auth_code="1",
                payout_amount=float(payments[0].entitlement_quantity),
                fsp_code="1",
            )
        ],
        [
            PaymentRecordData(
                id=2,
                remote_id=str(payments[1].id),
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

    pg_service.sync_payment_plan(payment_plan)
    assert get_records_for_payment_instruction_mock.call_count == 2
    payments[0].refresh_from_db()
    assert payments[0].status == Payment.STATUS_DISTRIBUTION_SUCCESS
    assert payments[0].fsp_auth_code == "1"
    assert payments[0].delivered_quantity == payments[0].entitlement_quantity
    assert payments[0].delivered_quantity_usd == 100.0

    payments[1].refresh_from_db()
    assert payments[1].status == Payment.STATUS_ERROR
    assert payments[1].fsp_auth_code == "2"
    assert payments[1].delivered_quantity is None
    assert payments[1].reason_for_unsuccessful_payment == "Error"

    payment_plan.refresh_from_db()
    assert payment_plan.status == PaymentPlan.Status.FINISHED


@mock.patch(
    "hope.apps.payment.services.payment_gateway.PaymentGatewayAPI.change_payment_instruction_status",
    return_value="FINALIZED",
)
@mock.patch("hope.models.payment_plan.PaymentPlan.get_exchange_rate", return_value=2.0)
@mock.patch("hope.apps.payment.services.payment_gateway.PaymentGatewayAPI.get_record")
@mock.patch(
    "hope.apps.payment.services.payment_gateway.get_quantity_in_usd",
    return_value=100.00,
)
def test_sync_record(
    get_quantity_in_usd_mock: Any,
    get_record_mock: Any,
    get_exchange_rate_mock: Any,
    change_payment_instruction_status_mock: Any,
    payment_gateway_setup: dict,
) -> None:
    payments = payment_gateway_setup["payments"]
    payment_plan = payment_gateway_setup["payment_plan"]
    split_1, split_2 = payment_gateway_setup["splits"]

    payments[0].status = Payment.STATUS_ERROR
    payments[0].save()

    payments[1].status = Payment.STATUS_DISTRIBUTION_SUCCESS
    payments[1].save()

    split_1.sent_to_payment_gateway = True
    split_2.sent_to_payment_gateway = True
    split_1.save()
    split_2.save()

    get_record_mock.side_effect = [
        PaymentRecordData(
            id=1,
            remote_id=str(payments[0].id),
            created="2023-10-10",
            modified="2023-10-11",
            record_code="1",
            parent="1",
            status="TRANSFERRED_TO_BENEFICIARY",
            auth_code="1",
            payout_amount=float(payments[0].entitlement_quantity),
            fsp_code="1",
        )
    ]

    pg_service = PaymentGatewayService()
    pg_service.api.get_record = get_record_mock  # type: ignore
    pg_service.api.change_payment_instruction_status = change_payment_instruction_status_mock  # type: ignore

    pg_service.sync_record(payments[0])
    assert get_record_mock.call_count == 1
    payments[0].refresh_from_db()
    assert payments[0].status == Payment.STATUS_DISTRIBUTION_SUCCESS
    assert payments[0].fsp_auth_code == "1"
    assert payments[0].delivered_quantity == payments[0].entitlement_quantity
    assert payments[0].delivered_quantity_usd == 100.0

    payment_plan.refresh_from_db()
    assert payment_plan.status == PaymentPlan.Status.FINISHED
    assert change_payment_instruction_status_mock.call_count == 2


def test_get_hope_status(payment_gateway_setup: dict) -> None:
    payment = payment_gateway_setup["payments"][0]
    record = PaymentRecordData(
        id=1,
        remote_id=str(payment.id),
        created="2023-10-10",
        modified="2023-10-11",
        record_code="1",
        parent="1",
        status="TRANSFERRED_TO_BENEFICIARY",
        auth_code="1",
        payout_amount=float(payment.entitlement_quantity),
        fsp_code="1",
    )
    assert record.get_hope_status(payment.entitlement_quantity) == Payment.STATUS_DISTRIBUTION_SUCCESS
    assert record.get_hope_status(Decimal("1000000.00")) == Payment.STATUS_DISTRIBUTION_PARTIAL

    record.payout_amount = None
    assert record.get_hope_status(Decimal("1000000.00")) == Payment.STATUS_ERROR

    record.payout_amount = float(payment.entitlement_quantity)
    record.status = "NOT EXISTING STATUS"
    assert record.get_hope_status(Decimal("1000000.00")) == Payment.STATUS_ERROR


@mock.patch("hope.apps.payment.services.payment_gateway.PaymentGatewayAPI.add_records_to_payment_instruction")
@mock.patch("hope.apps.payment.services.payment_gateway.PaymentGatewayAPI.change_payment_instruction_status")
def test_add_records_to_payment_instructions_for_split(
    change_payment_instruction_status_mock: Any,
    add_records_to_payment_instruction_mock: Any,
    payment_gateway_setup: dict,
) -> None:
    split_1, split_2 = payment_gateway_setup["splits"]
    payments = payment_gateway_setup["payments"]
    payment_plan = payment_gateway_setup["payment_plan"]

    split_1.sent_to_payment_gateway = False
    split_2.sent_to_payment_gateway = False
    split_1.save()
    split_2.save()

    add_records_to_payment_instruction_mock.return_value = AddRecordsResponseData(
        remote_id="1",
        records={"1": payments[0].id, "2": payments[1].id},
        errors=None,
    )

    change_payment_instruction_status_mock.side_effect = [
        PaymentInstructionStatus.CLOSED.value,
        PaymentInstructionStatus.READY.value,
        PaymentInstructionStatus.CLOSED.value,
        PaymentInstructionStatus.READY.value,
    ]
    pg_service = PaymentGatewayService()
    pg_service.api.add_records_to_payment_instruction = add_records_to_payment_instruction_mock
    pg_service.add_records_to_payment_instructions(payment_plan)

    split_1.refresh_from_db()
    split_2.refresh_from_db()
    payments[0].refresh_from_db()
    payments[1].refresh_from_db()

    assert split_1.sent_to_payment_gateway
    assert split_2.sent_to_payment_gateway
    assert change_payment_instruction_status_mock.call_count == 4
    assert payments[0].status == Payment.STATUS_SENT_TO_PG
    assert payments[1].status == Payment.STATUS_SENT_TO_PG


@mock.patch("hope.apps.payment.services.payment_gateway.PaymentGatewayAPI.add_records_to_payment_instruction")
@mock.patch("hope.apps.payment.services.payment_gateway.PaymentGatewayAPI.change_payment_instruction_status")
def test_add_records_to_payment_instructions_for_split_error(
    change_payment_instruction_status_mock: Any,
    add_records_to_payment_instruction_mock: Any,
    payment_gateway_setup: dict,
) -> None:
    split_1, split_2 = payment_gateway_setup["splits"]
    payments = payment_gateway_setup["payments"]
    payment_plan = payment_gateway_setup["payment_plan"]

    split_1.sent_to_payment_gateway = False
    split_2.sent_to_payment_gateway = False
    split_1.save()
    split_2.save()

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
    pg_service.api.add_records_to_payment_instruction = add_records_to_payment_instruction_mock
    pg_service.add_records_to_payment_instructions(payment_plan)

    split_1.refresh_from_db()
    split_2.refresh_from_db()
    payments[0].refresh_from_db()
    payments[1].refresh_from_db()

    assert split_1.sent_to_payment_gateway is False
    assert split_2.sent_to_payment_gateway is False
    assert payments[0].status == Payment.STATUS_ERROR
    assert payments[1].status == Payment.STATUS_ERROR
    assert payments[0].reason_for_unsuccessful_payment == "Error"
    assert payments[1].reason_for_unsuccessful_payment == "Error"


@mock.patch("hope.apps.payment.services.payment_gateway.PaymentGatewayAPI._post")
def test_api_add_records_to_payment_instruction(
    post_mock: Any,
    payment_gateway_setup: dict,
) -> None:
    payment_plan = payment_gateway_setup["payment_plan"]
    payments = payment_gateway_setup["payments"]
    delivery_mechanisms = payment_gateway_setup["delivery_mechanisms"]

    post_mock.return_value = (
        {
            "remote_id": "123",
            "records": {
                "1": payments[0].id,
            },
            "errors": None,
        },
        200,
    )

    payment_plan.delivery_mechanism = delivery_mechanisms["cash_over_the_counter"]
    payment_plan.save()
    PaymentGatewayAPI().add_records_to_payment_instruction([payments[0]], "123")
    post_mock.assert_called_once_with(
        "payment_instructions/123/add_records/",
        [
            {
                "remote_id": str(payments[0].id),
                "record_code": payments[0].unicef_id,
                "payload": {
                    "amount": str(payments[0].entitlement_quantity),
                    "phone_no": str(payments[0].collector.phone_no),
                    "last_name": payments[0].collector.family_name,
                    "middle_name": payments[0].collector.middle_name,
                    "first_name": payments[0].collector.given_name,
                    "full_name": payments[0].collector.full_name,
                    "destination_currency": payments[0].currency,
                    "delivery_mechanism": "transfer",
                    "account_type": "bank",
                },
                "extra_data": payments[0].household_snapshot.snapshot_data,
            }
        ],
        validate_response=True,
    )


@mock.patch("hope.apps.payment.services.payment_gateway.PaymentGatewayAPI._post")
def test_api_add_records_to_payment_instruction_wallet_integration_mobile(
    post_mock: Any,
    payment_gateway_setup: dict,
    account_types: dict,
    delivery_mechanisms: dict,
) -> None:
    payments = payment_gateway_setup["payments"]

    post_mock.return_value = (
        {
            "remote_id": "123",
            "records": {
                "1": payments[0].id,
            },
            "errors": None,
        },
        200,
    )

    primary_collector = payments[0].collector
    fi = FinancialInstitution.objects.create(type=FinancialInstitution.FinancialInstitutionType.TELCO, name="ABC")
    AccountFactory(
        number="123456789",
        individual=primary_collector,
        data={
            "provider": "Provider",
            "service_provider_code": "CBA",
        },
        account_type=account_types["mobile"],
        financial_institution=fi,
        rdi_merge_status=MergeStatusModel.MERGED,
    )
    payments[0].delivery_type = delivery_mechanisms["mobile_money"]
    payments[0].save()

    PaymentHouseholdSnapshot.objects.all().delete()
    assert PaymentHouseholdSnapshot.objects.count() == 0
    assert Payment.objects.count() == 2

    create_payment_plan_snapshot_data(payments[0].parent)
    assert PaymentHouseholdSnapshot.objects.count() == 2
    payments[0].refresh_from_db()

    PaymentGatewayAPI().add_records_to_payment_instruction([payments[0]], "123")
    post_mock.assert_called_once_with(
        "payment_instructions/123/add_records/",
        [
            {
                "remote_id": str(payments[0].id),
                "record_code": payments[0].unicef_id,
                "payload": {
                    "amount": str(payments[0].entitlement_quantity),
                    "phone_no": str(primary_collector.phone_no),
                    "last_name": primary_collector.family_name,
                    "middle_name": primary_collector.middle_name,
                    "first_name": primary_collector.given_name,
                    "full_name": primary_collector.full_name,
                    "destination_currency": payments[0].currency,
                    "delivery_mechanism": "mobile_money",
                    "account_type": "mobile",
                    "account": {
                        "number": "123456789",
                        "service_provider_code": "CBA",
                        "provider": "Provider",
                        "financial_institution_pk": str(fi.id),
                        "financial_institution_name": str(fi.name),
                    },
                },
                "extra_data": payments[0].household_snapshot.snapshot_data,
            }
        ],
        validate_response=True,
    )


@mock.patch("hope.apps.payment.services.payment_gateway.PaymentGatewayAPI._post")
def test_api_add_records_to_payment_instruction_wallet_integration_bank(
    post_mock: Any,
    payment_gateway_setup: dict,
    delivery_mechanisms: dict,
    uba_fsp: FinancialServiceProvider,
) -> None:
    payments = payment_gateway_setup["payments"]
    pg_fsp = payment_gateway_setup["fsp"]

    post_mock.return_value = (
        {
            "remote_id": "123",
            "records": {
                "1": payments[0].id,
            },
            "errors": None,
        },
        200,
    )

    primary_collector = payments[0].collector

    AccountFactory(
        number="123",
        individual=primary_collector,
        account_type=delivery_mechanisms["transfer_to_account"].account_type,
        data={
            "name": "ABC",
            "code": "456",
        },
        rdi_merge_status=MergeStatusModel.MERGED,
    )
    payments[0].delivery_type = delivery_mechanisms["transfer_to_account"]
    payments[0].save()

    PaymentHouseholdSnapshot.objects.all().delete()
    assert PaymentHouseholdSnapshot.objects.count() == 0
    assert Payment.objects.count() == 2

    create_payment_plan_snapshot_data(payments[0].parent)
    assert PaymentHouseholdSnapshot.objects.count() == 2
    payments[0].refresh_from_db()

    expected_error = (
        "No Financial Institution Mapping found for"
        " financial_institution_code 456,"
        f" fsp {payments[0].financial_service_provider},"
        f" payment {payments[0].id},"
        f" collector {payments[0].collector}."
    )
    with pytest.raises(Exception, match=re.escape(expected_error)):
        PaymentGatewayAPI().add_records_to_payment_instruction([payments[0]], "123")

    payments[0].financial_service_provider = uba_fsp
    payments[0].save()
    PaymentHouseholdSnapshot.objects.all().delete()
    create_payment_plan_snapshot_data(payments[0].parent)
    payments[0].refresh_from_db()
    payments[0].collector.refresh_from_db()
    payments[0].household_snapshot.refresh_from_db()

    expected_payload = {
        "amount": str(payments[0].entitlement_quantity),
        "phone_no": str(primary_collector.phone_no),
        "last_name": primary_collector.family_name,
        "middle_name": primary_collector.middle_name,
        "first_name": primary_collector.given_name,
        "full_name": primary_collector.full_name,
        "destination_currency": payments[0].currency,
        "delivery_mechanism": "transfer_to_account",
        "account_type": "bank",
        "account": {
            "number": "123",
            "name": "ABC",
            "code": "456",
            "service_provider_code": "456",
            "financial_institution_pk": "",
            "financial_institution_name": "",
        },
    }
    expected_body = {
        "remote_id": str(payments[0].id),
        "record_code": payments[0].unicef_id,
        "payload": expected_payload,
        "extra_data": payments[0].household_snapshot.snapshot_data,
    }
    PaymentGatewayAPI().add_records_to_payment_instruction([payments[0]], "123")
    actual_args, actual_kwargs = post_mock.call_args
    assert actual_args[0] == "payment_instructions/123/add_records/"
    assert normalize(actual_args[1][0]) == normalize(expected_body)
    assert actual_kwargs["validate_response"] is True

    post_mock.reset_mock()

    payments[0].financial_service_provider = pg_fsp
    payments[0].save()

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
        financial_service_provider=pg_fsp,
        code="789",
    )

    PaymentHouseholdSnapshot.objects.all().delete()
    create_payment_plan_snapshot_data(payments[0].parent)
    payments[0].refresh_from_db()
    payments[0].collector.refresh_from_db()
    payments[0].household_snapshot.refresh_from_db()
    for account in payments[0].collector.accounts.all():
        account.refresh_from_db()

    PaymentGatewayAPI().add_records_to_payment_instruction([payments[0]], "123")
    expected_payload["account"]["code"] = "456"
    expected_payload["account"]["service_provider_code"] = "789"
    expected_body["extra_data"] = payments[0].household_snapshot.snapshot_data

    actual_args, actual_kwargs = post_mock.call_args
    assert actual_args[0] == "payment_instructions/123/add_records/"
    assert normalize(actual_args[1][0]) == normalize(expected_body)
    assert actual_kwargs["validate_response"] is True
    post_mock.reset_mock()


@mock.patch("hope.apps.payment.services.payment_gateway.PaymentGatewayAPI._post")
def test_api_add_records_to_payment_instruction_validation_error(
    post_mock: Any,
    payment_gateway_setup: dict,
) -> None:
    payment = payment_gateway_setup["payments"][0]
    payment.entitlement_quantity = None
    payment.collector.flex_fields = {}
    payment.save()
    payment.collector.save()
    with pytest.raises(
        PaymentGatewayAPI.PaymentGatewayAPIError,
        match="This field may not be null.",
    ):
        PaymentGatewayAPI().add_records_to_payment_instruction([payment], "123")


@mock.patch("hope.apps.payment.services.payment_gateway.PaymentGatewayAPI._post")
def test_api_add_records_to_payment_instruction_no_snapshot(
    post_mock: Any,
    payment_gateway_setup: dict,
) -> None:
    payment = payment_gateway_setup["payments"][0]
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

    with pytest.raises(
        PaymentGatewayAPI.PaymentGatewayAPIError,
        match=f"Not found snapshot for Payment {payment.unicef_id}",
    ):
        PaymentGatewayAPI().add_records_to_payment_instruction([payment], "123")


@mock.patch("hope.apps.payment.services.payment_gateway.PaymentGatewayAPI._get")
def test_api_get_fsps(get_mock: Any) -> None:
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
def test_api_get_account_types(get_mock: Any) -> None:
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
def test_api_create_payment_instruction(post_mock: Any) -> None:
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
def test_api_get_record(get_mock: Any) -> None:
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
def test_api_change_payment_instruction_status(post_mock: Any) -> None:
    status = Mock()
    status.value = "bad_status"
    with pytest.raises(PaymentGatewayAPI.PaymentGatewayAPIError, match="Can't set invalid Payment Instruction status:"):
        PaymentGatewayAPI().change_payment_instruction_status(
            status,
            "123",
        )

    post_mock.return_value = {"status": "ABORTED"}, 200
    response = PaymentGatewayAPI().change_payment_instruction_status(
        PaymentInstructionStatus.ABORTED,
        "123",
    )
    assert response == "ABORTED"


@mock.patch("hope.apps.payment.services.payment_gateway.PaymentGatewayAPI.get_delivery_mechanisms")
def test_sync_delivery_mechanisms(
    get_delivery_mechanisms_mock: Any,
    delivery_mechanisms: dict,
    account_types: dict,
) -> None:
    assert DeliveryMechanism.objects.count() == len(delivery_mechanisms)

    dm_cash = DeliveryMechanism.objects.get(code="cash")
    dm_cash.is_active = False
    dm_cash.payment_gateway_id = "2"
    dm_cash.save()

    get_delivery_mechanisms_mock.return_value = [
        DeliveryMechanismData(
            id=33,
            code="new_dm",
            name="New DM",
            transfer_type="CASH",
            account_type=account_types["bank"].payment_gateway_id,
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
def test_sync_fsps(
    get_fsps_mock: Any,
    payment_gateway_setup: dict,
) -> None:
    pg_fsp = payment_gateway_setup["fsp"]
    dm_cash_over_the_counter = payment_gateway_setup["delivery_mechanisms"]["cash_over_the_counter"]
    dm_transfer = payment_gateway_setup["delivery_mechanisms"]["transfer"]

    assert pg_fsp.name == "Western Union"
    assert pg_fsp.payment_gateway_id == "123"
    assert list(pg_fsp.delivery_mechanisms.values_list("code", flat=True)) == ["cash_over_the_counter"]

    dm_cash_over_the_counter.payment_gateway_id = "555"
    dm_cash_over_the_counter.save()
    dm_transfer.payment_gateway_id = "666"
    dm_transfer.save()

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
                    "delivery_mechanism": dm_cash_over_the_counter.payment_gateway_id,
                    "delivery_mechanism_name": dm_cash_over_the_counter.code,
                    "label": "label21",
                    "required_fields": ["field1", "field2"],
                },
                {
                    "id": 22,
                    "key": "key22",
                    "delivery_mechanism": dm_transfer.payment_gateway_id,
                    "delivery_mechanism_name": dm_transfer.code,
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
                    "delivery_mechanism": dm_transfer.payment_gateway_id,
                    "delivery_mechanism_name": dm_transfer.code,
                    "label": "label23",
                    "required_fields": ["field3", "field4"],
                },
            ],
        ),
    ]

    pg_service = PaymentGatewayService()
    pg_service.api.get_fsps = get_fsps_mock  # type: ignore

    pg_service.sync_fsps()

    pg_fsp.refresh_from_db()
    assert pg_fsp.name == "Western Union"
    assert pg_fsp.payment_gateway_id == "123"
    assert list(pg_fsp.delivery_mechanisms.values_list("code", flat=True)) == ["transfer"]

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
def test_periodic_sync_payment_gateway_delivery_mechanisms(sync_delivery_mechanisms_mock: Any) -> None:
    periodic_sync_payment_gateway_delivery_mechanisms()
    assert sync_delivery_mechanisms_mock.call_count == 1


@mock.patch("hope.apps.payment.services.payment_gateway.PaymentGatewayAPI.get_record")
@mock.patch("hope.apps.payment.services.payment_gateway.PaymentGatewayAPI.add_records_to_payment_instruction")
@mock.patch("hope.apps.payment.services.payment_gateway.PaymentGatewayAPI.change_payment_instruction_status")
def test_add_missing_records_to_payment_instructions(
    get_record_mock: Any,
    add_records_to_payment_instruction_mock: Any,
    change_payment_instruction_status_mock: Any,
    payment_gateway_setup: dict,
) -> None:
    payment_plan = payment_gateway_setup["payment_plan"]
    # Fetch payments in the same order as eligible_payments.all() to match production iteration order
    payments = list(payment_plan.eligible_payments.all())

    get_record_mock.side_effect = [
        PaymentRecordData(
            id=1,
            remote_id=str(payments[0].id),
            created="2023-10-10",
            modified="2023-10-11",
            record_code="1",
            parent="1",
            status="TRANSFERRED_TO_BENEFICIARY",
            auth_code="1",
            payout_amount=float(payments[0].entitlement_quantity),
            fsp_code="1",
        ),
        None,
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

    with patch.object(pg_service.api, "add_records_to_payment_instruction"):
        pg_service.api.add_records_to_payment_instruction = add_records_to_payment_instruction_mock

        pg_service.add_missing_records_to_payment_instructions(payment_plan)
        assert get_record_mock.call_count == 2

        called_payments, called_split = (
            pg_service.api.add_records_to_payment_instruction.call_args[0][0],
            pg_service.api.add_records_to_payment_instruction.call_args[0][1],
        )
        missing_payment = payments[1]  # second in DB order — got None from side_effect
        assert called_payments == list(Payment.objects.filter(pk=missing_payment.pk))
        assert called_split == missing_payment.parent_split_id


def test_map_financial_institution_pk_and_mapping_found(payment_gateway_setup: dict) -> None:
    payment = payment_gateway_setup["payments"][0]
    fsp = payment_gateway_setup["fsp"]
    fi = FinancialInstitution.objects.create(
        name="Bank A",
        type=FinancialInstitution.FinancialInstitutionType.BANK,
        country=CountryFactory(iso_code3="AFG"),
    )
    FinancialInstitutionMapping.objects.create(
        financial_institution=fi,
        financial_service_provider=fsp,
        code="BANKA_CODE_FOR_OTHER_FSP",
    )
    account_data = {"financial_institution_pk": str(fi.pk), "number": "123"}

    result = PaymentSerializer()._map_financial_institution(payment, account_data)
    assert result["service_provider_code"] == "BANKA_CODE_FOR_OTHER_FSP"
    assert result["number"] == "123"


def test_map_financial_institution_pk_and_mapping_missing_raises(payment_gateway_setup: dict) -> None:
    payment = payment_gateway_setup["payments"][0]
    fi = FinancialInstitution.objects.create(
        name="Bank B",
        type=FinancialInstitution.FinancialInstitutionType.BANK,
        country=CountryFactory(iso_code3="AFG"),
    )
    account_data = {"financial_institution_pk": str(fi.pk)}

    with pytest.raises(Exception, match="No Financial Institution Mapping found"):
        PaymentSerializer()._map_financial_institution(payment, account_data)


def test_map_financial_institution_with_code_and_fsp_is_uba_passthrough(
    payment_gateway_setup: dict,
    uba_fsp: FinancialServiceProvider,
) -> None:
    payment = payment_gateway_setup["payments"][0]
    payment.financial_service_provider = uba_fsp
    payment.save()
    account_data = {"code": "UBA_SPECIFIC_CODE", "number": "999"}

    result = PaymentSerializer()._map_financial_institution(payment, account_data)
    assert result["service_provider_code"] == "UBA_SPECIFIC_CODE"
    assert result["number"] == "999"


def test_map_financial_institution_with_code_and_fsp_is_not_uba_map_via_uba_mapping(
    payment_gateway_setup: dict,
    uba_fsp: FinancialServiceProvider,
) -> None:
    payment = payment_gateway_setup["payments"][0]
    pg_fsp = payment_gateway_setup["fsp"]

    fi = FinancialInstitution.objects.create(name="Bank C", type=FinancialInstitution.FinancialInstitutionType.BANK)
    FinancialInstitutionMapping.objects.create(
        financial_institution=fi, financial_service_provider=uba_fsp, code="UBA_CODE_X"
    )
    FinancialInstitutionMapping.objects.create(
        financial_institution=fi, financial_service_provider=pg_fsp, code="OTHER_FSP_CODE_FOR_BANKC"
    )

    account_data = {"code": "UBA_CODE_X", "extra": "keep"}

    result = PaymentSerializer()._map_financial_institution(payment, account_data)
    assert result["service_provider_code"] == "OTHER_FSP_CODE_FOR_BANKC"
    assert result["extra"] == "keep"


def test_map_financial_institution_with_code_mapping_missing_raises(
    payment_gateway_setup: dict,
    uba_fsp: FinancialServiceProvider,
) -> None:
    payment = payment_gateway_setup["payments"][0]
    account_data = {"code": "UNKNOWN_CODE"}

    with pytest.raises(Exception, match="No Financial Institution Mapping found"):
        PaymentSerializer()._map_financial_institution(payment, account_data)
