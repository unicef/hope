from uuid import UUID

from django.db import transaction
from django.db.models import QuerySet

from hope.apps.core.models import BusinessArea
from hope.apps.household.models import Household
from hope.apps.registration_data.models import (
    KoboImportedSubmission,
    RegistrationDataImport,
)


class MarkSubmissions:
    def __init__(self, business_area: BusinessArea) -> None:
        self.business_area = business_area

    def execute(self) -> dict:
        # Filter rdi with status done and following business area slug
        datahub_ids = self._get_datahub_ids()

        # Filter households submissions_id for following rdi id
        submission_ids = self._get_submissions_ids(datahub_ids)

        # Exclude submissions for merged rdi
        submissions = self._get_submissions(submission_ids)
        if not submissions:
            return {
                "message": "No suitable (unmerged) Submissions found",
                "submissions": 0,
            }

        # Mark as amended
        with transaction.atomic():
            rows = submissions.update(amended=True)
            return {
                "message": f"{rows} submissions successfully amended",
                "submissions": rows,
            }

    def _get_submissions(self, submission_ids: list[UUID]) -> QuerySet[KoboImportedSubmission]:
        return KoboImportedSubmission.objects.exclude(kobo_submission_uuid__in=list(submission_ids))

    def _get_submissions_ids(self, datahub_ids: QuerySet) -> list[UUID]:
        return list(
            Household.objects.filter(
                kobo_submission_uuid__isnull=False,
                registration_data_import__id__in=list(datahub_ids),
            ).values_list("kobo_submission_uuid", flat=True)
        )

    def _get_datahub_ids(self) -> QuerySet[RegistrationDataImport]:
        return (
            RegistrationDataImport.objects.filter(status=RegistrationDataImport.MERGED)
            .filter(business_area=self.business_area)
            .values_list("id", flat=True)
        )
