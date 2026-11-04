from datetime import datetime, timedelta, timezone as dt_timezone
from decimal import Decimal
import json
from unittest.mock import Mock

from dateutil.relativedelta import relativedelta
from django.contrib.admin.options import get_content_type_for_model
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db import IntegrityError
from django.utils import timezone
from django.utils.timezone import now
import pytest

from extras.test_utils.factories.account import UserFactory
from extras.test_utils.factories.core import CurrencyFactory, FileTempFactory, PaymentPlanPurposeFactory
from extras.test_utils.factories.household import HouseholdFactory, IndividualFactory
from extras.test_utils.factories.payment import (
    ApprovalFactory,
    ApprovalProcessFactory,
    FinancialServiceProviderFactory,
    FollowUpInstructionFactory,
    PaymentFactory,
    PaymentListFactory,
    PaymentListSplitFactory,
    PaymentPlanFactory,
)
from extras.test_utils.factories.program import ProgramCycleFactory, ProgramFactory
from extras.test_utils.factories.steficon import RuleCommitFactory
from hope.apps.household.const import NON_BENEFICIARY
from hope.apps.household.services.household_recalculate_data import recalculate_data
from hope.apps.payment.flows import PaymentListFlow
from hope.models import Approval, FileTemp, Payment, PaymentList, ProgramCycle, Rule

pytestmark = pytest.mark.django_db


@pytest.fixture
def user():
    return UserFactory()


@pytest.fixture
def program_cycle():
    return ProgramCycleFactory(end_date=now().date() + timedelta(days=30))


@pytest.fixture
def payment_list(program_cycle):
    return PaymentListFactory(program_cycle=program_cycle)


def test_get_last_approval_process_date_in_approval(user, program_cycle):
    sent_for_approval_date = timezone.datetime(2000, 10, 10, tzinfo=dt_timezone.utc)
    payment_list = PaymentListFactory(program_cycle=program_cycle, status=PaymentList.Status.IN_APPROVAL)
    ApprovalProcessFactory(
        payment_plan=payment_list.payment_plan,
        sent_for_approval_date=sent_for_approval_date,
        sent_for_approval_by=user,
    )
    payment_list.refresh_from_db()
    modified_data = payment_list._get_last_approval_process_data()
    assert modified_data.modified_date == sent_for_approval_date
    assert modified_data.modified_by == user


@pytest.fixture
def removed_payment_list_without_owner(program_cycle):
    return PaymentListFactory(program_cycle=program_cycle, is_removed=True, payment_plan=None)


def test_last_approval_process_of_plan_without_owner_is_its_own(removed_payment_list_without_owner):
    approval_process = ApprovalProcessFactory(payment_list=removed_payment_list_without_owner)

    assert removed_payment_list_without_owner.last_approval_process == approval_process


def test_get_last_approval_process_date_in_approval_without_process(user, program_cycle):
    payment_list = PaymentListFactory(program_cycle=program_cycle, status=PaymentList.Status.IN_APPROVAL)
    modified_data = payment_list._get_last_approval_process_data()
    assert modified_data.modified_date == payment_list.updated_at
    assert modified_data.modified_by is None


def test_get_last_approval_process_date_in_authorization_with_approval(user, program_cycle):
    payment_list = PaymentListFactory(program_cycle=program_cycle, status=PaymentList.Status.IN_AUTHORIZATION)
    approval_process = ApprovalProcessFactory(payment_plan=payment_list.payment_plan)
    approval = ApprovalFactory(
        approval_process=approval_process,
        type=Approval.APPROVAL,
        created_by=user,
    )
    approval.created_at = timezone.datetime(2000, 10, 11, tzinfo=dt_timezone.utc)
    approval.save(update_fields=["created_at"])
    payment_list.refresh_from_db()
    modified_data = payment_list._get_last_approval_process_data()
    assert modified_data.modified_date == approval.created_at
    assert modified_data.modified_by == user


def test_get_last_approval_process_date_in_authorization_without_approval(user, program_cycle):
    payment_list = PaymentListFactory(program_cycle=program_cycle, status=PaymentList.Status.IN_AUTHORIZATION)
    ApprovalProcessFactory(payment_plan=payment_list.payment_plan)
    payment_list.refresh_from_db()
    modified_data = payment_list._get_last_approval_process_data()
    assert modified_data.modified_date == payment_list.updated_at
    assert modified_data.modified_by is None


def test_get_last_approval_process_date_in_review_with_authorizations(user, program_cycle):
    payment_list = PaymentListFactory(program_cycle=program_cycle, status=PaymentList.Status.IN_REVIEW)
    approval_process = ApprovalProcessFactory(payment_plan=payment_list.payment_plan)
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
    payment_list.refresh_from_db()
    modified_data = payment_list._get_last_approval_process_data()
    assert modified_data.modified_date == last_authorization.created_at
    assert modified_data.modified_by == user


def test_get_last_approval_process_date_in_review_without_authorization(user, program_cycle):
    payment_list = PaymentListFactory(program_cycle=program_cycle, status=PaymentList.Status.IN_REVIEW)
    ApprovalProcessFactory(payment_plan=payment_list.payment_plan)
    payment_list.refresh_from_db()
    modified_data = payment_list._get_last_approval_process_data()
    assert modified_data.modified_date == payment_list.updated_at
    assert modified_data.modified_by is None


