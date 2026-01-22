from datetime import date

import pytest

from extras.test_utils.factories import (
    AccountFactory,
    AccountTypeFactory,
    BusinessAreaFactory,
    DeliveryMechanismFactory,
    FinancialServiceProviderFactory,
    HouseholdFactory,
    PaymentFactory,
    PaymentPlanFactory,
    ProgramCycleFactory,
    ProgramFactory,
    RegistrationDataImportFactory,
)
from hope.apps.payment.services import payment_household_snapshot_service
from hope.apps.payment.services.payment_household_snapshot_service import create_payment_plan_snapshot_data
from hope.models import MergeStatusModel

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area():
    return BusinessAreaFactory()


@pytest.fixture
def program(business_area):
    return ProgramFactory(business_area=business_area)


@pytest.fixture
def program_cycle(program):
    return ProgramCycleFactory(program=program)


@pytest.fixture
def registration_data_import(business_area, program):
    return RegistrationDataImportFactory(business_area=business_area, program=program)


@pytest.fixture
def account_type():
    return AccountTypeFactory(key="bank", label="Bank")


@pytest.fixture
def delivery_mechanism(account_type):
    return DeliveryMechanismFactory(code="atm_card", name="ATM Card", account_type=account_type)


@pytest.fixture
def financial_service_provider():
    return FinancialServiceProviderFactory()


@pytest.fixture
def payment_plan(business_area, program_cycle):
    return PaymentPlanFactory(business_area=business_area, program_cycle=program_cycle)


@pytest.fixture
def household_one(business_area, program, registration_data_import):
    return HouseholdFactory(
        business_area=business_area,
        program=program,
        registration_data_import=registration_data_import,
        rdi_merge_status=MergeStatusModel.MERGED,
    )


@pytest.fixture
def household_two(business_area, program, registration_data_import):
    return HouseholdFactory(
        business_area=business_area,
        program=program,
        registration_data_import=registration_data_import,
        rdi_merge_status=MergeStatusModel.MERGED,
    )


@pytest.fixture
def account(account_type, household_one):
    return AccountFactory(
        individual=household_one.head_of_household,
        account_type=account_type,
        number="123",
        data={
            "test": "value",
            "name_of_cardholder": "Marek",
        },
        rdi_merge_status=MergeStatusModel.MERGED,
    )


@pytest.fixture
def payments(
    account,
    payment_plan,
    business_area,
    program,
    household_one,
    household_two,
    delivery_mechanism,
    financial_service_provider,
):
    return [
        PaymentFactory(
            parent=payment_plan,
            business_area=business_area,
            program=program,
            household=household_one,
            head_of_household=household_one.head_of_household,
            collector=household_one.head_of_household,
            entitlement_quantity=100.00,
            entitlement_quantity_usd=200.00,
            delivered_quantity=50.00,
            delivered_quantity_usd=100.00,
            currency="PLN",
            financial_service_provider=financial_service_provider,
            delivery_type=delivery_mechanism,
        ),
        PaymentFactory(
            parent=payment_plan,
            business_area=business_area,
            program=program,
            household=household_two,
            head_of_household=household_two.head_of_household,
            collector=household_two.head_of_household,
            entitlement_quantity=100.00,
            entitlement_quantity_usd=200.00,
            delivered_quantity=50.00,
            delivered_quantity_usd=100.00,
            currency="PLN",
            financial_service_provider=financial_service_provider,
            delivery_type=delivery_mechanism,
        ),
    ]


@pytest.fixture
def batch_payment_plan(business_area, program_cycle):
    return PaymentPlanFactory(
        business_area=business_area,
        program_cycle=program_cycle,
        dispersion_start_date=date(2020, 8, 10),
        dispersion_end_date=date(2020, 12, 10),
    )


@pytest.fixture
def batch_payments(batch_payment_plan, business_area, program, registration_data_import):
    payments = []
    for _ in range(20):
        household = HouseholdFactory(
            business_area=business_area,
            program=program,
            registration_data_import=registration_data_import,
        )
        head_of_household = household.head_of_household
        payments.append(
            PaymentFactory(
                parent=batch_payment_plan,
                business_area=business_area,
                program=program,
                household=household,
                head_of_household=head_of_household,
                collector=head_of_household,
                currency="PLN",
            )
        )
    return payments


def test_build_snapshot(payment_plan, payments, household_one, household_two) -> None:
    create_payment_plan_snapshot_data(payment_plan)

    payment_one, payment_two = payments

    payment_one.refresh_from_db()
    payment_two.refresh_from_db()

    assert payment_one.household_snapshot is not None
    assert payment_two.household_snapshot is not None
    assert str(payment_one.household_snapshot.snapshot_data["id"]) == str(household_one.id)
    assert str(payment_two.household_snapshot.snapshot_data["id"]) == str(household_two.id)
    assert len(payment_one.household_snapshot.snapshot_data["individuals"]) == household_one.individuals.count()
    assert len(payment_two.household_snapshot.snapshot_data["individuals"]) == household_two.individuals.count()
    assert payment_one.household_snapshot.snapshot_data["primary_collector"] is not None
    assert payment_one.household_snapshot.snapshot_data["primary_collector"].get("account_data", {}) == {
        "test": "value",
        "number": "123",
        "name_of_cardholder": "Marek",
        "financial_institution_name": "",
        "financial_institution_pk": "",
    }


def test_batching(batch_payment_plan, batch_payments, monkeypatch) -> None:
    monkeypatch.setattr(payment_household_snapshot_service, "page_size", 2)

    assert batch_payment_plan.payment_items.count() == len(batch_payments)

    create_payment_plan_snapshot_data(batch_payment_plan)

    assert batch_payment_plan.payment_items.filter(household_snapshot__isnull=False).count() == len(batch_payments)
