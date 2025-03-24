import logging

from django.core.paginator import Paginator

from dateutil.relativedelta import relativedelta

from hct_mis_api.apps.household.models import Individual

logger = logging.getLogger(__name__)


def calculate_age_at_registration_field(batch_size: int = 10_000) -> None:
    individual_queryset = (
        Individual.objects.select_related("registration_data_import")
        .order_by("created_at")
        .filter(birth_date__isnull=False)
        .filter(registration_data_import__created_at__isnull=False)
    ).values_list("id", "birth_date", "registration_data_import__created_at")

    paginator = Paginator(individual_queryset, batch_size)
    pages = paginator.num_pages

    try:
        for page_number in paginator.page_range:
            logger.info(f"Processing page {page_number}/{pages}")

            individuals_to_update = []
            page = paginator.page(page_number)
            for individual_id, birth_date, rdi_created_at in page.object_list:
                individual = Individual(
                    id=str(individual_id),
                    age_at_registration=relativedelta(rdi_created_at.replace(tzinfo=None), birth_date).years,
                )
                individuals_to_update.append(individual)
            Individual.objects.bulk_update(individuals_to_update, ["age_at_registration"])
    except Exception:
        logger.warning("Migration of age_at_registration field failed")
        raise

    logger.info("Migration of age_at_registration went successfully")