def test_get_last_approval_process_date_accepted_with_finance_release(user, program_cycle):
    payment_list = PaymentListFactory(program_cycle=program_cycle, status=PaymentList.Status.ACCEPTED)
    approval_process = ApprovalProcessFactory(payment_plan=payment_list.payment_plan)
    finance_release = ApprovalFactory(
        approval_process=approval_process,
        type=Approval.FINANCE_RELEASE,
        created_by=user,
    )
    finance_release.created_at = timezone.datetime(2000, 10, 13, tzinfo=dt_timezone.utc)
    finance_release.save(update_fields=["created_at"])
    payment_list.refresh_from_db()
    modified_data = payment_list._get_last_approval_process_data()
    assert modified_data.modified_date == finance_release.created_at
    assert modified_data.modified_by == user


def test_get_last_approval_process_date_accepted_without_finance_release(user, program_cycle):
    payment_list = PaymentListFactory(program_cycle=program_cycle, status=PaymentList.Status.ACCEPTED)
    ApprovalProcessFactory(payment_plan=payment_list.payment_plan)
    payment_list.refresh_from_db()
    modified_data = payment_list._get_last_approval_process_data()
    assert modified_data.modified_date == payment_list.updated_at
    assert modified_data.modified_by is None


def test_get_last_approval_process_date_other_status_fallback(user, program_cycle):
    payment_list = PaymentListFactory(program_cycle=program_cycle, status=PaymentList.Status.LOCKED)
    approval_process = ApprovalProcessFactory(payment_plan=payment_list.payment_plan)
    approval = ApprovalFactory(
        approval_process=approval_process,
        type=Approval.FINANCE_RELEASE,
        created_by=user,
    )
    approval.created_at = timezone.datetime(2000, 10, 14, tzinfo=dt_timezone.utc)
    approval.save(update_fields=["created_at"])
    payment_list.refresh_from_db()
    modified_data = payment_list._get_last_approval_process_data()
    assert modified_data.modified_date == payment_list.updated_at
    assert modified_data.modified_by is None


def test_currency_exchange_date():
    payment_list = PaymentListFactory(
        status=PaymentList.Status.LOCKED,
        dispersion_end_date=datetime(2000, 11, 11).date(),
    )
    payment_list.refresh_from_db()
    assert str(payment_list.currency_exchange_date) == "2000-11-11"

    payment_list.status = PaymentList.Status.ACCEPTED
    payment_list.save()
    group = payment_list.payment_plan
    group.status = group.Status.ACCEPTED
    group.save(update_fields=["status"])

    approval_process = ApprovalProcessFactory(payment_plan=group)
    approval = ApprovalFactory(approval_process=approval_process, type=Approval.FINANCE_RELEASE)
    assert group.currency_exchange_date == approval.created_at.date()
    assert str(payment_list.currency_exchange_date) == str(approval.created_at.date())


def test_payment_list_create(user):
    payment_list = PaymentListFactory(created_by=user)
    assert isinstance(payment_list, PaymentList)


def test_is_payment_gateway_and_all_sent_to_fsp_false_for_sent_to_payment_gateway(payment_list):
    PaymentFactory(parent=payment_list)
    payment_list.payment_plan.financial_service_provider = FinancialServiceProviderFactory()
    payment_list.payment_plan.use_payment_gateway = True
    payment_list.payment_plan.save(update_fields=["financial_service_provider", "use_payment_gateway"])
    payment_list.eligible_payments.update(status=Payment.STATUS_SENT_TO_PG)

    assert payment_list.is_payment_gateway_and_all_sent_to_fsp is False


def test_is_payment_gateway_and_all_sent_to_fsp_true_for_sent_to_fsp(payment_list):
    PaymentFactory(parent=payment_list)
    payment_list.payment_plan.financial_service_provider = FinancialServiceProviderFactory()
    payment_list.payment_plan.use_payment_gateway = True
    payment_list.payment_plan.save(update_fields=["financial_service_provider", "use_payment_gateway"])
    payment_list.eligible_payments.update(status=Payment.STATUS_SENT_TO_FSP)

    assert payment_list.is_payment_gateway_and_all_sent_to_fsp is True


def test_update_population_count_fields(payment_list):
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

    PaymentFactory(parent=payment_list, household=hh1, collector=hoh1)
    PaymentFactory(parent=payment_list, household=hh2, collector=hoh2)

    payment_list.update_population_count_fields()

    payment_list.refresh_from_db()
    assert payment_list.female_children_count == 1
    assert payment_list.male_children_count == 1
    assert payment_list.female_adults_count == 1
    assert payment_list.male_adults_count == 1
    assert payment_list.total_households_count == 2
    assert payment_list.total_individuals_count == 4


def test_update_population_count_fields_excludes_withdrawn_individuals(payment_list):
    hoh = IndividualFactory(
        household=None,
        sex="FEMALE",
        birth_date=datetime.now().date() - relativedelta(years=30),
    )
    household = HouseholdFactory(head_of_household=hoh, registration_data_import=hoh.registration_data_import)

    IndividualFactory(
        household=household,
        sex="MALE",
        birth_date=datetime.now().date() - relativedelta(years=20),
        withdrawn=True,
        registration_data_import=household.registration_data_import,
    )
    IndividualFactory(
        household=household,
        sex="FEMALE",
        birth_date=datetime.now().date() - relativedelta(years=5),
        withdrawn=True,
        registration_data_import=household.registration_data_import,
    )

    PaymentFactory(parent=payment_list, household=household, collector=hoh)

    payment_list.update_population_count_fields()

    payment_list.refresh_from_db()
    assert payment_list.total_individuals_count == 1
    assert payment_list.female_adults_count == 1
    assert payment_list.male_adults_count == 0
    assert payment_list.female_children_count == 0
    assert payment_list.total_households_count == 1


