from constance.test import override_config
from django.conf import settings

from core.base_test_case import BaseElasticSearchTestCase
from sanction_list.tasks.load_xml import LoadSanctionListXMLTask


@override_config(
    SANCTION_LIST_MATCH_SCORE=10,
)
class TestBatchDeduplication(BaseElasticSearchTestCase):
    multi_db = True

    TEST_FILES_PATH = f"{settings.PROJECT_ROOT}/apps/sanction_list/tests/test_files"

    @classmethod
    def setUpTestData(cls):
        full_sanction_list_path = f"{cls.TEST_FILES_PATH}/full_sanction_list.xml"
        task = LoadSanctionListXMLTask(full_sanction_list_path)
        task.execute()
        cls.rebuild_search_index()

    def test_execute(self):
        pass
