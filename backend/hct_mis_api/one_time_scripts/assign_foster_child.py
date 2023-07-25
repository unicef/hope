from django.db.models import DateField, DurationField, Q
from django.db.models.expressions import ExpressionWrapper, F
from django.db.models.functions import Cast, Extract

from hct_mis_api.apps.household.models import (
    FOSTER_CHILD,
    RELATIONSHIP_OTHER,
    Individual,
)


def migrate_foster_child(start_date: str = "2023-05-31", end_date: str = "2023-06-12") -> None:
    Individual.objects.filter(
        Q(relationship=RELATIONSHIP_OTHER)
        & Q(household__registration_data_import__created_at__isnull=False)
        & Q(household__registration_data_import__created_at__gte=start_date)
        & Q(household__registration_data_import__created_at__lte=end_date)
    ).alias(
        date_diff=Extract(
            ExpressionWrapper(
                F("household__registration_data_import__created_at") - Cast("birth_date", output_field=DateField()),
                output_field=DurationField(),
            ),
            "days",
        )
    ).filter(
        Q(date_diff__lt=365 * 18)
    ).update(
        relationship=FOSTER_CHILD
    )