def test_update_population_count_fields_excludes_duplicates_and_non_beneficiaries(payment_list):
    hoh = IndividualFactory(
        household=None,
        sex="FEMALE",
        birth_date=datetime.now().date() - relativedelta(years=30),
    )
    household = HouseholdFactory(head_of_household=hoh, registration_data_import=hoh.registration_data_import)

    IndividualFactory(
        household=household,
        sex="MALE",
        birth_date=datetime.now().date() - relativedelta(years=20),
        duplicate=True,
        registration_data_import=household.registration_data_import,
    )
    IndividualFactory(
        household=household,
        sex="MALE",
        birth_date=datetime.now().date() - relativedelta(years=40),
        relationship=NON_BENEFICIARY,
        registration_data_import=household.registration_data_import,
    )

    PaymentFactory(parent=payment_list, household=household, collector=hoh)

    payment_list.update_population_count_fields()

    payment_list.refresh_from_db()
    assert payment_list.total_individuals_count == 1
    assert payment_list.female_adults_count == 1
    assert payment_list.male_adults_count == 0


def test_update_population_count_fields_total_matches_sum_of_household_sizes(payment_list):
    hoh = IndividualFactory(
        household=None,
        sex="FEMALE",
        birth_date=datetime.now().date() - relativedelta(years=30),
    )
    household = HouseholdFactory(head_of_household=hoh, registration_data_import=hoh.registration_data_import)

    IndividualFactory(
        household=household,
        sex="MALE",
        birth_date=datetime.now().date() - relativedelta(years=20),
        registration_data_import=household.registration_data_import,
    )
    IndividualFactory(
        household=household,
        sex="MALE",
        birth_date=datetime.now().date() - relativedelta(years=25),
        withdrawn=True,
        registration_data_import=household.registration_data_import,
    )

    PaymentFactory(parent=payment_list, household=household, collector=hoh)

    data_collecting_type = household.program.data_collecting_type
    data_collecting_type.recalculate_composition = True
    data_collecting_type.save(update_fields=["recalculate_composition"])

    recalculate_data(household)
    payment_list.update_population_count_fields()

    household.refresh_from_db()
    payment_list.refresh_from_db()
    assert payment_list.total_individuals_count == household.size


def test_update_money_fields(payment_list):
    PaymentFactory(
        parent=payment_list,
        entitlement_quantity=Decimal("100.00"),
        entitlement_quantity_usd=Decimal("200.00"),
        delivered_quantity=Decimal("50.00"),
        delivered_quantity_usd=Decimal("100.00"),
        currency=CurrencyFactory(code="PLN", name="Polish Zloty"),
    )
    PaymentFactory(
        parent=payment_list,
        entitlement_quantity=Decimal("100.00"),
        entitlement_quantity_usd=Decimal("200.00"),
        delivered_quantity=Decimal("50.00"),
        delivered_quantity_usd=Decimal("100.00"),
        currency=CurrencyFactory(code="PLN", name="Polish Zloty"),
    )

    payment_list.update_money_fields()

    payment_list.refresh_from_db()
    assert payment_list.total_entitled_quantity == Decimal("200.00")
    assert payment_list.total_entitled_quantity_usd == Decimal("400.00")
    assert payment_list.total_delivered_quantity == Decimal("100.00")
    assert payment_list.total_delivered_quantity_usd == Decimal("200.00")
    assert payment_list.total_undelivered_quantity == Decimal("100.00")
    assert payment_list.total_undelivered_quantity_usd == Decimal("200.00")


def test_not_excluded_payments():
    payment_list = PaymentListFactory()
    PaymentFactory(parent=payment_list, conflicted=False, currency=CurrencyFactory(code="PLN", name="Polish Zloty"))
    PaymentFactory(parent=payment_list, conflicted=True, currency=CurrencyFactory(code="PLN", name="Polish Zloty"))

    payment_list.refresh_from_db()
    assert payment_list.eligible_payments.count() == 1


def test_can_be_locked():
    program = ProgramFactory(cycle=False)
    program_cycle = ProgramCycleFactory(program=program, end_date=now().date() + timedelta(days=30))

    payment_list = PaymentListFactory(
        program_cycle=program_cycle,
        status=PaymentList.Status.LOCKED,
    )
    assert payment_list.can_be_locked is False

    payment_list.status = PaymentList.Status.OPEN
    payment_list.save()
    assert payment_list.can_be_locked is False

    payment_1 = PaymentFactory(parent=payment_list, currency=CurrencyFactory(code="PLN", name="Polish Zloty"))
    assert payment_list.can_be_locked

    payment_list_conflicted = PaymentListFactory(
        status=PaymentList.Status.LOCKED,
        program_cycle=program_cycle,
        business_area=payment_list.business_area,
    )
    PaymentFactory(
        parent=payment_list_conflicted,
        household=payment_1.household,
        currency=CurrencyFactory(code="PLN", name="Polish Zloty"),
    )
    shared_purpose = PaymentPlanPurposeFactory()
    program.payment_plan_purposes.add(shared_purpose)
    payment_list.payment_plan_purposes.add(shared_purpose)
    payment_list_conflicted.payment_plan_purposes.add(shared_purpose)
    assert payment_list.eligible_payments_with_conflicts.filter(payment_list_hard_conflicted=True).count() == 1
    assert payment_list.can_be_locked is False

    PaymentFactory(parent=payment_list, currency=CurrencyFactory(code="PLN", name="Polish Zloty"))
    assert payment_list.can_be_locked is True


