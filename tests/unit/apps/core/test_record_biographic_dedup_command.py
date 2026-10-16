import json
from pathlib import Path

from constance.test import override_config
from django.core.management import call_command
import pytest

from extras.test_utils.factories.core import BusinessAreaFactory
from extras.test_utils.factories.geo import CountryFactory
from extras.test_utils.factories.program import ProgramFactory
from hope.models import DataCollectingType, Program

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.usefixtures("django_elasticsearch_setup"),
    pytest.mark.elasticsearch,
    pytest.mark.xdist_group(name="elasticsearch"),
]

FILES_DIR = Path(__file__).resolve().parent / "test_files"


@pytest.fixture
def program(create_program_es_index) -> Program:
    afghanistan = CountryFactory(
        name="Afghanistan",
        short_name="Afghanistan",
        iso_code2="AF",
        iso_code3="AFG",
        iso_num="0004",
    )
    business_area = BusinessAreaFactory(
        slug="afghanistan",
        postpone_deduplication=False,
        office_country=afghanistan,
    )
    business_area.countries.add(afghanistan)
    program = ProgramFactory(
        business_area=business_area,
        status=Program.ACTIVE,
        data_collecting_type__type=DataCollectingType.Type.SOCIAL,
        beneficiary_group__master_detail=False,
    )
    create_program_es_index(program)
    return program


@pytest.fixture
def population_finding() -> dict:
    return {
        "first": {"reference_pk": "rdi:3"},
        "second": {"reference_pk": "population:3"},
        "score": 12.0,
        "status_code": 200,
    }


@pytest.fixture
def batch_finding() -> dict:
    return {
        "first": {"reference_pk": "rdi:4"},
        "second": {"reference_pk": "rdi:5"},
        "score": 12.0,
        "status_code": 200,
    }


@pytest.fixture
def population_ticket() -> dict:
    return {
        "issue_type": 24,
        "is_multiple_duplicates_version": True,
        "golden_records_individual": "rdi:3",
        "possible_duplicate": "rdi:3",
        "possible_duplicates": ["population:3"],
        "score_min": 12.0,
        "score_max": 12.0,
    }


# Which individual of an in-batch pair becomes golden_records_individual depends on UUID order.
@pytest.fixture
def batch_ticket_rdi_4_as_golden() -> dict:
    return {
        "issue_type": 24,
        "is_multiple_duplicates_version": True,
        "golden_records_individual": "rdi:4",
        "possible_duplicate": "rdi:4",
        "possible_duplicates": ["rdi:5"],
        "score_min": 12.0,
        "score_max": 12.0,
    }


@pytest.fixture
def batch_ticket_rdi_5_as_golden() -> dict:
    return {
        "issue_type": 24,
        "is_multiple_duplicates_version": True,
        "golden_records_individual": "rdi:5",
        "possible_duplicate": "rdi:5",
        "possible_duplicates": ["rdi:4"],
        "score_min": 12.0,
        "score_max": 12.0,
    }


@override_config(IS_ELASTICSEARCH_ENABLED=True)
def test_record_biographic_dedup_writes_findings_and_tickets_keyed_by_xlsx_row(
    program: Program,
    population_finding: dict,
    batch_finding: dict,
    population_ticket: dict,
    batch_ticket_rdi_4_as_golden: dict,
    batch_ticket_rdi_5_as_golden: dict,
    tmp_path,
) -> None:
    output = tmp_path / "recording.json"

    call_command(
        "record_biographic_dedup",
        str(program.id),
        str(FILES_DIR / "record_biographic_dedup_population.xlsx"),
        str(FILES_DIR / "record_biographic_dedup_rdi.xlsx"),
        str(output),
    )

    assert json.loads(output.read_text()) in (
        {"findings": [population_finding, batch_finding], "tickets": [population_ticket, batch_ticket_rdi_4_as_golden]},
        {"findings": [population_finding, batch_finding], "tickets": [population_ticket, batch_ticket_rdi_5_as_golden]},
    )
