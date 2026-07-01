from decimal import Decimal

from django.contrib.contenttypes.models import ContentType
import pytest

from extras.test_utils.factories.account import UserFactory
from extras.test_utils.factories.payment import PaymentFactory, PaymentPlanFactory
from extras.test_utils.factories.program import ProgramFactory
from hope.apps.activity_log.utils import copy_model_object
from hope.apps.core.utils import nested_getattr
from hope.apps.payment.services.mark_as_failed import mark_as_failed as mark_as_failed_service
from hope.apps.payment.utils import (
    bulk_log_payment_changes,
    log_payment_change,
    log_payment_plan_approval,
    log_payment_plan_supporting_document,
    update_payments_and_log,
)
from hope.models import LogEntry, Payment, PaymentPlan, Program, User

pytestmark = pytest.mark.django_db


@pytest.fixture
def user() -> User:
    return UserFactory(first_name="Pay", last_name="Author")


@pytest.fixture
def program() -> Program:
    return ProgramFactory(name="Payment log program")


@pytest.fixture
def payment_plan(program: Program) -> PaymentPlan:
    return PaymentPlanFactory(program_cycle__program=program)


@pytest.fixture
def payments(payment_plan: PaymentPlan, program: Program) -> list[Payment]:
    return [
        PaymentFactory(parent=payment_plan, program=program, status=Payment.STATUS_PENDING),
        PaymentFactory(parent=payment_plan, program=program, status=Payment.STATUS_PENDING),
    ]


@pytest.mark.parametrize("field_path", sorted(Payment.ACTIVITY_LOG_MAPPING.keys()))
def test_payment_activity_log_mapping_keys_resolve(payments: list[Payment], field_path: str) -> None:
    nested_getattr(payments[0], field_path)


@pytest.mark.enable_activity_log
def test_log_payment_change_single_edit(payments: list[Payment], user: User, program: Program) -> None:
    payment = payments[0]
    old_payment = copy_model_object(payment)
    payment.status = Payment.STATUS_FORCE_FAILED
    payment.delivered_quantity = Decimal("0.00")
    payment.save(update_fields=["status", "delivered_quantity"])

    log_payment_change(old_payment, payment, str(user.pk))

    log = LogEntry.objects.get(object_id=payment.pk)
    assert log.action == LogEntry.UPDATE
    assert log.user == user
    assert log.changes["status"]["to"] == Payment.STATUS_FORCE_FAILED
    assert list(log.programs.values_list("pk", flat=True)) == [program.pk]


@pytest.mark.enable_activity_log
def test_bulk_log_payment_changes_one_insert_path(payments: list[Payment], user: User) -> None:
    pairs = []
    for payment in payments:
        old_payment = copy_model_object(payment)
        payment.status = Payment.STATUS_DISTRIBUTION_SUCCESS
        payment.delivered_quantity = Decimal("100.00")
        payment.save(update_fields=["status", "delivered_quantity"])
        pairs.append((old_payment, payment))

    bulk_log_payment_changes(pairs, user)

    logs = LogEntry.objects.filter(object_id__in=[p.pk for p in payments])
    assert logs.count() == 2
    assert all(log.changes["status"]["to"] == Payment.STATUS_DISTRIBUTION_SUCCESS for log in logs)
    assert all(log.user == user for log in logs)


@pytest.mark.enable_activity_log
def test_bulk_log_payment_changes_skips_noop(payments: list[Payment], user: User) -> None:
    # no field changed -> no log
    pairs = [(copy_model_object(payment), payment) for payment in payments]

    bulk_log_payment_changes(pairs, user)

    assert not LogEntry.objects.filter(object_id__in=[p.pk for p in payments]).exists()


@pytest.mark.enable_activity_log
def test_mark_as_failed_service_logs_single_payment(payments: list[Payment], user: User) -> None:
    payment = payments[0]

    mark_as_failed_service(payment, str(user.pk))

    log = LogEntry.objects.get(object_id=payment.pk)
    assert log.action == LogEntry.UPDATE
    assert log.user == user
    assert log.changes["status"]["to"] == Payment.STATUS_FORCE_FAILED


@pytest.mark.enable_activity_log
def test_log_payment_plan_approval_records_actor_and_comment(
    payment_plan: PaymentPlan, user: User, program: Program
) -> None:
    log_payment_plan_approval(payment_plan, user, "AUTHORIZATION", "Looks good")

    log = LogEntry.objects.get(object_id=payment_plan.pk)
    assert log.user == user
    assert log.changes["acceptance_process"]["to"] == "AUTHORIZATION"
    assert log.changes["comment"]["to"] == "Looks good"
    assert list(log.programs.values_list("pk", flat=True)) == [program.pk]