def test_get_exchange_rate_for_usdc_currency():
    payment_list = PaymentListFactory(currency=CurrencyFactory(code="USDC", name="USD Coin", is_crypto=True))
    assert payment_list.get_exchange_rate() == 1.0


def test_get_exchange_rate_returns_db_value_when_custom_flag_is_set():
    group = PaymentPlanFactory(
        currency=CurrencyFactory(code="PLN", name="Polish Zloty"),
        custom_exchange_rate=True,
        exchange_rate=Decimal("1.25"),
    )
    payment_list = PaymentListFactory(program_cycle=group.cycle, payment_plan=group)
    assert payment_list.get_exchange_rate() == 1.25


def test_get_exchange_rate_fetches_unore_rate_when_custom_flag_is_not_set():
    group = PaymentPlanFactory(
        currency=CurrencyFactory(code="PLN", name="Polish Zloty"),
        custom_exchange_rate=False,
        exchange_rate=Decimal("1.25"),
    )
    payment_list = PaymentListFactory(program_cycle=group.cycle, payment_plan=group)
    payment_list.get_unore_exchange_rate = Mock(return_value=2.5)

    assert payment_list.get_exchange_rate() == 2.5
    payment_list.get_unore_exchange_rate.assert_called_once_with(None)


def test_is_reconciled():
    payment_list = PaymentListFactory(currency=CurrencyFactory(code="USDC", name="USD Coin", is_crypto=True))
    assert payment_list.is_reconciled is False

    PaymentFactory(parent=payment_list, currency=CurrencyFactory(code="PLN", name="Polish Zloty"), excluded=True)
    assert payment_list.is_reconciled is False

    PaymentFactory(parent=payment_list, currency=CurrencyFactory(code="PLN", name="Polish Zloty"), conflicted=True)
    assert payment_list.is_reconciled is False

    payment_1 = PaymentFactory(
        parent=payment_list, currency=CurrencyFactory(code="PLN", name="Polish Zloty"), status=Payment.STATUS_PENDING
    )
    assert payment_list.is_reconciled is False

    payment_2 = PaymentFactory(
        parent=payment_list, currency=CurrencyFactory(code="PLN", name="Polish Zloty"), status=Payment.STATUS_SENT_TO_PG
    )
    assert payment_list.is_reconciled is False

    payment_1.status = Payment.STATUS_SENT_TO_FSP
    payment_1.save()
    assert payment_list.is_reconciled is False

    payment_1.status = Payment.STATUS_DISTRIBUTION_SUCCESS
    payment_1.save()
    assert payment_list.is_reconciled is False

    payment_2.status = Payment.STATUS_SENT_TO_FSP
    payment_2.save()
    assert payment_list.is_reconciled is False

    payment_2.status = Payment.STATUS_DISTRIBUTION_PARTIAL
    payment_2.save()
    assert payment_list.is_reconciled is True


def test_save_pp_steficon_rule_validation(payment_list):
    rule_for_tp = RuleCommitFactory(rule__type=Rule.TYPE_TARGETING, version=11)
    rule_for_pp = RuleCommitFactory(rule__type=Rule.TYPE_PAYMENT_LIST, version=22)

    assert payment_list.steficon_rule_targeting_id is None
    assert payment_list.steficon_rule_id is None

    payment_list.steficon_rule = rule_for_tp
    with pytest.raises(
        ValidationError,
        match=f"The selected RuleCommit must be associated with a Rule of type {Rule.TYPE_PAYMENT_LIST}.",
    ):
        payment_list.save()

    payment_list.steficon_rule_targeting = rule_for_pp
    with pytest.raises(
        ValidationError,
        match=f"The selected RuleCommit must be associated with a Rule of type {Rule.TYPE_TARGETING}.",
    ):
        payment_list.save()


def test_payment_list_exclude_hh_property(payment_list):
    household = HouseholdFactory()
    other_household = HouseholdFactory()
    other_individual = other_household.head_of_household
    payment_list.excluded_ids = f"{household.unicef_id},{other_individual.unicef_id}"
    payment_list.save(update_fields=["excluded_ids"])
    payment_list.refresh_from_db()

    assert set(payment_list.excluded_household_ids_targeting_level) == {
        household.unicef_id,
        other_household.unicef_id,
    }


def test_remove_export_file_entitlement():
    payment_list = PaymentListFactory(status=PaymentList.Status.LOCKED)
    file_temp = FileTempFactory(
        object_id=payment_list.pk,
        content_type=get_content_type_for_model(payment_list),
        created=timezone.now(),
        file=ContentFile(b"abc", "Test_123.xlsx"),
    )
    payment_list.export_file_entitlement = file_temp
    payment_list.save()
    payment_list.refresh_from_db()
    assert payment_list.has_entitlement_file
    assert payment_list.export_file_entitlement.pk == file_temp.pk

    payment_list.remove_export_file_entitlement()
    payment_list.save()
    payment_list.refresh_from_db()
    assert not payment_list.has_entitlement_file
    assert payment_list.export_file_entitlement is None


