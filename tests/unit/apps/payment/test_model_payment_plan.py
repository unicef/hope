from datetime import datetime, timedelta, timezone as dt_timezone
from decimal import Decimal
import json

from dateutil.relativedelta import relativedelta
from django.contrib.admin.options import get_content_type_for_model
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.utils import timezone
from django.utils.timezone import now
import pytest

from extras.test_utils.factories.account import UserFactory
from extras.test_utils.factories.core import FileTempFactory
from extras.test_utils.factories.household import HouseholdFactory, IndividualFactory
from extras.test_utils.factories.payment import (
    ApprovalFactory,
    ApprovalProcessFactory,
    PaymentFactory,
    PaymentPlanFactory,
)
from extras.test_utils.factories.program import ProgramCycleFactory, ProgramFactory
from extras.test_utils.factories.steficon import RuleCommitFactory
from extras.test_utils.factories.targeting import TargetingCriteriaRuleFactory
from hope.apps.core.currencies import USDC
from hope.models import Approval, Payment, PaymentPlan, ProgramCycle, Rule

pytestmark = pytest.mark.django_db


@pytest.fixture
def user():
    return UserFactory()


@pytest.fixture
def program_cycle():
    return ProgramCycleFactory(end_date=now().date() + timedelta(days=30))


@pytest.fixture
def payment_plan(program_cycle):
    return PaymentPlanFactory(program_cycle=program_cycle)


def test_get_last_approval_process_date_in_approval(user, program_cycle):
    sent_for_approval_date = timezone.datetime(2000, 10, 10, tzinfo=dt_timezone.utc)
    payment_plan = PaymentPlanFactory(program_cycle=program_cycle, status=PaymentPlan.Status.IN_APPROVAL)
    ApprovalProcessFactory(
        payment_plan=payment_plan,
        sent_for_approval_date=sent_for_approval_date,
        sent_for_approval_by=user,
    )
    payment_plan.refresh_from_db()
    modified_data = payment_plan._get_last_approval_process_data()
    assert modified_data.modified_date == sent_for_approval_date
    assert modified_data.modified_by == user


def test_get_last_approval_process_date_in_approval_without_process(user, program_cycle):
    payment_plan = PaymentPlanFactory(program_cycle=program_cycle, status=PaymentPlan.Status.IN_APPROVAL)
    modified_data = payment_plan._get_last_approval_process_data()
    assert modified_data.modified_date == payment_plan.updated_at
    assert modified_data.modified_by is None


def test_get_last_approval_process_date_in_authorization_with_approval(user, program_cycle):
    payment_plan = PaymentPlanFactory(program_cycle=program_cycle, status=PaymentPlan.Status.IN_AUTHORIZATION)
    approval_process = ApprovalProcessFactory(payment_plan=payment_plan)
    approval = ApprovalFactory(
        approval_process=approval_process,
        type=Approval.APPROVAL,
        created_by=user,
    )
    approval.created_at = timezone.datetime(2000, 10, 11, tzinfo=dt_timezone.utc)
    approval.save(update_fields=["created_at"])
    payment_plan.refresh_from_db()
    modified_data = payment_plan._get_last_approval_process_data()
    assert modified_data.modified_date == approval.created_at
    assert modified_data.modified_by == user


def test_get_last_approval_process_date_in_authorization_without_approval(user, program_cycle):
    payment_plan = PaymentPlanFactory(program_cycle=program_cycle, status=PaymentPlan.Status.IN_AUTHORIZATION)
    ApprovalProcessFactory(payment_plan=payment_plan)
    payment_plan.refresh_from_db()
    modified_data = payment_plan._get_last_approval_process_data()
    assert modified_data.modified_date == payment_plan.updated_at
    assert modified_data.modified_by is None


def test_get_last_approval_process_date_in_review_with_authorizations(user, program_cycle):
    payment_plan = PaymentPlanFactory(program_cycle=program_cycle, status=PaymentPlan.Status.IN_REVIEW)
    approval_process = ApprovalProcessFactory(payment_plan=payment_plan)
    first_authorization = ApprovalFactory(
        approval_process=approval_process,
        type=Approval.AUTHORIZATION,
        created_by=user,
    )
    first_authorization.created_at = timezone.datetime(2000, 10, 11, tzinfo=dt_timezone.utc)
    first_authorization.save(update_fields=["created_at"])
    last_authorization = ApprovalFactory(
        approval_process=approval_process,
        type=Approval.AUTHORIZATION,
        created_by=user,
    )
    last_authorization.created_at = timezone.datetime(2000, 10, 12, tzinfo=dt_timezone.utc)
    last_authorization.save(update_fields=["created_at"])
    payment_plan.refresh_from_db()
    modified_data = payment_plan._get_last_approval_process_data()
    assert modified_data.modified_date == last_authorization.created_at
    assert modified_data.modified_by == user


