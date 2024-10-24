from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import (
    Case,
    Exists,
    F,
    Func,
    JSONField,
    OuterRef,
    Q,
    QuerySet,
    Subquery,
    Value,
    When,
)

from model_utils.managers import SoftDeletableManager, SoftDeletableQuerySet


class ArraySubquery(Subquery):
    template = "ARRAY(%(subquery)s)"
    output_field = ArrayField(base_field=models.TextField())


class PaymentQuerySet(SoftDeletableQuerySet):
    def with_payment_plan_conflicts(self) -> QuerySet:
        from hct_mis_api.apps.payment.models import Payment, PaymentPlan

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

        soft_conflicting_pps = (
            self.eligible()
            .select_related("parent")
            .exclude(id=OuterRef("id"))
            .exclude(parent__id=OuterRef("parent_id"))
            .exclude(is_follow_up=True)
            .filter(parent__program_cycle_id=OuterRef("parent__program_cycle_id"))
            .filter(
                Q(parent__program_cycle__start_date__lte=OuterRef("parent__program_cycle__end_date"))
                | Q(parent__program_cycle__end_date__isnull=True),
                Q(parent__program_cycle__end_date__gte=OuterRef("parent__program_cycle__start_date"))
                | Q(parent__program_cycle__end_date__isnull=True),
                ~Q(status=Payment.STATUS_ERROR),
                ~Q(status=Payment.STATUS_NOT_DISTRIBUTED),
                ~Q(status=Payment.STATUS_FORCE_FAILED),
                parent__status=PaymentPlan.Status.OPEN,
                household=OuterRef("household"),
            )
        )
        soft_conflicting_pps = _annotate_conflict_data(soft_conflicting_pps)

        hard_conflicting_pps = (
            self.eligible()
            .select_related("parent")
            .exclude(id=OuterRef("id"))
            .exclude(parent__id=OuterRef("parent_id"))
            .exclude(is_follow_up=True)
            .filter(parent__program_cycle_id=OuterRef("parent__program_cycle_id"))
            .filter(
                Q(parent__program_cycle__start_date__lte=OuterRef("parent__program_cycle__end_date"))
                | Q(parent__program_cycle__end_date__isnull=True),
                Q(parent__program_cycle__end_date__gte=OuterRef("parent__program_cycle__start_date"))
                | Q(parent__program_cycle__end_date__isnull=True),
                Q(household=OuterRef("household")) & Q(conflicted=False),
                ~Q(parent__status=PaymentPlan.Status.OPEN),
                ~Q(status=Payment.STATUS_ERROR),
                ~Q(status=Payment.STATUS_NOT_DISTRIBUTED),
                ~Q(status=Payment.STATUS_FORCE_FAILED),
            )
        )
        hard_conflicting_pps = _annotate_conflict_data(hard_conflicting_pps)

        return self.annotate(
            payment_plan_hard_conflicted=Exists(hard_conflicting_pps),
            payment_plan_hard_conflicted_data=ArraySubquery(hard_conflicting_pps.values("conflict_data")),
            payment_plan_soft_conflicted=Exists(soft_conflicting_pps),
            payment_plan_soft_conflicted_data=ArraySubquery(soft_conflicting_pps.values("conflict_data")),
        )

    def eligible(self) -> QuerySet:
        return self.exclude(Q(conflicted=True) | Q(excluded=True))


class PaymentManager(SoftDeletableManager):
    _queryset_class = PaymentQuerySet
    use_for_related_fields = True

    def get_queryset(self) -> QuerySet:
        return super().get_queryset().with_payment_plan_conflicts()

    def eligible(self) -> QuerySet:
        return self.get_queryset().eligible()
