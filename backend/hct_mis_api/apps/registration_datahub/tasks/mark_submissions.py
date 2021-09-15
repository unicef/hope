import operator
from functools import reduce

from django.db.models import Q

from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.registration_datahub.models import (
    ImportedHousehold,
    KoboImportedSubmission,
    RegistrationDataImportDatahub,
)


class MarkSubmissions:
    def __init__(self, business_area: BusinessArea):
        self.business_area = business_area

    def execute(self):
        # Filter rdi with status done and following business area slug
        rdi_ids = self._get_rdi_ids()
        if not rdi_ids:
            return {"message": "No suitable RDI found", "submissions": 0}

        # Filter households submissions_id for following rdi id
        submission_ids = self._get_submissions_ids(rdi_ids)
        if not submission_ids:
            return {"message": "No suitable Submissions found", "submissions": 0}

        # Exclude submissions for merged rdi
        submissions = self._get_submissions(submission_ids)
        if not submissions:
            return {"message": "No suitable (unmerged) Submissions found", "submissions": 0}

        # Mark as amended
        rows = submissions.update(amended=True)
        return {"message": f"{rows} submissions successfully amended", "submissions": rows}


    def _get_submissions(self, submission_ids):
        return KoboImportedSubmission.objects.exclude(
            reduce(operator.or_, (Q(kobo_submission_uuid=submission_id) for submission_id in submission_ids))
        )

    def _get_submissions_ids(self, rdi_ids):
        return ImportedHousehold.objects.filter(
            kobo_submission_uuid__isnull=False,
            registration_data_import__id__in=rdi_ids,
        ).values_list("kobo_submission_uuid", flat=True)

    def _get_rdi_ids(self):
        return (
            RegistrationDataImportDatahub.objects.filter(import_done=RegistrationDataImportDatahub.DONE)
            .filter(business_area_slug=self.business_area.slug)
            .values_list("id", flat=True)
        )
