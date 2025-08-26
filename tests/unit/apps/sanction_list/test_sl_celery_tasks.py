import responses
from django.core.management import call_command

from hope.apps.sanction_list.celery_tasks import sync_sanction_list_task
from hope.models.sanction_list import SanctionListIndividual


def test_sync_sanction_list_task(
    mocked_responses: "RequestsMock", sanction_list: "SanctionList", eu_file: bytes
) -> None:
    call_command("loadcountries")
    mocked_responses.add(responses.GET, "http://example.com/sl.xml", body=eu_file, status=200)
    sync_sanction_list_task.apply_async()
    assert SanctionListIndividual.objects.count() == 2
