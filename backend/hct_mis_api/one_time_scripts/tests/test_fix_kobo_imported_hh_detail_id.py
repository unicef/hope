from django.core.management import call_command

from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.registration_datahub.fixtures import ImportedHouseholdFactory
from hct_mis_api.apps.registration_datahub.models import (
    ImportedHousehold,
    KoboImportedSubmission,
)
from hct_mis_api.one_time_scripts.fix_kobo_imported_hh_detail_id import (
    fix_kobo_imported_hh_detail_id,
)


class TestFixKoboHhDetailId(APITestCase):
    databases = {"default", "registration_datahub"}
    @classmethod
    def setUpTestData(cls) -> None:
        create_afghanistan()
        call_command("loadcountries")
        ImportedHouseholdFactory(
            kobo_submission_uuid="6bb78c41-da41-47e2-9b4e-27dfbd7e7777",
            kobo_asset_id="aD3dSDiFoASn7CAtBS3h33",
            kobo_submission_time="2033-11-11T11:33:33",
            detail_id=None,
        )

    def test_update_hh_details(self) -> None:
        assert KoboImportedSubmission.objects.count() == 0
        assert ImportedHousehold.objects.exclude(kobo_asset_id="").filter(detail_id__isnull=True).count() == 1

        # update ImportedHousehold detail_id
        fix_kobo_imported_hh_detail_id()

        assert KoboImportedSubmission.objects.count() == 1
        assert ImportedHousehold.objects.exclude(kobo_asset_id="").filter(detail_id__isnull=True).count() == 0

        kobo_imported_submission = KoboImportedSubmission.objects.first()
        imported_hh = ImportedHousehold.objects.first()

        assert kobo_imported_submission.imported_household == imported_hh
        assert kobo_imported_submission.kobo_submission_uuid == imported_hh.kobo_submission_uuid
        assert kobo_imported_submission.kobo_asset_id == imported_hh.kobo_asset_id
        assert kobo_imported_submission.kobo_submission_time == imported_hh.kobo_submission_time
        assert kobo_imported_submission.registration_data_import == imported_hh.registration_data_import
