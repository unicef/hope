from django.db import models

from hope.models.import_data import ImportData


class KoboImportData(ImportData):
    kobo_asset_id = models.CharField(max_length=100)
    only_active_submissions = models.BooleanField(default=True)
    pull_pictures = models.BooleanField(default=True)

    class Meta:
        app_label = "registration_data"