@pytest.mark.enable_activity_log
def test_log_payment_plan_supporting_document_create_and_delete(payment_plan: PaymentPlan, user: User) -> None:
    log_payment_plan_supporting_document(payment_plan, user, "contract.pdf", created=True)
    log_payment_plan_supporting_document(payment_plan, user, "contract.pdf", created=False)

    logs = LogEntry.objects.filter(object_id=payment_plan.pk).order_by("timestamp")
    assert logs.count() == 2
    assert logs[0].changes["supporting_document"]["to"] == "contract.pdf"
    assert logs[1].changes["supporting_document"]["from"] == "contract.pdf"
    assert logs[1].changes["supporting_document"]["to"] is None


@pytest.mark.enable_activity_log
def test_update_payments_and_log_field_update(payments: list[Payment], user: User, program: Program) -> None:
    queryset = Payment.objects.filter(pk__in=[p.pk for p in payments])

    updated = update_payments_and_log(queryset, {"excluded": True}, str(user.pk))

    assert updated == 2
    for payment in payments:
        payment.refresh_from_db()
        assert payment.excluded is True
    logs = LogEntry.objects.filter(object_id__in=[p.pk for p in payments])
    assert logs.count() == 2
    assert all(log.changes["excluded"]["to"] == "True" for log in logs)
    assert all(log.user == user for log in logs)
    assert all(list(log.programs.values_list("pk", flat=True)) == [program.pk] for log in logs)


@pytest.mark.enable_activity_log
def test_update_payments_and_log_extra_update_not_logged(payments: list[Payment], user: User) -> None:
    queryset = Payment.objects.filter(pk__in=[p.pk for p in payments])

    update_payments_and_log(
        queryset,
        {"entitlement_quantity": Decimal("50.00")},
        str(user.pk),
        extra_update={"entitlement_quantity_usd": Decimal("50.00")},
    )

    log = LogEntry.objects.filter(object_id=payments[0].pk).first()
    assert "entitlement_quantity" in log.changes
    assert "entitlement_quantity_usd" not in log.changes


@pytest.mark.enable_activity_log
def test_bulk_log_payment_changes_query_count_is_constant(
    payments: list[Payment], user: User, django_assert_num_queries
) -> None:
    pairs = []
    for payment in payments:
        old_payment = copy_model_object(payment)
        payment.status = Payment.STATUS_DISTRIBUTION_SUCCESS
        payment.save(update_fields=["status"])
        pairs.append((old_payment, payment))
    ContentType.objects.get_for_model(Payment)  # warm content-type cache so the count is deterministic

    # 2 payments -> log bulk insert + program m2m bulk insert; a per-row regression would exceed this
    with django_assert_num_queries(2):
        bulk_log_payment_changes(pairs, user=user)

    assert LogEntry.objects.filter(object_id__in=[p.pk for p in payments]).count() == 2


@pytest.mark.enable_activity_log
def test_update_payments_and_log_query_count_is_constant(
    payments: list[Payment], user: User, django_assert_num_queries
) -> None:
    queryset = Payment.objects.filter(pk__in=[p.pk for p in payments])
    ContentType.objects.get_for_model(Payment)  # warm content-type cache

    # values snapshot + update + user lookup + log insert + program m2m insert, regardless of row count
    with django_assert_num_queries(5):
        update_payments_and_log(queryset, {"excluded": True}, str(user.pk))

    assert LogEntry.objects.filter(object_id__in=[p.pk for p in payments]).count() == 2


@pytest.mark.enable_activity_log
def test_update_payments_and_log_logs_fk_valued_change(payments: list[Payment], user: User) -> None:
    target, source = payments
    queryset = Payment.objects.filter(pk=target.pk)

    update_payments_and_log(queryset, {"source_payment": source}, str(user.pk))

    target.refresh_from_db()
    assert target.source_payment_id == source.pk
    log = LogEntry.objects.get(object_id=target.pk)
    assert log.changes["source_payment"]["to"] == str(source)


@pytest.mark.enable_activity_log
def test_bulk_log_payment_changes_records_create_when_old_is_none(payments: list[Payment], user: User) -> None:
    new = payments[0]

    bulk_log_payment_changes([(None, new)], user)

    log = LogEntry.objects.get(object_id=new.pk)
    assert log.action == LogEntry.CREATE


@pytest.mark.enable_activity_log
def test_log_payment_plan_approval_without_comment(payment_plan: PaymentPlan, user: User) -> None:
    log_payment_plan_approval(payment_plan, user, "APPROVAL", None)

    log = LogEntry.objects.get(object_id=payment_plan.pk)
    assert log.changes["acceptance_process"]["to"] == "APPROVAL"
    assert "comment" not in log.changes


@pytest.mark.enable_activity_log
def test_update_payments_and_log_skips_unchanged_payment(payments: list[Payment], user: User) -> None:
    already_excluded, changing = payments
    already_excluded.excluded = True
    already_excluded.save(update_fields=["excluded"])
    queryset = Payment.objects.filter(pk__in=[p.pk for p in payments])

    update_payments_and_log(queryset, {"excluded": True}, str(user.pk))

    # already True -> field skipped -> no changes -> row produces no log; only the changed one is logged
    assert not LogEntry.objects.filter(object_id=already_excluded.pk).exists()
    assert LogEntry.objects.filter(object_id=changing.pk).exists()