def test_get_last_approval_process_date_in_review_without_authorization(user, program_cycle):
    payment_plan = PaymentPlanFactory(program_cycle=program_cycle, status=PaymentPlan.Status.IN_REVIEW)
    ApprovalProcessFactory(payment_plan=payment_plan)
    payment_plan.refresh_from_db()
    modified_data = payment_plan._get_last_approval_process_data()
    assert modified_data.modified_date == payment_plan.updated_at
    assert modified_data.modified_by is None


def test_get_last_approval_process_date_accepted_with_finance_release(user, program_cycle):
    payment_plan = PaymentPlanFactory(program_cycle=program_cycle, status=PaymentPlan.Status.ACCEPTED)
    approval_process = ApprovalProcessFactory(payment_plan=payment_plan)
    finance_release = ApprovalFactory(
        approval_process=approval_process,
        type=Approval.FINANCE_RELEASE,
        created_by=user,
    )
    finance_release.created_at = timezone.datetime(2000, 10, 13, tzinfo=dt_timezone.utc)
    finance_release.save(update_fields=["created_at"])
    payment_plan.refresh_from_db()
    modified_data = payment_plan._get_last_approval_process_data()
    assert modified_data.modified_date == finance_release.created_at
    assert modified_data.modified_by == user


def test_get_last_approval_process_date_accepted_without_finance_release(user, program_cycle):
    payment_plan = PaymentPlanFactory(program_cycle=program_cycle, status=PaymentPlan.Status.ACCEPTED)
    ApprovalProcessFactory(payment_plan=payment_plan)
    payment_plan.refresh_from_db()
    modified_data = payment_plan._get_last_approval_process_data()
    assert modified_data.modified_date == payment_plan.updated_at
    assert modified_data.modified_by is None


def test_get_last_approval_process_date_other_status_fallback(user, program_cycle):
    payment_plan = PaymentPlanFactory(program_cycle=program_cycle, status=PaymentPlan.Status.LOCKED)
    approval_process = ApprovalProcessFactory(payment_plan=payment_plan)
    approval = ApprovalFactory(
        approval_process=approval_process,
        type=Approval.FINANCE_RELEASE,
        created_by=user,
    )
    approval.created_at = timezone.datetime(2000, 10, 14, tzinfo=dt_timezone.utc)
    approval.save(update_fields=["created_at"])
    payment_plan.refresh_from_db()
    modified_data = payment_plan._get_last_approval_process_data()
    assert modified_data.modified_date == payment_plan.updated_at
    assert modified_data.modified_by is None


def test_currency_exchange_date():
    payment_plan = PaymentPlanFactory(
        status=PaymentPlan.Status.LOCKED,
        dispersion_end_date=datetime(2000, 11, 11).date(),
    )
    payment_plan.refresh_from_db()
    assert str(payment_plan.currency_exchange_date) == "2000-11-11"

    payment_plan.status = PaymentPlan.Status.ACCEPTED
    payment_plan.save()

    approval_process = ApprovalProcessFactory(payment_plan=payment_plan)
    approval = ApprovalFactory(approval_process=approval_process, type=Approval.FINANCE_RELEASE)
    assert str(payment_plan.currency_exchange_date) == str(approval.created_at.date())


def test_payment_plan_create(user):
    payment_plan = PaymentPlanFactory(created_by=user)
    assert isinstance(payment_plan, PaymentPlan)


def test_update_population_count_fields(payment_plan):
    hoh1 = IndividualFactory(
        household=None,
        sex="FEMALE",
        birth_date=datetime.now().date() - relativedelta(years=5),
    )
    hoh2 = IndividualFactory(
        household=None,
        sex="MALE",
        birth_date=datetime.now().date() - relativedelta(years=5),
    )
    hh1 = HouseholdFactory(head_of_household=hoh1, registration_data_import=hoh1.registration_data_import)
    hh2 = HouseholdFactory(head_of_household=hoh2, registration_data_import=hoh2.registration_data_import)

    IndividualFactory(
        household=hh1,
        sex="FEMALE",
        birth_date=datetime.now().date() - relativedelta(years=20),
        registration_data_import=hh1.registration_data_import,
    )
    IndividualFactory(
        household=hh2,
        sex="MALE",
        birth_date=datetime.now().date() - relativedelta(years=20),
        registration_data_import=hh2.registration_data_import,
    )

    PaymentFactory(parent=payment_plan, household=hh1, collector=hoh1)
    PaymentFactory(parent=payment_plan, household=hh2, collector=hoh2)

    payment_plan.update_population_count_fields()

    payment_plan.refresh_from_db()
    assert payment_plan.female_children_count == 1
    assert payment_plan.male_children_count == 1
    assert payment_plan.female_adults_count == 1
    assert payment_plan.male_adults_count == 1
    assert payment_plan.total_households_count == 2
    assert payment_plan.total_individuals_count == 4


