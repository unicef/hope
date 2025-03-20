from django.db.models import QuerySet

import django_filters
from django_filters import FilterSet

from hct_mis_api.apps.core.utils import decode_id_string_required
from hct_mis_api.apps.payment.models import PaymentPlan


class PaymentPlanFilter(FilterSet):
    status = django_filters.ChoiceFilter(
        choices=PaymentPlan.Status.choices,
    )
    program = django_filters.CharFilter(method="filter_by_program")
    name = django_filters.CharFilter(field_name="name", lookup_expr="startswith")
    is_payment_plan = django_filters.BooleanFilter(method="filter_is_payment_plan", required=True)

    class Meta:
        model = PaymentPlan
        fields = {
            "total_entitled_quantity": ["gte", "lte"],
            "dispersion_start_date": ["gte"],
            "dispersion_end_date": ["lte"],
            "is_follow_up": ["exact"],
        }

    def filter_by_program(self, qs: QuerySet, name: str, value: str) -> QuerySet:
        return qs.filter(program_cycle__program_id=decode_id_string_required(value))

    def filter_is_payment_plan(self, qs: "QuerySet", name: str, value: bool) -> "QuerySet[PaymentPlan]":
        """if True return list of PaymentPlan
        if False return list of TargetPopulation
        else return empty list
        """
        if value is True:
            return qs.exclude(status__in=PaymentPlan.PRE_PAYMENT_PLAN_STATUSES)
        elif value is False:
            return qs.filter(status__in=PaymentPlan.PRE_PAYMENT_PLAN_STATUSES)
        else:
            return PaymentPlan.objects.none()