def test_remove_imported_file():
    payment_list = PaymentListFactory(
        status=PaymentList.Status.LOCKED,
        imported_file_date=timezone.now(),
    )
    file_temp = FileTempFactory(
        object_id=payment_list.pk,
        content_type=get_content_type_for_model(payment_list),
        created=timezone.now(),
        file=ContentFile(b"abc", "Test_777.xlsx"),
    )
    payment_list.imported_file = file_temp
    payment_list.save()
    payment_list.refresh_from_db()
    assert payment_list.imported_file.pk == file_temp.pk
    assert payment_list.imported_file_name == "Test_777.xlsx"

    payment_list.remove_imported_file()
    payment_list.save()
    payment_list.refresh_from_db()
    assert payment_list.imported_file_name == ""
    assert payment_list.imported_file is None
    assert payment_list.imported_file_date is None


def test_has_payments_reconciliation_overdue():
    payment_list = PaymentListFactory(
        dispersion_start_date=now().date() - timedelta(days=20),
        dispersion_end_date=now().date(),
        status=PaymentList.Status.ACCEPTED,
    )
    program = payment_list.program
    program.reconciliation_window_in_days = 10
    program.save()

    PaymentFactory(parent=payment_list, status=Payment.STATUS_ERROR)
    assert payment_list.has_payments_reconciliation_overdue is False

    PaymentFactory(parent=payment_list, status=Payment.STATUS_SUCCESS, delivered_quantity=Decimal("100.00"))
    assert payment_list.has_payments_reconciliation_overdue is False

    PaymentFactory(parent=payment_list, status=Payment.STATUS_PENDING, delivered_quantity=None)
    assert payment_list.has_payments_reconciliation_overdue is True

    program.reconciliation_window_in_days = 30
    program.save()
    assert payment_list.has_payments_reconciliation_overdue is False

    program.reconciliation_window_in_days = 0
    program.save()
    assert payment_list.has_payments_reconciliation_overdue is False


def test_remove_export_files_removes_entitlement_when_locked():
    payment_list = PaymentListFactory(status=PaymentList.Status.LOCKED)
    file_temp = FileTempFactory(
        object_id=payment_list.pk,
        content_type=get_content_type_for_model(payment_list),
        created=timezone.now(),
        file=ContentFile(b"abc", "entitlement.xlsx"),
    )
    payment_list.export_file_entitlement = file_temp
    payment_list.save()

    payment_list.remove_export_files()

    payment_list.refresh_from_db()
    assert payment_list.export_file_entitlement is None


def test_has_entitlement_file_returns_true_with_entitlement_file():
    payment_list = PaymentListFactory(status=PaymentList.Status.LOCKED)
    file_temp = FileTempFactory(
        object_id=payment_list.pk,
        content_type=get_content_type_for_model(payment_list),
        created=timezone.now(),
        file=ContentFile(b"abc", "entitlement.xlsx"),
    )
    payment_list.export_file_entitlement = file_temp
    payment_list.save()

    assert payment_list.has_entitlement_file is True


def test_has_entitlement_file_returns_false_on_missing_file_temp():
    payment_list = PaymentListFactory(status=PaymentList.Status.LOCKED)
    file_temp = FileTempFactory(
        object_id=payment_list.pk,
        content_type=get_content_type_for_model(payment_list),
        created=timezone.now(),
        file=ContentFile(b"abc", "entitlement.xlsx"),
    )
    file_temp_id = file_temp.pk
    FileTemp.objects.filter(pk=file_temp_id).delete()
    # stale FK id on the instance, row already gone -> descriptor raises FileTemp.DoesNotExist
    payment_list.export_file_entitlement_id = file_temp_id

    assert payment_list.has_entitlement_file is False


def test_can_send_to_payment_gateway_returns_false_when_instruction_managed():
    instruction = FollowUpInstructionFactory()
    payment_list = PaymentListFactory(
        status=PaymentList.Status.ACCEPTED,
        follow_up_instruction=instruction,
    )
    PaymentListSplitFactory(payment_list=payment_list, sent_to_payment_gateway=False)

    assert payment_list.can_send_to_payment_gateway is False


