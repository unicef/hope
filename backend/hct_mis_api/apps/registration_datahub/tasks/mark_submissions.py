from typing import Dict, List

from django.db import transaction
from django.db.models import QuerySet

from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.registration_data.models import RegistrationDataImport
from hct_mis_api.apps.registration_datahub.models import (
    ImportedHousehold,
    KoboImportedSubmission,
)


class MarkSubmissions:
    def __init__(self, business_area: BusinessArea):
        self.business_area = business_area

    def execute(self) -> Dict:
        # Filter rdi with status done and following business area slug
        datahub_ids = self._get_datahub_ids()

        # Filter households submissions_id for following rdi id
        submission_ids = self._get_submissions_ids(datahub_ids)

        # Exclude submissions for merged rdi
        submissions = self._get_submissions(submission_ids)
        if not submissions:
            return {"message": "No suitable (unmerged) Submissions found", "submissions": 0}

        # Mark as amended
        with transaction.atomic(using="registration_datahub"):
            rows = submissions.update(amended=True)
            return {"message": f"{rows} submissions successfully amended", "submissions": rows}

    def _get_submissions(self, submission_ids) -> QuerySet[KoboImportedSubmission]:
        return KoboImportedSubmission.objects.exclude(kobo_submission_uuid__in=list(submission_ids))

    def _get_submissions_ids(self, datahub_ids) -> List:
        return ImportedHousehold.objects.filter(
            kobo_submission_uuid__isnull=False,
            registration_data_import__id__in=list(datahub_ids),
        ).values_list("kobo_submission_uuid", flat=True)

    def _get_datahub_ids(self) -> QuerySet[RegistrationDataImport]:
        return (
            RegistrationDataImport.objects.filter(status=RegistrationDataImport.MERGED)
            .filter(business_area=self.business_area)
            .values_list("datahub_id", flat=True)
        )