def test_update_money_fields(payment_plan):
    PaymentFactory(
        parent=payment_plan,
        entitlement_quantity=Decimal("100.00"),
        entitlement_quantity_usd=Decimal("200.00"),
        delivered_quantity=Decimal("50.00"),
        delivered_quantity_usd=Decimal("100.00"),
        currency="PLN",
    )
    PaymentFactory(
        parent=payment_plan,
        entitlement_quantity=Decimal("100.00"),
        entitlement_quantity_usd=Decimal("200.00"),
        delivered_quantity=Decimal("50.00"),
        delivered_quantity_usd=Decimal("100.00"),
        currency="PLN",
    )

    payment_plan.update_money_fields()

    payment_plan.refresh_from_db()
    assert payment_plan.total_entitled_quantity == Decimal("200.00")
    assert payment_plan.total_entitled_quantity_usd == Decimal("400.00")
    assert payment_plan.total_delivered_quantity == Decimal("100.00")
    assert payment_plan.total_delivered_quantity_usd == Decimal("200.00")
    assert payment_plan.total_undelivered_quantity == Decimal("100.00")
    assert payment_plan.total_undelivered_quantity_usd == Decimal("200.00")


def test_not_excluded_payments():
    payment_plan = PaymentPlanFactory()
    PaymentFactory(parent=payment_plan, conflicted=False, currency="PLN")
    PaymentFactory(parent=payment_plan, conflicted=True, currency="PLN")

    payment_plan.refresh_from_db()
    assert payment_plan.eligible_payments.count() == 1


def test_can_be_locked():
    program = ProgramFactory()
    program_cycle = ProgramCycleFactory(program=program, end_date=now().date() + timedelta(days=30))

    payment_plan = PaymentPlanFactory(
        program_cycle=program_cycle,
        status=PaymentPlan.Status.LOCKED,
    )
    assert payment_plan.can_be_locked is False

    payment_plan.status = PaymentPlan.Status.OPEN
    payment_plan.save()
    assert payment_plan.can_be_locked is False

    payment_1 = PaymentFactory(parent=payment_plan, currency="PLN")
    assert payment_plan.can_be_locked

    payment_plan_conflicted = PaymentPlanFactory(
        status=PaymentPlan.Status.LOCKED,
        program_cycle=program_cycle,
        business_area=payment_plan.business_area,
    )
    PaymentFactory(
        parent=payment_plan_conflicted,
        household=payment_1.household,
        currency="PLN",
    )
    assert payment_plan.eligible_payments_with_conflicts.filter(payment_plan_hard_conflicted=True).count() == 1
    assert payment_plan.can_be_locked is False

    PaymentFactory(parent=payment_plan, currency="PLN")
    assert payment_plan.can_be_locked is True


def test_is_population_finalized():
    payment_plan = PaymentPlanFactory(status=PaymentPlan.Status.TP_PROCESSING)
    assert payment_plan.is_population_finalized()


def test_get_exchange_rate_for_usdc_currency():
    payment_plan = PaymentPlanFactory(currency=USDC)
    assert payment_plan.get_exchange_rate() == 1.0


def test_is_reconciled():
    payment_plan = PaymentPlanFactory(currency=USDC)
    assert payment_plan.is_reconciled is False

    PaymentFactory(parent=payment_plan, currency="PLN", excluded=True)
    assert payment_plan.is_reconciled is False

    PaymentFactory(parent=payment_plan, currency="PLN", conflicted=True)
    assert payment_plan.is_reconciled is False

    payment_1 = PaymentFactory(parent=payment_plan, currency="PLN", status=Payment.STATUS_PENDING)
    assert payment_plan.is_reconciled is False

    payment_2 = PaymentFactory(parent=payment_plan, currency="PLN", status=Payment.STATUS_SENT_TO_PG)
    assert payment_plan.is_reconciled is False

    payment_1.status = Payment.STATUS_SENT_TO_FSP
    payment_1.save()
    assert payment_plan.is_reconciled is False

    payment_1.status = Payment.STATUS_DISTRIBUTION_SUCCESS
    payment_1.save()
    assert payment_plan.is_reconciled is False

    payment_2.status = Payment.STATUS_SENT_TO_FSP
    payment_2.save()
    assert payment_plan.is_reconciled is False

    payment_2.status = Payment.STATUS_DISTRIBUTION_PARTIAL
    payment_2.save()
    assert payment_plan.is_reconciled is True