def test_manager_annotations_pp_conflicts():
    program = ProgramFactory(cycle=False)
    program_cycle = ProgramCycleFactory(program=program, end_date=now().date() + timedelta(days=30))

    pp1 = PaymentListFactory(
        program_cycle=program_cycle,
        status=PaymentList.Status.OPEN,
    )

    pp2 = PaymentListFactory(
        status=PaymentList.Status.LOCKED,
        program_cycle=program_cycle,
        business_area=pp1.business_area,
    )
    pp3 = PaymentListFactory(
        status=PaymentList.Status.OPEN,
        program_cycle=program_cycle,
        business_area=pp1.business_area,
    )
    pp4 = PaymentListFactory(
        status=PaymentList.Status.OPEN,
        program_cycle=program_cycle,
        business_area=pp1.business_area,
    )
    shared_purpose = PaymentPlanPurposeFactory()
    program.payment_plan_purposes.add(shared_purpose)
    for pp in [pp1, pp2, pp3, pp4]:
        pp.payment_plan_purposes.add(shared_purpose)

    p1 = PaymentFactory(parent=pp1)
    p2 = PaymentFactory(parent=pp2, household=p1.household)
    p3 = PaymentFactory(parent=pp3, household=p1.household)
    p4 = PaymentFactory(parent=pp4, household=p1.household)

    for obj in [pp1, pp2, pp3, pp4, p1, p2, p3, p4]:
        obj.refresh_from_db()

    p1_data = pp1.eligible_payments_with_conflicts.filter(id=p1.id).values()[0]
    assert p1_data["payment_list_hard_conflicted"] is True
    assert p1_data["payment_list_soft_conflicted"] is True

    assert len(p1_data["payment_list_hard_conflicted_data"]) == 1
    assert json.loads(p1_data["payment_list_hard_conflicted_data"][0]) == {
        "payment_id": str(p2.id),
        "payment_list_id": str(pp2.id),
        "payment_list_status": str(pp2.status),
        "payment_list_start_date": program_cycle.start_date.strftime("%Y-%m-%d"),
        "payment_list_end_date": program_cycle.end_date.strftime("%Y-%m-%d"),
        "payment_list_unicef_id": str(pp2.unicef_id),
        "payment_unicef_id": str(p2.unicef_id),
    }
    assert len(p1_data["payment_list_soft_conflicted_data"]) == 2
    assert len([json.loads(conflict_data) for conflict_data in p1_data["payment_list_soft_conflicted_data"]]) == len(
        [
            {
                "payment_id": str(p3.id),
                "payment_list_id": str(pp3.id),
                "payment_list_status": str(pp3.status),
                "payment_list_start_date": program_cycle.start_date.strftime("%Y-%m-%d"),
                "payment_list_end_date": program_cycle.end_date.strftime("%Y-%m-%d"),
                "payment_list_unicef_id": str(pp3.unicef_id),
                "payment_unicef_id": str(p3.unicef_id),
            },
            {
                "payment_id": str(p4.id),
                "payment_list_id": str(pp4.id),
                "payment_list_status": str(pp4.status),
                "payment_list_start_date": program_cycle.start_date.strftime("%Y-%m-%d"),
                "payment_list_end_date": program_cycle.end_date.strftime("%Y-%m-%d"),
                "payment_list_unicef_id": str(pp4.unicef_id),
                "payment_unicef_id": str(p4.unicef_id),
            },
        ]
    )

    ProgramCycle.objects.filter(pk=program_cycle.id).update(end_date=None)
    program_cycle.refresh_from_db()
    assert program_cycle.end_date is None

    payment_data = pp1.eligible_payments_with_conflicts.filter(id=p1.id).values()[0]
    assert payment_data["payment_list_hard_conflicted"] is True
    assert payment_data["payment_list_soft_conflicted"] is True

    assert len(payment_data["payment_list_hard_conflicted_data"]) == 1
    assert json.loads(payment_data["payment_list_hard_conflicted_data"][0]) == {
        "payment_id": str(p2.id),
        "payment_list_id": str(pp2.id),
        "payment_list_status": str(pp2.status),
        "payment_list_start_date": program_cycle.start_date.strftime("%Y-%m-%d"),
        "payment_list_end_date": None,
        "payment_list_unicef_id": str(pp2.unicef_id),
        "payment_unicef_id": str(p2.unicef_id),
    }
    assert len(payment_data["payment_list_soft_conflicted_data"]) == 2
    assert len(
        [json.loads(conflict_data) for conflict_data in payment_data["payment_list_soft_conflicted_data"]]
    ) == len(
        [
            {
                "payment_id": str(p3.id),
                "payment_list_id": str(pp3.id),
                "payment_list_status": str(pp3.status),
                "payment_list_start_date": program_cycle.start_date.strftime("%Y-%m-%d"),
                "payment_list_end_date": None,
                "payment_list_unicef_id": str(pp3.unicef_id),
                "payment_unicef_id": str(p3.unicef_id),
            },
            {
                "payment_id": str(p4.id),
                "payment_list_id": str(pp4.id),
                "payment_list_status": str(pp4.status),
                "payment_list_start_date": program_cycle.start_date.strftime("%Y-%m-%d"),
                "payment_list_end_date": None,
                "payment_list_unicef_id": str(pp4.unicef_id),
                "payment_unicef_id": str(p4.unicef_id),
            },
        ]
    )

    pp1.status = PaymentList.Status.ACCEPTED
    pp1.save()
    payment_data = pp1.eligible_payments_with_conflicts.filter(id=p1.id).values()[0]
    assert not getattr(payment_data, "payment_list_hard_conflicted", None)
    assert not getattr(payment_data, "payment_list_soft_conflicted", None)
    assert not getattr(payment_data, "payment_list_hard_conflicted_data", None)
    assert not getattr(payment_data, "payment_list_soft_conflicted_data", None)


