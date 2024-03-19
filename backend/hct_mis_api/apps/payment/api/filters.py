import django_filters
from django_filters import FilterSet

from hct_mis_api.apps.core.utils import decode_id_string_required
from hct_mis_api.apps.payment.models import PaymentPlan


class PaymentPlanFilter(FilterSet):
    status = django_filters.ChoiceFilter(
        choices=PaymentPlan.Status.choices,
    )
    program = django_filters.CharFilter(method="filter_by_program")

    class Meta:
        model = PaymentPlan
        fields = {
            "total_entitled_quantity": ["gte", "lte"],
            "dispersion_start_date": ["gte"],
            "dispersion_end_date": ["lte"],
            "is_follow_up": ["exact"],
        }

    def filter_by_program(self, qs, name, value):
        return qs.filter(program_id=decode_id_string_required(value))
