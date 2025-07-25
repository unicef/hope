from typing import TYPE_CHECKING

from django.core.management import call_command

import responses

from hct_mis_api.apps.sanction_list.celery_tasks import sync_sanction_list_task
from hct_mis_api.apps.sanction_list.models import SanctionListIndividual

if TYPE_CHECKING:
    from responses import RequestsMock

    from hct_mis_api.apps.sanction_list.models import SanctionList


def test_sync_sanction_list_task(
    mocked_responses: "RequestsMock", sanction_list: "SanctionList", eu_file: bytes
) -> None:
    call_command("loadcountries")
    mocked_responses.add(responses.GET, "http://example.com/sl.xml", body=eu_file, status=200)
    sync_sanction_list_task.apply_async()
    assert SanctionListIndividual.objects.count() == 2
