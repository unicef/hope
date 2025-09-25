from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models

from hope.models.utils import TimeStampedUUIDModel


class XlsxUpdateFile(TimeStampedUUIDModel):
    file = models.FileField()
    business_area = models.ForeignKey("core.BusinessArea", on_delete=models.CASCADE)
    rdi = models.ForeignKey("registration_data.RegistrationDataImport", on_delete=models.CASCADE, null=True)
    xlsx_match_columns = ArrayField(models.CharField(max_length=32), null=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.PROTECT)
    program = models.ForeignKey("program.Program", null=True, on_delete=models.CASCADE)

    class Meta:
        app_label = "household"
