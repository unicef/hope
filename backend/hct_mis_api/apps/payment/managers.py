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
    Subquery,
    Value,
    When,
)

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
                    Value("YYYY-MM-DD"),
                    function="to_char",
                    output_field=models.CharField(),
                ),
                formatted_pp_end_date=Func(
                    F("payment_plan__end_date"),
                    Value("YYYY-MM-DD"),
                    function="to_char",
                    output_field=models.CharField(),
                ),
            ).annotate(
                conflict_data=Func(
                    Value("payment_plan_unicef_id"),
                    F("payment_plan__unicef_id"),
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
                    Value("payment_unicef_id"),
                    F("unicef_id"),
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
                payment_plan__is_removed=False,
                household=OuterRef("household"),
            )
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
        )
        hard_conflicting_pps = _annotate_conflict_data(hard_conflicting_pps)

        return self.annotate(
            payment_plan_hard_conflicted=Exists(hard_conflicting_pps),
            payment_plan_hard_conflicted_data=ArraySubquery(hard_conflicting_pps.values("conflict_data")),
            payment_plan_soft_conflicted=Exists(soft_conflicting_pps),
            payment_plan_soft_conflicted_data=ArraySubquery(soft_conflicting_pps.values("conflict_data")),
        )

    def with_payment_channels(self):
        from hct_mis_api.apps.payment.models import PaymentChannel

        return self.select_related("assigned_payment_channel", "collector", "financial_service_provider").annotate(
            has_defined_payment_channel=Exists(PaymentChannel.objects.filter(individual=OuterRef("collector"))),
            has_assigned_payment_channel=Case(
                When(assigned_payment_channel=None, then=Value(False)),
                default=Value(True),
                output_field=models.BooleanField(),
            ),
        )


class PaymentManager(SoftDeletableManager):
    _queryset_class = PaymentQuerySet
    use_for_related_fields = True

    def get_queryset(self):
        return super().get_queryset().with_payment_plan_conflicts().with_payment_channels()
