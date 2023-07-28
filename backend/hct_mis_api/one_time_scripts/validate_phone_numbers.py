from django.core.paginator import Paginator

from hct_mis_api.apps.household.models import Individual
from hct_mis_api.apps.utils.phone import calculate_phone_numbers_validity


def validate_phone_numbers() -> None:
    individuals = []
    queryset = Individual.objects.only(
        "phone_no", "phone_no_alternative", "phone_no_valid", "phone_no_alternative_valid"
    )
    paginator = Paginator(queryset, 1000)
    number_of_pages = paginator.num_pages
    for page in paginator.page_range:
        print(f"Processing page {page} of {number_of_pages}")
        for individual in paginator.page(page).object_list:
            individual = calculate_phone_numbers_validity(individual)
            individuals.append(individual)
        Individual.objects.bulk_update(individuals, ["phone_no_valid", "phone_no_alternative_valid"])
        individuals = []