def test_save_pp_steficon_rule_validation(payment_plan):
    rule_for_tp = RuleCommitFactory(rule__type=Rule.TYPE_TARGETING, version=11)
    rule_for_pp = RuleCommitFactory(rule__type=Rule.TYPE_PAYMENT_PLAN, version=22)

    assert payment_plan.steficon_rule_targeting_id is None
    assert payment_plan.steficon_rule_id is None

    payment_plan.steficon_rule = rule_for_tp
    with pytest.raises(
        ValidationError,
        match=f"The selected RuleCommit must be associated with a Rule of type {Rule.TYPE_PAYMENT_PLAN}.",
    ):
        payment_plan.save()

    payment_plan.steficon_rule_targeting = rule_for_pp
    with pytest.raises(
        ValidationError,
        match=f"The selected RuleCommit must be associated with a Rule of type {Rule.TYPE_TARGETING}.",
    ):
        payment_plan.save()


def test_payment_plan_exclude_hh_property(payment_plan):
    household = HouseholdFactory()
    other_household = HouseholdFactory()
    other_individual = other_household.head_of_household
    payment_plan.excluded_ids = f"{household.unicef_id},{other_individual.unicef_id}"
    payment_plan.save(update_fields=["excluded_ids"])
    payment_plan.refresh_from_db()

    assert set(payment_plan.excluded_household_ids_targeting_level) == {
        household.unicef_id,
        other_household.unicef_id,
    }


def test_payment_plan_has_empty_criteria_property(payment_plan):
    assert payment_plan.has_empty_criteria


def test_has_empty_ids_criteria(payment_plan):
    assert payment_plan.has_empty_ids_criteria
    TargetingCriteriaRuleFactory(
        payment_plan=payment_plan,
        household_ids="HH-1, HH-2",
        individual_ids="IND-01, IND-02",
    )
    assert not payment_plan.has_empty_ids_criteria


def test_remove_export_file_entitlement():
    payment_plan = PaymentPlanFactory(status=PaymentPlan.Status.LOCKED)
    file_temp = FileTempFactory(
        object_id=payment_plan.pk,
        content_type=get_content_type_for_model(payment_plan),
        created=timezone.now(),
        file=ContentFile(b"abc", "Test_123.xlsx"),
    )
    payment_plan.export_file_entitlement = file_temp
    payment_plan.save()
    payment_plan.refresh_from_db()
    assert payment_plan.has_export_file
    assert payment_plan.export_file_entitlement.pk == file_temp.pk

    payment_plan.remove_export_file_entitlement()
    payment_plan.save()
    payment_plan.refresh_from_db()
    assert not payment_plan.has_export_file
    assert payment_plan.export_file_entitlement is None


def test_remove_imported_file():
    payment_plan = PaymentPlanFactory(
        status=PaymentPlan.Status.LOCKED,
        imported_file_date=timezone.now(),
    )
    file_temp = FileTempFactory(
        object_id=payment_plan.pk,
        content_type=get_content_type_for_model(payment_plan),
        created=timezone.now(),
        file=ContentFile(b"abc", "Test_777.xlsx"),
    )
    payment_plan.imported_file = file_temp
    payment_plan.save()
    payment_plan.refresh_from_db()
    assert payment_plan.imported_file.pk == file_temp.pk
    assert payment_plan.imported_file_name == "Test_777.xlsx"

    payment_plan.remove_imported_file()
    payment_plan.save()
    payment_plan.refresh_from_db()
    assert payment_plan.imported_file_name == ""
    assert payment_plan.imported_file is None
    assert payment_plan.imported_file_date is None


