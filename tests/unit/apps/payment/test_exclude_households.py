from datetime import date, timedelta
from unittest import mock

import pytest

from extras.test_utils.factories.core import BeneficiaryGroupFactory, DataCollectingTypeFactory
from extras.test_utils.factories.household import HouseholdFactory
from extras.test_utils.factories.payment import PaymentFactory, PaymentPlanFactory
from extras.test_utils.factories.program import ProgramCycleFactory, ProgramFactory
from hope.apps.payment.celery_tasks import payment_plan_exclude_beneficiaries
from hope.models import DataCollectingType, PaymentPlan

pytestmark = pytest.mark.django_db


@pytest.fixture
def program():
    return ProgramFactory(
        data_collecting_type=DataCollectingTypeFactory(type=DataCollectingType.Type.STANDARD),
    )


@pytest.fixture
def program_cycle(program):
    return ProgramCycleFactory(
        program=program,
        start_date=date.today(),
        end_date=date.today() + timedelta(days=365),
    )


@pytest.fixture
def payment_plan(program_cycle):
    return PaymentPlanFactory(
        status=PaymentPlan.Status.LOCKED,
        program_cycle=program_cycle,
    )


@pytest.fixture
def payment_plan_data(payment_plan, program):
    households = [
        HouseholdFactory(program=program),
        HouseholdFactory(program=program),
        HouseholdFactory(program=program),
    ]
    payments = [
        PaymentFactory(parent=payment_plan, household=households[0], collector=households[0].head_of_household),
        PaymentFactory(parent=payment_plan, household=households[1], collector=households[1].head_of_household),
        PaymentFactory(parent=payment_plan, household=households[2], collector=households[2].head_of_household),
    ]
    individuals = [household.head_of_household for household in households]
    return {"households": households, "payments": payments, "individuals": individuals}


def test_exclude_successfully(payment_plan, payment_plan_data):
    payment_plan.background_action_status = PaymentPlan.BackgroundActionStatus.EXCLUDE_BENEFICIARIES
    payment_plan.save(update_fields=["background_action_status"])

    hh_unicef_id_1 = payment_plan_data["households"][0].unicef_id
    hh_unicef_id_2 = payment_plan_data["households"][1].unicef_id

    payment_plan_exclude_beneficiaries(
        payment_plan_id=payment_plan.pk,
        excluding_hh_or_ind_ids=[hh_unicef_id_1, hh_unicef_id_2],
        exclusion_reason="Nice Job!",
    )

    payment_plan.refresh_from_db()
    payment_plan_data["payments"][0].refresh_from_db()
    payment_plan_data["payments"][1].refresh_from_db()
    payment_plan_data["payments"][2].refresh_from_db()

    assert payment_plan.exclusion_reason == "Nice Job!"
    assert payment_plan.exclude_household_error == ""
    assert payment_plan.background_action_status is None
    assert set(payment_plan.excluded_beneficiaries_ids) == {hh_unicef_id_1, hh_unicef_id_2}
    assert payment_plan_data["payments"][0].excluded is True
    assert payment_plan_data["payments"][1].excluded is True
    assert payment_plan_data["payments"][2].excluded is False


def test_exclude_with_invalid_id_sets_info_message(payment_plan, payment_plan_data):
    payment_plan.background_action_status = PaymentPlan.BackgroundActionStatus.EXCLUDE_BENEFICIARIES
    payment_plan.save(update_fields=["background_action_status"])

    hh_unicef_id_1 = payment_plan_data["households"][0].unicef_id
    wrong_hh_id = "INVALID_ID"

    payment_plan_exclude_beneficiaries(
        payment_plan_id=payment_plan.pk,
        excluding_hh_or_ind_ids=[hh_unicef_id_1, wrong_hh_id],
        exclusion_reason="reason wrong id",
    )

    payment_plan.refresh_from_db()

    error_msg = f"['Beneficiary with ID {wrong_hh_id} is not part of this Payment Plan.']"
    assert payment_plan.exclusion_reason == "reason wrong id"
    assert payment_plan.exclude_household_error == error_msg
    assert set(payment_plan.excluded_beneficiaries_ids) == {hh_unicef_id_1}


def test_exclude_all_households_error(payment_plan, payment_plan_data):
    payment_plan.background_action_status = PaymentPlan.BackgroundActionStatus.EXCLUDE_BENEFICIARIES
    payment_plan.save(update_fields=["background_action_status"])

    hh_unicef_ids = [household.unicef_id for household in payment_plan_data["households"]]

    payment_plan_exclude_beneficiaries(
        payment_plan_id=payment_plan.pk,
        excluding_hh_or_ind_ids=hh_unicef_ids,
        exclusion_reason="reason exclude_all_households",
    )

    payment_plan.refresh_from_db()

    error_msg = "['Households cannot be entirely excluded from the Payment Plan.']"
    assert payment_plan.exclusion_reason == "reason exclude_all_households"
    assert payment_plan.background_action_status == PaymentPlan.BackgroundActionStatus.EXCLUDE_BENEFICIARIES_ERROR
    assert payment_plan.exclude_household_error == error_msg


