from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import JSONField, Q, Subquery, OuterRef, Exists, F, Value, Func
from model_utils.managers import SoftDeletableManager, SoftDeletableQuerySet


class ArraySubquery(Subquery):
    template = "ARRAY(%(subquery)s)"
    output_field = ArrayField(base_field=models.TextField())


class PaymentQuerySet(SoftDeletableQuerySet):
    def with_payment_plan_conflicts(self):
        from hct_mis_api.apps.payment.models import PaymentPlan

        def _annotate_conflict_data(qs):
            return qs.annotate(
                formatted_pp_start_date=Func(
                    F("payment_plan__start_date"),
                    Value("DD-MM-YYYY"),
                    function="to_char",
                    output_field=models.CharField(),
                ),
                formatted_pp_end_date=Func(
                    F("payment_plan__end_date"),
                    Value("DD-MM-YYYY"),
                    function="to_char",
                    output_field=models.CharField(),
                ),
            ).annotate(
                conflict_data=Func(
                    Value("payment_plan_id"),
                    F("payment_plan_id"),
                    Value("payment_plan_start_date"),
                    F("formatted_pp_start_date"),
                    Value("payment_plan_end_date"),
                    F("formatted_pp_end_date"),
                    Value("payment_plan_status"),
                    F("payment_plan__status"),
                    Value("payment_id"),
                    F("id"),
                    function="jsonb_build_object",
                    output_field=JSONField(),
                ),
            )

        soft_conflicting_pps = (
            self.select_related("payment_plan")
            .exclude(id=OuterRef("id"))
            .exclude(payment_plan__id=OuterRef("payment_plan_id"))
            .filter(
                Q(payment_plan__start_date__lte=OuterRef("payment_plan__end_date"))
                & Q(payment_plan__end_date__gte=OuterRef("payment_plan__start_date")),
                payment_plan__status=PaymentPlan.Status.OPEN,
                household=OuterRef("household"),
            )
            .distinct()
        )
        soft_conflicting_pps = _annotate_conflict_data(soft_conflicting_pps)

        hard_conflicting_pps = (
            self.select_related("payment_plan")
            .exclude(id=OuterRef("id"))
            .exclude(payment_plan__id=OuterRef("payment_plan_id"))
            .filter(
                Q(payment_plan__start_date__lte=OuterRef("payment_plan__end_date"))
                & Q(payment_plan__end_date__gte=OuterRef("payment_plan__start_date")),
                ~Q(payment_plan__status=PaymentPlan.Status.OPEN),
                Q(household=OuterRef("household")) & Q(excluded=False),
            )
            .distinct()
        )
        hard_conflicting_pps = _annotate_conflict_data(hard_conflicting_pps)

        return self.annotate(
            payment_plan_hard_conflicted=Exists(hard_conflicting_pps),
            payment_plan_hard_conflicted_data=ArraySubquery(hard_conflicting_pps.values("conflict_data")),
            payment_plan_soft_conflicted=Exists(soft_conflicting_pps),
            payment_plan_soft_conflicted_data=ArraySubquery(soft_conflicting_pps.values("conflict_data")),
        )


class PaymentManager(SoftDeletableManager):
    _queryset_class = PaymentQuerySet
    use_for_related_fields = True

    def get_queryset(self):
        return super().get_queryset().with_payment_plan_conflicts()