def test_has_payments_reconciliation_overdue():
    payment_plan = PaymentPlanFactory(
        dispersion_start_date=now().date() - timedelta(days=20),
        dispersion_end_date=now().date(),
        status=PaymentPlan.Status.ACCEPTED,
    )
    program = payment_plan.program
    program.reconciliation_window_in_days = 10
    program.save()

    PaymentFactory(parent=payment_plan, status=Payment.STATUS_ERROR)
    assert payment_plan.has_payments_reconciliation_overdue is False

    PaymentFactory(parent=payment_plan, status=Payment.STATUS_SUCCESS, delivered_quantity=Decimal("100.00"))
    assert payment_plan.has_payments_reconciliation_overdue is False

    PaymentFactory(parent=payment_plan, status=Payment.STATUS_PENDING, delivered_quantity=None)
    assert payment_plan.has_payments_reconciliation_overdue is True

    program.reconciliation_window_in_days = 30
    program.save()
    assert payment_plan.has_payments_reconciliation_overdue is False

    program.reconciliation_window_in_days = 0
    program.save()
    assert payment_plan.has_payments_reconciliation_overdue is False


def test_manager_annotations_pp_conflicts():
    program = ProgramFactory()
    program_cycle = ProgramCycleFactory(program=program, end_date=now().date() + timedelta(days=30))

    pp1 = PaymentPlanFactory(
        program_cycle=program_cycle,
        status=PaymentPlan.Status.OPEN,
    )

    pp2 = PaymentPlanFactory(
        status=PaymentPlan.Status.LOCKED,
        program_cycle=program_cycle,
        business_area=pp1.business_area,
    )
    pp3 = PaymentPlanFactory(
        status=PaymentPlan.Status.OPEN,
        program_cycle=program_cycle,
        business_area=pp1.business_area,
    )
    pp4 = PaymentPlanFactory(
        status=PaymentPlan.Status.OPEN,
        program_cycle=program_cycle,
        business_area=pp1.business_area,
    )
    p1 = PaymentFactory(parent=pp1)
    p2 = PaymentFactory(parent=pp2, household=p1.household)
    p3 = PaymentFactory(parent=pp3, household=p1.household)
    p4 = PaymentFactory(parent=pp4, household=p1.household)

    for obj in [pp1, pp2, pp3, pp4, p1, p2, p3, p4]:
        obj.refresh_from_db()

    p1_data = pp1.eligible_payments_with_conflicts.filter(id=p1.id).values()[0]
    assert p1_data["payment_plan_hard_conflicted"] is True
    assert p1_data["payment_plan_soft_conflicted"] is True

    assert len(p1_data["payment_plan_hard_conflicted_data"]) == 1
    assert json.loads(p1_data["payment_plan_hard_conflicted_data"][0]) == {
        "payment_id": str(p2.id),
        "payment_plan_id": str(pp2.id),
        "payment_plan_status": str(pp2.status),
        "payment_plan_start_date": program_cycle.start_date.strftime("%Y-%m-%d"),
        "payment_plan_end_date": program_cycle.end_date.strftime("%Y-%m-%d"),
        "payment_plan_unicef_id": str(pp2.unicef_id),
        "payment_unicef_id": str(p2.unicef_id),
    }
    assert len(p1_data["payment_plan_soft_conflicted_data"]) == 2
    assert len([json.loads(conflict_data) for conflict_data in p1_data["payment_plan_soft_conflicted_data"]]) == len(
        [
            {
                "payment_id": str(p3.id),
                "payment_plan_id": str(pp3.id),
                "payment_plan_status": str(pp3.status),
                "payment_plan_start_date": program_cycle.start_date.strftime("%Y-%m-%d"),
                "payment_plan_end_date": program_cycle.end_date.strftime("%Y-%m-%d"),
                "payment_plan_unicef_id": str(pp3.unicef_id),
                "payment_unicef_id": str(p3.unicef_id),
            },
            {
                "payment_id": str(p4.id),
                "payment_plan_id": str(pp4.id),
                "payment_plan_status": str(pp4.status),
                "payment_plan_start_date": program_cycle.start_date.strftime("%Y-%m-%d"),
                "payment_plan_end_date": program_cycle.end_date.strftime("%Y-%m-%d"),
                "payment_plan_unicef_id": str(pp4.unicef_id),
                "payment_unicef_id": str(p4.unicef_id),
            },
        ]
    )

    ProgramCycle.objects.filter(pk=program_cycle.id).update(end_date=None)
    program_cycle.refresh_from_db()
    assert program_cycle.end_date is None

    payment_data = pp1.eligible_payments_with_conflicts.filter(id=p1.id).values()[0]
    assert payment_data["payment_plan_hard_conflicted"] is True
    assert payment_data["payment_plan_soft_conflicted"] is True

    assert len(payment_data["payment_plan_hard_conflicted_data"]) == 1
    assert json.loads(payment_data["payment_plan_hard_conflicted_data"][0]) == {
        "payment_id": str(p2.id),
        "payment_plan_id": str(pp2.id),
        "payment_plan_status": str(pp2.status),
        "payment_plan_start_date": program_cycle.start_date.strftime("%Y-%m-%d"),
        "payment_plan_end_date": None,
        "payment_plan_unicef_id": str(pp2.unicef_id),
        "payment_unicef_id": str(p2.unicef_id),
    }
    assert len(payment_data["payment_plan_soft_conflicted_data"]) == 2
    assert len(
        [json.loads(conflict_data) for conflict_data in payment_data["payment_plan_soft_conflicted_data"]]
    ) == len(
        [
            {
                "payment_id": str(p3.id),
                "payment_plan_id": str(pp3.id),
                "payment_plan_status": str(pp3.status),
                "payment_plan_start_date": program_cycle.start_date.strftime("%Y-%m-%d"),
                "payment_plan_end_date": None,
                "payment_plan_unicef_id": str(pp3.unicef_id),
                "payment_unicef_id": str(p3.unicef_id),
            },
            {
                "payment_id": str(p4.id),
                "payment_plan_id": str(pp4.id),
                "payment_plan_status": str(pp4.status),
                "payment_plan_start_date": program_cycle.start_date.strftime("%Y-%m-%d"),
                "payment_plan_end_date": None,
                "payment_plan_unicef_id": str(pp4.unicef_id),
                "payment_unicef_id": str(p4.unicef_id),
            },
        ]
    )

    pp1.status = PaymentPlan.Status.ACCEPTED
    pp1.save()
    payment_data = pp1.eligible_payments_with_conflicts.filter(id=p1.id).values()[0]
    assert not getattr(payment_data, "payment_plan_hard_conflicted", None)
    assert not getattr(payment_data, "payment_plan_soft_conflicted", None)
    assert not getattr(payment_data, "payment_plan_hard_conflicted_data", None)
    assert not getattr(payment_data, "payment_plan_soft_conflicted_data", None)


