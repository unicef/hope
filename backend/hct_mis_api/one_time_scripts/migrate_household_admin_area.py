from django.core.paginator import Paginator

from hct_mis_api.apps.household.models import Household
from hct_mis_api.apps.registration_datahub.models import ImportedHousehold


def migrate_household_admin_area() -> None:
    queryset = Household.objects.all().order_by("pk")
    paginator = Paginator(queryset, 10000)
    queryset_count = queryset.count()
    for page_number in paginator.page_range:
        print(f"Processing page {page_number}/{queryset_count/10000}")
        page = paginator.page(page_number)
        for household in page.object_list:
            if household.admin_area:
                household.set_admin_areas()


def migrate_imported_household_admin_area() -> None:
    queryset = ImportedHousehold.objects.all().order_by("pk")
    paginator = Paginator(queryset, 10000)
    queryset_count = queryset.count()
    for page_number in paginator.page_range:
        to_update = []
        print(f"Processing page {page_number}/{queryset_count/10000}")
        page = paginator.page(page_number)
        for imported_household in page.object_list:
            if imported_household.admin2:
                imported_household.admin_area = imported_household.admin2
                imported_household.admin_area_title = imported_household.admin2_title
            elif imported_household.admin1:
                imported_household.admin_area = imported_household.admin1
                imported_household.admin_area_title = imported_household.admin1_title
            else:
                continue

            to_update.append(imported_household)

        ImportedHousehold.objects.bulk_update(to_update, ["admin_area", "admin_area_title"])
