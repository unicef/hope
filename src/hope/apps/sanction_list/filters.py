from django.db.models.functions import Lower

from django_filters import FilterSet

from hope.apps.core.utils import CustomOrderingFilter
from hope.apps.sanction_list.models import SanctionListIndividual


class SanctionListIndividualFilter(FilterSet):
    class Meta:
        fields = {
            "id": ["exact"],
            "full_name": ["exact", "startswith"],
            "reference_number": ["exact"],
        }
        model = SanctionListIndividual

    order_by = CustomOrderingFilter(
        fields=(
            "id",
            "reference_number",
            Lower("full_name"),
            "listed_on",
        )
    )
