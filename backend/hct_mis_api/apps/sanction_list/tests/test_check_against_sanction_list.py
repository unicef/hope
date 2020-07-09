from io import BytesIO
from pathlib import Path

from django.core import mail
from django.core.files import File
from django.test import TestCase
from django.conf import settings

from sanction_list.models import UploadedXLSXFile
from sanction_list.tasks.check_against_sanction_list import (
    CheckAgainstSanctionListTask,
)
from sanction_list.tasks.load_xml import LoadSanctionListXMLTask


class TestCheckAgainstSanctionList(TestCase):
    TEST_FILES_PATH = (
        f"{settings.PROJECT_ROOT}/apps/sanction_list/tests/test_files"
    )

    @classmethod
    def setUpTestData(cls):
        full_sanction_list_path = (
            f"{cls.TEST_FILES_PATH}/full_sanction_list.xml"
        )
        task = LoadSanctionListXMLTask(full_sanction_list_path)
        task.execute()

    def test_check_against_sanction_list(self):
        content = Path(
            f"{self.TEST_FILES_PATH}/TestSanctionList.xlsx"
        ).read_bytes()
        file = File(BytesIO(content), name="TestSanctionList.xlsx")
        uploaded_file_obj = UploadedXLSXFile.objects.create(
            file=file, associated_email="wnosal@outlook.com"
        )
        task = CheckAgainstSanctionListTask()
        task.execute(str(uploaded_file_obj.id))

        self.assertEqual(len(mail.outbox), 1)

        message = mail.outbox[0].body
        self.assertIn("Found 5 matching results.", message)
        self.assertIn("ABDULLAH YAHYA  AL HAKIM", message)
        self.assertIn("CHO CHUN RYONG", message)
        self.assertIn("Date of birth: July 17, 1964", message)