def test_manager_annotations_conflicts_for_follow_up():
    program_cycle = ProgramCycleFactory(end_date=now().date() + timedelta(days=30))
    pp1 = PaymentPlanFactory(
        program_cycle=program_cycle,
        is_follow_up=False,
        status=PaymentPlan.Status.FINISHED,
    )
    pp2_follow_up = PaymentPlanFactory(
        status=PaymentPlan.Status.OPEN,
        is_follow_up=True,
        source_payment_plan=pp1,
        program_cycle=program_cycle,
    )
    pp3 = PaymentPlanFactory(
        status=PaymentPlan.Status.OPEN,
        is_follow_up=True,
        source_payment_plan=pp1,
        program_cycle=program_cycle,
    )
    p1 = PaymentFactory(
        parent=pp1,
        is_follow_up=False,
        status=Payment.STATUS_ERROR,
    )
    p2 = PaymentFactory(
        parent=pp2_follow_up,
        household=p1.household,
        is_follow_up=True,
        source_payment=p1,
    )

    for obj in [pp1, pp2_follow_up, pp3, p1, p2]:
        obj.refresh_from_db()

    p2_data = pp2_follow_up.eligible_payments_with_conflicts.filter(id=p2.id).values()[0]
    assert p2_data["payment_plan_hard_conflicted"] is False
    assert p2_data["payment_plan_soft_conflicted"] is False

    p3_payment = PaymentFactory(
        parent=pp3,
        household=p1.household,
        is_follow_up=False,
    )
    p3_payment.refresh_from_db()
    p3_data = pp3.eligible_payments_with_conflicts.filter(id=p3_payment.id).values()[0]
    assert p3_data["payment_plan_hard_conflicted"] is False
    assert p3_data["payment_plan_soft_conflicted"] is True

    data = {
        "payment_id": str(p2.id),
        "payment_plan_id": str(pp2_follow_up.id),
        "payment_unicef_id": str(p2.unicef_id),
        "payment_plan_status": "OPEN",
        "payment_plan_end_date": pp2_follow_up.program_cycle.end_date.isoformat(),
        "payment_plan_unicef_id": str(pp2_follow_up.unicef_id),
        "payment_plan_start_date": pp2_follow_up.program_cycle.start_date.isoformat(),
    }
    assert p3_data["payment_plan_soft_conflicted_data"] == [json.dumps(data)]
