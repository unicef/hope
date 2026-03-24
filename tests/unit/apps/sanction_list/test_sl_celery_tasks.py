from typing import TYPE_CHECKING

import responses

from extras.test_utils.factories import CountryFactory
from hope.apps.sanction_list.celery_tasks import sync_sanction_list_task
from hope.models import SanctionList, SanctionListIndividual

if TYPE_CHECKING:
    from responses import RequestsMock


def test_sync_sanction_list_task(mocked_responses: "RequestsMock", sanction_list: SanctionList, eu_file: bytes) -> None:
    sanction_list: SanctionList = SanctionList.objects.all().first()
    assert sanction_list is not None
    CountryFactory(name="Afghanistan", short_name="Afghanistan", iso_code2="AF", iso_code3="AFG", iso_num="0004")
    mocked_responses.add(responses.GET, "http://example.com/sl.xml", body=eu_file, status=200)
    sync_sanction_list_task.apply_async()
    assert SanctionListIndividual.objects.count() == 2
