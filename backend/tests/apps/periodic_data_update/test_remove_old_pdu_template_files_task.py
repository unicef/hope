from datetime import timedelta
from tempfile import NamedTemporaryFile

from django.contrib.admin.options import get_content_type_for_model
from django.core.files.base import ContentFile
from django.utils import timezone

import pytest

from hct_mis_api.apps.account.fixtures import BusinessAreaFactory
from hct_mis_api.apps.core.models import FileTemp
from hct_mis_api.apps.periodic_data_update.celery_tasks import (
    remove_old_pdu_template_files_task,
)
from hct_mis_api.apps.periodic_data_update.fixtures import (
    PeriodicDataUpdateTemplateFactory,
)
from hct_mis_api.apps.periodic_data_update.models import PeriodicDataUpdateTemplate

pytestmark = pytest.mark.django_db


class TestRemoveOldPDUTemplateFilesTask:
    def set_up(self, afghanistan: BusinessAreaFactory) -> None:
        self.afghanistan = afghanistan
        self.pdu_template1 = PeriodicDataUpdateTemplateFactory()
        self.pdu_template1.refresh_from_db()
        self.pdu_template2 = PeriodicDataUpdateTemplateFactory()
        self.pdu_template3 = PeriodicDataUpdateTemplateFactory()

        # Save files with different creation dates
        self._create_file(self.pdu_template1, days_ago=10)  # Recent file
        self._create_file(self.pdu_template2, days_ago=35)  # Old file
        self._create_file(self.pdu_template3, days_ago=40)  # Older file

    def _create_file(self, pdu_template: PeriodicDataUpdateTemplate, days_ago: int) -> None:
        filename = f"Test File {pdu_template.pk}.xlsx"
        file_content = b"Test content"
        file_temp = NamedTemporaryFile(delete=False)
        file_temp.write(file_content)
        file_temp.flush()

        creation_time = timezone.now() - timedelta(days=days_ago)
        file = FileTemp.objects.create(
            object_id=pdu_template.pk,
            content_type=get_content_type_for_model(pdu_template),
            created=creation_time,
            file=ContentFile(file_content, filename),
        )
        pdu_template.file = file
        pdu_template.status = PeriodicDataUpdateTemplate.Status.EXPORTED
        pdu_template.save()

    def test_remove_old_pdu_template_files_task(self, afghanistan: BusinessAreaFactory) -> None:
        self.set_up(afghanistan)

        assert self.pdu_template1.file is not None  # Not older than 30 days
        assert self.pdu_template2.file is not None  # Older than 30 days
        assert self.pdu_template3.file is not None  # Older than 30 days

        assert self.pdu_template1.status == PeriodicDataUpdateTemplate.Status.EXPORTED
        assert self.pdu_template2.status == PeriodicDataUpdateTemplate.Status.EXPORTED
        assert self.pdu_template3.status == PeriodicDataUpdateTemplate.Status.EXPORTED

        remove_old_pdu_template_files_task()

        self.pdu_template1.refresh_from_db()
        self.pdu_template2.refresh_from_db()
        self.pdu_template3.refresh_from_db()

        assert self.pdu_template1.file is not None  # Not older than 30 days
        assert self.pdu_template2.file is None  # Older than 30 days
        assert self.pdu_template3.file is None  # Older than 30 days

        assert self.pdu_template1.status == PeriodicDataUpdateTemplate.Status.EXPORTED
        assert self.pdu_template2.status == PeriodicDataUpdateTemplate.Status.TO_EXPORT
        assert self.pdu_template3.status == PeriodicDataUpdateTemplate.Status.TO_EXPORT

        assert self.pdu_template1.can_export is False
        assert self.pdu_template2.can_export is True
        assert self.pdu_template3.can_export is True