def test_undo_exclude_payment_error_when_payment_has_hard_conflicts(
    payment_plan,
    payment_plan_data,
    program_cycle,
):
    household_1 = payment_plan_data["households"][0]
    payment_1 = payment_plan_data["payments"][0]
    payment_1.excluded = True
    payment_1.save(update_fields=["excluded"])

    finished_payment_plan = PaymentPlanFactory(
        status=PaymentPlan.Status.FINISHED,
        is_follow_up=False,
        program_cycle=program_cycle,
    )
    PaymentFactory(
        parent=finished_payment_plan,
        household=household_1,
        excluded=False,
    )

    payment_plan.background_action_status = PaymentPlan.BackgroundActionStatus.EXCLUDE_BENEFICIARIES
    payment_plan.save(update_fields=["background_action_status"])

    payment_plan_exclude_beneficiaries(
        payment_plan_id=payment_plan.pk,
        excluding_hh_or_ind_ids=[],
        exclusion_reason="Undo HH_1",
    )

    payment_plan.refresh_from_db()

    error_msg = (
        f"['It is not possible to undo exclude Beneficiary with ID {household_1.unicef_id} "
        "because of hard conflict(s) with other Payment Plan(s).']"
    )
    assert payment_plan.background_action_status == PaymentPlan.BackgroundActionStatus.EXCLUDE_BENEFICIARIES_ERROR
    assert payment_plan.exclude_household_error == error_msg


def test_exclude_undoes_excluded_payments(payment_plan, payment_plan_data):
    payment_plan.background_action_status = PaymentPlan.BackgroundActionStatus.EXCLUDE_BENEFICIARIES
    payment_plan.save(update_fields=["background_action_status"])

    payment_1, payment_2 = payment_plan_data["payments"][:2]
    payment_1.excluded = True
    payment_1.save(update_fields=["excluded"])
    hh_unicef_id_2 = payment_plan_data["households"][1].unicef_id
    payment_plan_exclude_beneficiaries(
        payment_plan_id=payment_plan.pk,
        excluding_hh_or_ind_ids=[hh_unicef_id_2],
        exclusion_reason="undo excluded payments",
    )

    payment_1.refresh_from_db()
    payment_2.refresh_from_db()

    assert payment_1.excluded is False
    assert payment_2.excluded is True
    assert set(payment_plan.excluded_beneficiaries_ids) == {hh_unicef_id_2}


def test_exclude_individuals_people_program(payment_plan, payment_plan_data, program):
    people_dct = DataCollectingTypeFactory(label="Social DCT", type=DataCollectingType.Type.SOCIAL)
    beneficiary_group = BeneficiaryGroupFactory(name="People", master_detail=False)
    program.data_collecting_type = people_dct
    program.beneficiary_group = beneficiary_group
    program.save(update_fields=["data_collecting_type", "beneficiary_group"])

    payment_plan.background_action_status = PaymentPlan.BackgroundActionStatus.EXCLUDE_BENEFICIARIES
    payment_plan.save(update_fields=["background_action_status"])

    ind_unicef_id_1 = payment_plan_data["individuals"][0].unicef_id
    ind_unicef_id_2 = payment_plan_data["individuals"][1].unicef_id

    payment_plan_exclude_beneficiaries(
        payment_plan_id=payment_plan.pk,
        excluding_hh_or_ind_ids=[ind_unicef_id_1, ind_unicef_id_2],
        exclusion_reason="Test For People",
    )

    payment_plan.refresh_from_db()
    payment_plan_data["payments"][0].refresh_from_db()
    payment_plan_data["payments"][1].refresh_from_db()
    payment_plan_data["payments"][2].refresh_from_db()

    assert payment_plan.exclusion_reason == "Test For People"
    assert payment_plan.exclude_household_error == ""
    assert payment_plan.background_action_status is None
    assert set(payment_plan.excluded_beneficiaries_ids) == {ind_unicef_id_1, ind_unicef_id_2}
    assert payment_plan_data["payments"][0].excluded is True
    assert payment_plan_data["payments"][1].excluded is True
    assert payment_plan_data["payments"][2].excluded is False


def test_exclude_handles_exception_during_updates(payment_plan, payment_plan_data):
    payment_plan.background_action_status = PaymentPlan.BackgroundActionStatus.EXCLUDE_BENEFICIARIES
    payment_plan.save(update_fields=["background_action_status"])

    hh_unicef_id_1 = payment_plan_data["households"][0].unicef_id

    with (
        mock.patch.object(PaymentPlan, "update_population_count_fields", side_effect=Exception("boom")) as pop_mock,
        mock.patch.object(PaymentPlan, "update_money_fields") as money_mock,
    ):
        payment_plan_exclude_beneficiaries(
            payment_plan_id=payment_plan.pk,
            excluding_hh_or_ind_ids=[hh_unicef_id_1],
            exclusion_reason="reason exception",
        )

    payment_plan.refresh_from_db()

    assert pop_mock.called is True
    assert money_mock.called is False
    assert payment_plan.exclusion_reason == "reason exception"
    assert payment_plan.background_action_status == PaymentPlan.BackgroundActionStatus.EXCLUDE_BENEFICIARIES_ERROR
    assert payment_plan.exclude_household_error is None


def test_exclude_retries_on_missing_payment_plan():
    missing_id = "00000000-0000-0000-0000-000000000000"
    with mock.patch.object(payment_plan_exclude_beneficiaries, "retry", side_effect=RuntimeError("retry")) as retry:
        with pytest.raises(RuntimeError, match="retry"):
            payment_plan_exclude_beneficiaries(
                payment_plan_id=missing_id,
                excluding_hh_or_ind_ids=[],
                exclusion_reason="missing",
            )

    assert retry.call_count == 1
