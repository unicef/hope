import logging

from django.core.paginator import Paginator

from hct_mis_api.apps.registration_datahub.models import (
    ImportedHousehold,
    KoboImportedSubmission,
)

logger = logging.getLogger(__name__)


def fix_kobo_imported_hh_detail_id() -> None:
    logger.info("=== Start updating Imported Households ===")

    imported_households_qs = ImportedHousehold.objects.exclude(kobo_asset_id="").filter(detail_id__isnull=True)

    logger.info(f"Found Imported Households with kobo_asset_id but without detail_id: {imported_households_qs.count()}")
    kobo_submissions = []

    paginator = Paginator(imported_households_qs.order_by("created_at"), 1000)

    for page in paginator.page_range:
        hh_for_update = []
        for imported_household in paginator.page(page).object_list:
            imported_household.detail_id = imported_household.kobo_asset_id
            hh_for_update.append(imported_household)

            # create new kobo submission if not exists
            if not imported_household.koboimportedsubmission_set.exists():
                kobo_submissions.append(
                    KoboImportedSubmission(
                        kobo_submission_uuid=imported_household.kobo_submission_uuid,
                        kobo_asset_id=imported_household.kobo_asset_id,
                        kobo_submission_time=imported_household.kobo_submission_time,
                        registration_data_import=imported_household.registration_data_import,
                        imported_household=imported_household,
                    )
                )
        ImportedHousehold.objects.bulk_update(hh_for_update, ["detail_id"])

    if kobo_submissions:
        KoboImportedSubmission.objects.bulk_create(kobo_submissions)
    logger.info(f"Created {len(kobo_submissions)} kobo submissions")
    logger.info("=== Finished updating Imported Households ===")