def test_manager_annotations_conflicts_for_follow_up():
    program_cycle = ProgramCycleFactory(end_date=now().date() + timedelta(days=30))
    pp1 = PaymentListFactory(
        program_cycle=program_cycle,
        plan_type=PaymentList.PlanType.REGULAR,
        status=PaymentList.Status.FINISHED,
    )
    pp2_follow_up = PaymentListFactory(
        status=PaymentList.Status.OPEN,
        plan_type=PaymentList.PlanType.FOLLOW_UP,
        source_payment_list=pp1,
        program_cycle=program_cycle,
    )
    pp3 = PaymentListFactory(
        status=PaymentList.Status.OPEN,
        plan_type=PaymentList.PlanType.FOLLOW_UP,
        source_payment_list=pp1,
        program_cycle=program_cycle,
    )
    shared_purpose = PaymentPlanPurposeFactory()
    program_cycle.program.payment_plan_purposes.add(shared_purpose)
    pp2_follow_up.payment_plan_purposes.add(shared_purpose)
    pp3.payment_plan_purposes.add(shared_purpose)
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
    assert p2_data["payment_list_hard_conflicted"] is False
    assert p2_data["payment_list_soft_conflicted"] is False

    p3_payment = PaymentFactory(
        parent=pp3,
        household=p1.household,
        is_follow_up=False,
    )
    p3_payment.refresh_from_db()
    p3_data = pp3.eligible_payments_with_conflicts.filter(id=p3_payment.id).values()[0]
    assert p3_data["payment_list_hard_conflicted"] is False
    assert p3_data["payment_list_soft_conflicted"] is True

    data = {
        "payment_id": str(p2.id),
        "payment_list_id": str(pp2_follow_up.id),
        "payment_unicef_id": str(p2.unicef_id),
        "payment_list_status": "OPEN",
        "payment_list_end_date": pp2_follow_up.program_cycle.end_date.isoformat(),
        "payment_list_unicef_id": str(pp2_follow_up.unicef_id),
        "payment_list_start_date": pp2_follow_up.program_cycle.start_date.isoformat(),
    }
    assert p3_data["payment_list_soft_conflicted_data"] == [json.dumps(data)]


def test_no_conflict_when_plans_have_different_purposes():
    program = ProgramFactory(status="ACTIVE")
    food = PaymentPlanPurposeFactory()
    education = PaymentPlanPurposeFactory()
    program.payment_plan_purposes.set([food, education])
    cycle = ProgramCycleFactory(program=program)
    plan_a = PaymentListFactory(program_cycle=cycle, status=PaymentList.Status.OPEN, payment_plan_purposes=[food])
    plan_b = PaymentListFactory(program_cycle=cycle, status=PaymentList.Status.OPEN, payment_plan_purposes=[education])
    payment_a = PaymentFactory(parent=plan_a)
    PaymentFactory(parent=plan_b, household=payment_a.household)

    result = plan_a.eligible_payments_with_conflicts.filter(id=payment_a.id).values()[0]

    assert result["payment_list_soft_conflicted"] is False
    assert result["payment_list_hard_conflicted"] is False


def test_conflict_when_plans_share_at_least_one_purpose():
    program = ProgramFactory(status="ACTIVE")
    food = PaymentPlanPurposeFactory()
    education = PaymentPlanPurposeFactory()
    program.payment_plan_purposes.set([food, education])
    cycle = ProgramCycleFactory(program=program)
    plan_a = PaymentListFactory(
        program_cycle=cycle, status=PaymentList.Status.OPEN, payment_plan_purposes=[food, education]
    )
    plan_b = PaymentListFactory(program_cycle=cycle, status=PaymentList.Status.OPEN, payment_plan_purposes=[food])
    payment_a = PaymentFactory(parent=plan_a)
    PaymentFactory(parent=plan_b, household=payment_a.household)

    result = plan_a.eligible_payments_with_conflicts.filter(id=payment_a.id).values()[0]

    assert result["payment_list_soft_conflicted"] is True
    assert result["payment_list_hard_conflicted"] is False


def test_beneficiary_allowed_in_single_multi_purpose_plan():
    program = ProgramFactory(status="ACTIVE")
    food = PaymentPlanPurposeFactory()
    education = PaymentPlanPurposeFactory()
    program.payment_plan_purposes.set([food, education])
    cycle = ProgramCycleFactory(program=program)
    plan = PaymentListFactory(
        program_cycle=cycle, status=PaymentList.Status.OPEN, payment_plan_purposes=[food, education]
    )
    payment = PaymentFactory(parent=plan)

    result = plan.eligible_payments_with_conflicts.filter(id=payment.id).values()[0]

    assert result["payment_list_soft_conflicted"] is False
    assert result["payment_list_hard_conflicted"] is False


def test_beneficiary_allowed_in_two_separate_single_purpose_plans():
    program = ProgramFactory(status="ACTIVE")
    food = PaymentPlanPurposeFactory()
    education = PaymentPlanPurposeFactory()
    program.payment_plan_purposes.set([food, education])
    cycle = ProgramCycleFactory(program=program)
    plan_food = PaymentListFactory(program_cycle=cycle, status=PaymentList.Status.OPEN, payment_plan_purposes=[food])
    plan_education = PaymentListFactory(
        program_cycle=cycle, status=PaymentList.Status.OPEN, payment_plan_purposes=[education]
    )
    payment = PaymentFactory(parent=plan_food)
    PaymentFactory(parent=plan_education, household=payment.household)

    result = plan_food.eligible_payments_with_conflicts.filter(id=payment.id).values()[0]

    assert result["payment_list_soft_conflicted"] is False
    assert result["payment_list_hard_conflicted"] is False


