from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import (
    Case,
    Exists,
    F,
    Func,
    JSONField,
    Model,
    OuterRef,
    Q,
    QuerySet,
    Subquery,
    Value,
    When,
)
from model_utils.managers import SoftDeletableQuerySet

from hope.models.utils import _M, SoftDeletableManager


class ArraySubquery(Subquery):
    template = "ARRAY(%(subquery)s)"
    output_field = ArrayField(base_field=models.TextField())


class PaymentQuerySet(SoftDeletableQuerySet):
    def with_payment_plan_conflicts(self, program_cycle_id: models.UUIDField) -> QuerySet:
        from hope.models import Payment, PaymentPlan, PaymentPlanPurpose

        def _annotate_conflict_data(qs: QuerySet) -> QuerySet:
            return qs.annotate(
                formatted_pp_start_date=Func(
                    F("parent__program_cycle__start_date"),
                    Value("YYYY-MM-DD"),
                    function="to_char",
                    output_field=models.CharField(),
                ),
                formatted_pp_end_date=Case(
                    When(
                        parent__program_cycle__end_date__isnull=False,
                        then=Func(
                            F("parent__program_cycle__end_date"),
                            Value("YYYY-MM-DD"),
                            function="to_char",
                            output_field=models.CharField(),
                        ),
                    ),
                    default=Value(None),
                    output_field=models.CharField(),
                ),
            ).annotate(
                conflict_data=Func(
                    Value("payment_plan_unicef_id"),
                    F("parent__unicef_id"),
                    Value("payment_plan_id"),
                    F("parent_id"),
                    Value("payment_plan_start_date"),
                    F("formatted_pp_start_date"),
                    Value("payment_plan_end_date"),
                    F("formatted_pp_end_date"),
                    Value("payment_plan_status"),
                    F("parent__status"),
                    Value("payment_id"),
                    F("id"),
                    Value("payment_unicef_id"),
                    F("unicef_id"),
                    function="jsonb_build_object",
                    output_field=JSONField(),
                ),
            )

        base_qs = Payment.objects.eligible().filter(parent__program_cycle_id=program_cycle_id)

        shared_purpose = PaymentPlanPurpose.objects.filter(
            payment_plans=OuterRef("parent"),
        ).filter(
            payment_plans=OuterRef(OuterRef("parent")),
        )

        soft_conflicting_pps = (
            base_qs.select_related("parent")
            .exclude(
                Q(id=OuterRef("id"))
                | Q(parent__id=OuterRef("parent_id"))
                | Q(parent__is_removed=True)
                | Q(parent__status=PaymentPlan.Status.ABORTED)
            )
            .filter(
                Q(parent__program_cycle_id=OuterRef("parent__program_cycle_id")),
                ~Q(status__in=Payment.FAILED_STATUSES),
                Exists(shared_purpose),
                parent__status=PaymentPlan.Status.OPEN,
                parent__plan_type=OuterRef("parent__plan_type"),
                household=OuterRef("household"),
            )
        )
        soft_conflicting_pps = _annotate_conflict_data(soft_conflicting_pps)

        hard_conflicting_pps = (
            base_qs.select_related("parent")
            .exclude(
                Q(id=OuterRef("id"))
                | Q(parent__id=OuterRef("parent_id"))
                | Q(parent__is_removed=True)
                | Q(parent__status=PaymentPlan.Status.ABORTED)
            )
            .filter(
                Q(parent__program_cycle_id=OuterRef("parent__program_cycle_id")),
                ~Q(status__in=Payment.FAILED_STATUSES),
                Q(parent__status__in=PaymentPlan.HARD_CONFLICT_STATUSES),
                Q(household=OuterRef("household")) & Q(conflicted=False),
                Q(parent__plan_type=OuterRef("parent__plan_type")),
                Exists(shared_purpose),
            )
        )
        hard_conflicting_pps = _annotate_conflict_data(hard_conflicting_pps)

        return self.annotate(
            payment_plan_hard_conflicted=Case(
                When(parent__status=PaymentPlan.Status.OPEN, then=Exists(hard_conflicting_pps)),
                default=Value(False),
                output_field=models.BooleanField(),
            ),
            payment_plan_hard_conflicted_data=Case(
                When(
                    parent__status=PaymentPlan.Status.OPEN,
                    then=ArraySubquery(hard_conflicting_pps.values("conflict_data")),
                ),
                default=Value([]),
                output_field=ArrayField(base_field=models.TextField()),
            ),
            payment_plan_soft_conflicted=Case(
                When(parent__status=PaymentPlan.Status.OPEN, then=Exists(soft_conflicting_pps)),
                default=Value(False),
                output_field=models.BooleanField(),
            ),
            payment_plan_soft_conflicted_data=Case(
                When(
                    parent__status=PaymentPlan.Status.OPEN,
                    then=ArraySubquery(soft_conflicting_pps.values("conflict_data")),
                ),
                default=Value([]),
                output_field=ArrayField(base_field=models.TextField()),
            ),
        )

    def eligible(self) -> QuerySet:
        return self.exclude(Q(conflicted=True) | Q(excluded=True) | Q(has_valid_wallet=False))

    def update_and_log(
        self,
        logged_changes: dict[str, object],
        user_id: str | None,
        extra_update: dict[str, object] | None = None,
    ) -> int:
        """Apply a bulk ``.update()`` and activity-log only the mapped fields, per payment.

        ``.update()`` bypasses ``save()``/signals, so there is no hook to auto-log the change:
        bundling the update and the log write in one call is what guarantees rows cannot be updated
        without an activity-log entry. The two responsibilities are coupled here deliberately.

        ``logged_changes`` are fields tracked in ACTIVITY_LOG_MAPPING (recorded in the diff);
        ``extra_update`` are applied to the rows but not logged (e.g. *_usd, entitlement_date).
        Old values are captured with a single ``.values()`` query, so cost is constant in query count
        regardless of how many payments are affected. Returns the number of rows updated.
        """
        from django.contrib.contenttypes.models import ContentType

        from hope.apps.payment.utils import _persist_payment_logs, _value_repr
        from hope.models import LogEntry, Payment, User

        # Build the column list to snapshot; FK fields are compared by their *_id attname.
        column_for_field: dict[str, str] = {}
        new_compare: dict[str, object] = {}
        new_repr: dict[str, str | None] = {}
        for field, value in logged_changes.items():
            if isinstance(value, Model):
                column = f"{field}_id"
                new_compare[field] = value.pk
                new_repr[field] = str(value)
            else:
                column = field
                new_compare[field] = value
                new_repr[field] = _value_repr(value)
            column_for_field[field] = column

        snapshot_columns = ["id", "unicef_id", "business_area_id", "program_id", *column_for_field.values()]
        # Snapshot BEFORE the update so old values are captured; ordering is load-bearing.
        rows = list(self.values(*snapshot_columns))

        updated = self.update(**{**logged_changes, **(extra_update or {})})

        user = User.objects.filter(pk=user_id).first() if user_id else None
        content_type = ContentType.objects.get_for_model(Payment)
        logs: list[LogEntry] = []
        program_ids: list[object] = []
        for row in rows:
            changes: dict[str, object] = {}
            for field, column in column_for_field.items():
                old_value = row[column]
                if old_value == new_compare[field]:
                    continue
                changes[field] = {"from": _value_repr(old_value), "to": new_repr[field]}
            if not changes:
                continue
            logs.append(
                LogEntry(
                    content_type=content_type,
                    object_id=row["id"],
                    action=LogEntry.UPDATE,
                    user=user,
                    business_area_id=row["business_area_id"],
                    object_repr=row["unicef_id"] or str(row["id"]),
                    changes=changes,
                )
            )
            program_ids.append(row["program_id"])
        _persist_payment_logs(logs, program_ids)
        return updated


class PaymentManager(SoftDeletableManager[_M]):
    _queryset_class = PaymentQuerySet
    use_for_related_fields = True

    def get_queryset(self) -> QuerySet[_M, _M]:
        return super().get_queryset()

    def eligible(self) -> QuerySet:
        return self.get_queryset().eligible()

    def eligible_with_conflicts_data(self, program_cycle_id: models.UUIDField) -> QuerySet:
        return self.get_queryset().eligible().with_payment_plan_conflicts(program_cycle_id=program_cycle_id)
