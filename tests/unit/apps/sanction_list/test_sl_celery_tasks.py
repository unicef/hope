from typing import TYPE_CHECKING

from django.core.management import call_command
import pytest
import responses

from hope.apps.sanction_list.celery_tasks import sync_sanction_list_task
from hope.models.sanction_list import SanctionList
from hope.models.sanction_list_individual import SanctionListIndividual

if TYPE_CHECKING:
    from responses import RequestsMock


@pytest.mark.xfail(reason="Failing In ONEMODEL xD")
# def test_sync_sanction_list_task(
#     mocked_responses: "RequestsMock", sanction_list, eu_file: bytes
# ) -> None:
def test_sync_sanction_list_task(mocked_responses: "RequestsMock", eu_file: bytes) -> None:
    sanction_list: SanctionList = SanctionList.objects.all().first()
    assert sanction_list is not None
    call_command("loadcountries")
    mocked_responses.add(responses.GET, "http://example.com/sl.xml", body=eu_file, status=200)
    sync_sanction_list_task.apply_async()
    # TODO: why we have here 2 SanctionListIndividual??
    assert SanctionListIndividual.objects.count() == 2
