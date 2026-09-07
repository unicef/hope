"""Live-Elasticsearch test for es_populate_delta.

The mocked tests in test_es_populate_delta.py never reach a real client (a MagicMock doc
accepts any kwarg), so a bad argument forwarded into bulk() slips straight through them.
This file keeps ONE end-to-end run against the real cluster to catch exactly that class
of bug: real DB rows, real command, real bulk() write, real search-side assertions.
"""

from typing import Any

from constance.test import override_config
from django.conf import settings
from django.core.management import call_command
from django.utils import timezone
from elasticsearch import Elasticsearch
import pytest

from extras.test_utils.factories import BusinessAreaFactory, HouseholdFactory, IndividualFactory, ProgramFactory
from hope.apps.household.documents import get_household_doc, get_individual_doc
from hope.apps.household.services.index_management import populate_program_indexes
from hope.models import BusinessArea, Household, Individual, Program

pytestmark = [
    pytest.mark.elasticsearch,
    pytest.mark.xdist_group(name="elasticsearch"),
    pytest.mark.usefixtures("django_elasticsearch_setup"),
]


@pytest.fixture
def delta_program() -> dict:
    with override_config(IS_ELASTICSEARCH_ENABLED=False):
        ba: BusinessArea = BusinessAreaFactory()
        program: Program = ProgramFactory(business_area=ba, status=Program.ACTIVE)
        household: Household = HouseholdFactory(program=program, business_area=ba)
        other: Individual = IndividualFactory(program=program, business_area=ba, household=household)
    return {"program": program, "household": household, "head": household.head_of_household, "other": other}


@pytest.mark.django_db
@override_config(IS_ELASTICSEARCH_ENABLED=True)
def test_delta_upserts_changed_and_removes_soft_deleted(delta_program: dict, create_program_es_index: Any) -> None:
    program: Program = delta_program["program"]
    head: Individual = delta_program["head"]
    create_program_es_index(program)
    populate_program_indexes(str(program.id))
    ind_index = get_individual_doc(str(program.id))._index._name
    hh_index = get_household_doc(str(program.id))._index._name
    since = timezone.now()
    with override_config(IS_ELASTICSEARCH_ENABLED=False):
        head.given_name = "DeltaChanged"
        head.save()
        delta_program["other"].delete()

    call_command("es_populate_delta", since=since.isoformat(), program=str(program.id))

    es = Elasticsearch(settings.ELASTICSEARCH_HOST)
    es.indices.refresh(index=[ind_index, hh_index])
    assert es.get_source(index=ind_index, id=str(head.id))["given_name"] == "DeltaChanged"
    assert not es.exists(index=ind_index, id=str(delta_program["other"].id))
    assert es.get_source(index=hh_index, id=str(delta_program["household"].id))["head_of_household"]["given_name"] == (
        "DeltaChanged"
    )
