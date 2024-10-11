import json
import operator
import time
from io import BytesIO
from typing import Dict

from django.core.files import File
from django.db import transaction

from hct_mis_api.apps.core.kobo.api import KoboAPI
from hct_mis_api.apps.core.kobo.common import count_population
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.registration_data.models import KoboImportData
from hct_mis_api.apps.registration_datahub.validators import (
    KoboProjectImportDataInstanceValidator,
)


class PullKoboSubmissions:
    @transaction.atomic()
    def execute(self, kobo_import_data: KoboImportData, program: Program) -> Dict:
        kobo_import_data.status = KoboImportData.STATUS_RUNNING
        kobo_import_data.save()
        kobo_api = KoboAPI(kobo_import_data.business_area_slug)
        submissions = kobo_api.get_project_submissions(
            kobo_import_data.kobo_asset_id, kobo_import_data.only_active_submissions
        )
        business_area = BusinessArea.objects.get(slug=kobo_import_data.business_area_slug)
        validator = KoboProjectImportDataInstanceValidator(program)
        skip_validate_pictures = kobo_import_data.pull_pictures is False
        validation_errors = validator.validate_everything(submissions, business_area, skip_validate_pictures)

        number_of_households, number_of_individuals = count_population(submissions, business_area)

        import_file_name = f"project-uid-{kobo_import_data.kobo_asset_id}-{time.time()}.json"
        file = File(BytesIO(json.dumps(submissions).encode()), name=import_file_name)
        kobo_import_data.file = file
        kobo_import_data.save()
        if validation_errors:
            validation_errors.sort(key=operator.itemgetter("header"))
            kobo_import_data.validation_errors = json.dumps(validation_errors)
            kobo_import_data.status = KoboImportData.STATUS_VALIDATION_ERROR
        else:
            kobo_import_data.status = KoboImportData.STATUS_FINISHED
        kobo_import_data.number_of_households = number_of_households
        kobo_import_data.number_of_individuals = number_of_individuals
        kobo_import_data.save()
        return {"kobo_import_data_id": kobo_import_data.id}
