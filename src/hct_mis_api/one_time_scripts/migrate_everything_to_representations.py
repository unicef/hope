import time

from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.household.models import Individual
from hct_mis_api.one_time_scripts.create_hh_and_ind_collections import (
    create_hh_and_ind_collections,
)
from hct_mis_api.one_time_scripts.migrate_data_to_representations import (
    migrate_data_to_representations_per_business_area,
)
from hct_mis_api.one_time_scripts.migrate_files_to_representations import (
    migrate_files_to_representations_per_business_area,
)
from hct_mis_api.one_time_scripts.migrate_grievance_to_representations import (
    migrate_grievance_to_representations_per_business_area,
)


def migrate_everything_to_representations_per_ba(ba_slug: str) -> None:
    start_time = time.time()
    ba = BusinessArea.objects.get(slug=ba_slug)
    print(f"STARTING MIGRATION FOR {ba.slug}" + "-" * 50)
    create_hh_and_ind_collections(ba)
    print(f"FINISHED CREATING COLLECTIONS FOR {ba.slug}" + "-" * 50)
    migrate_data_to_representations_per_business_area(ba)
    print(f"FINISHED MIGRATING DATA FOR {ba.slug}" + "-" * 50)
    migrate_files_to_representations_per_business_area(ba)
    print(f"FINISHED MIGRATING FILES FOR {ba.slug}" + "-" * 50)
    migrate_grievance_to_representations_per_business_area(ba)
    print(f"FINISHED MIGRATING GRIEVANCES FOR {ba.slug}" + "-" * 50)
    print(
        f"FINISHED MIGRATION FOR {ba.slug} in {time.time() - start_time} for {Individual.original_and_repr_objects.filter(business_area__slug=ba_slug).exclude(copied_from=None).count()} individuals"
        + "-" * 50
    )