def test_beneficiary_conflict_in_overlapping_plans():
    program = ProgramFactory(status="ACTIVE")
    food = PaymentPlanPurposeFactory()
    program.payment_plan_purposes.set([food])
    cycle = ProgramCycleFactory(program=program)
    plan_a = PaymentListFactory(program_cycle=cycle, status=PaymentList.Status.OPEN, payment_plan_purposes=[food])
    plan_b = PaymentListFactory(program_cycle=cycle, status=PaymentList.Status.OPEN, payment_plan_purposes=[food])
    payment_a = PaymentFactory(parent=plan_a)
    PaymentFactory(parent=plan_b, household=payment_a.household)

    result = plan_a.eligible_payments_with_conflicts.filter(id=payment_a.id).values()[0]

    assert result["payment_list_soft_conflicted"] is True
    assert result["payment_list_hard_conflicted"] is False


def test_payment_list_flow_xlsx_export_error_from_exporting() -> None:
    payment_list = PaymentListFactory(
        status=PaymentList.Status.LOCKED,
        background_action_status=PaymentList.BackgroundActionStatus.XLSX_EXPORTING,
    )
    PaymentListFlow(payment_list).background_action_status_xlsx_export_error()
    assert payment_list.background_action_status == PaymentList.BackgroundActionStatus.XLSX_EXPORT_ERROR


def test_payment_list_flow_xlsx_import_error_from_importing_reconciliation() -> None:
    payment_list = PaymentListFactory(
        status=PaymentList.Status.ACCEPTED,
        background_action_status=PaymentList.BackgroundActionStatus.XLSX_IMPORTING_RECONCILIATION,
    )
    PaymentListFlow(payment_list).background_action_status_xlsx_import_error()
    assert payment_list.background_action_status == PaymentList.BackgroundActionStatus.XLSX_IMPORT_ERROR


@pytest.fixture
def payment_list_importing_fsp_extra_fields() -> PaymentList:
    return PaymentListFactory(
        status=PaymentList.Status.LOCKED_FSP,
        background_action_status=PaymentList.BackgroundActionStatus.XLSX_IMPORTING_FSP_EXTRA_FIELDS,
    )


def test_payment_list_flow_xlsx_import_error_from_importing_fsp_extra_fields(
    payment_list_importing_fsp_extra_fields: PaymentList,
) -> None:
    PaymentListFlow(payment_list_importing_fsp_extra_fields).background_action_status_xlsx_import_error()

    assert (
        payment_list_importing_fsp_extra_fields.background_action_status
        == PaymentList.BackgroundActionStatus.XLSX_IMPORT_ERROR
    )


@pytest.fixture
def removed_payment_list_without_group(program_cycle):
    return PaymentListFactory(program_cycle=program_cycle, payment_plan=None, is_removed=True)


def test_live_payment_list_without_group_violates_constraint(payment_list):
    payment_list.payment_plan = None

    with pytest.raises(IntegrityError, match="payment_plan_in_group_or_instruction_unless_removed"):
        payment_list.save()


@pytest.fixture
def follow_up_instruction(program_cycle):
    return FollowUpInstructionFactory(program=program_cycle.program)


@pytest.fixture
def instruction_child_payment_list(program_cycle, follow_up_instruction):
    return PaymentListFactory(
        program_cycle=program_cycle,
        follow_up_instruction=follow_up_instruction,
        plan_type=PaymentList.PlanType.FOLLOW_UP,
        currency=CurrencyFactory(code="EUR", name="Euro"),
        financial_service_provider=FinancialServiceProviderFactory(),
    )


def test_follow_up_instruction_child_has_no_group(instruction_child_payment_list):
    assert instruction_child_payment_list.payment_plan_id is None


def test_follow_up_instruction_child_reads_currency_and_fsp_from_instruction(
    instruction_child_payment_list, follow_up_instruction
):
    assert instruction_child_payment_list.currency == follow_up_instruction.currency
    assert instruction_child_payment_list.currency.code == "EUR"
    assert instruction_child_payment_list.financial_service_provider == follow_up_instruction.financial_service_provider


@pytest.fixture
def payment_gateway_instruction_child_payment_list(instruction_child_payment_list, follow_up_instruction):
    follow_up_instruction.use_payment_gateway = True
    follow_up_instruction.save(update_fields=["use_payment_gateway"])
    return instruction_child_payment_list


def test_follow_up_instruction_child_reads_use_payment_gateway_from_instruction(
    payment_gateway_instruction_child_payment_list,
):
    assert payment_gateway_instruction_child_payment_list.use_payment_gateway is True
    assert payment_gateway_instruction_child_payment_list.is_payment_gateway is True


def test_payment_list_in_group_and_instruction_violates_constraint(payment_list, follow_up_instruction):
    payment_list.follow_up_instruction = follow_up_instruction

    with pytest.raises(IntegrityError, match="payment_plan_in_group_or_instruction_unless_removed"):
        payment_list.save()


def test_removed_payment_list_without_group_is_allowed(removed_payment_list_without_group):
    assert removed_payment_list_without_group.payment_plan_id is None
    assert removed_payment_list_without_group.is_removed is True


@pytest.fixture
def instruction_approval_process(follow_up_instruction):
    return ApprovalProcessFactory(follow_up_instruction=follow_up_instruction)


def test_follow_up_instruction_child_reads_its_approval_process_from_the_instruction(
    instruction_child_payment_list, instruction_approval_process
):
    assert instruction_child_payment_list.last_approval_process == instruction_approval_process
