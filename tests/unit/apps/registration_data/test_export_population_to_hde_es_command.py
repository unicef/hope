from collections.abc import Generator
from datetime import date
from io import StringIO
from typing import Any
from unittest import mock
from unittest.mock import patch

from django.core.management import call_command
from django.core.management.base import CommandError
import pytest

from extras.test_utils.factories import BusinessAreaFactory, IndividualFactory, ProgramFactory
from hope.models import BusinessArea, Individual, MergeStatusModel, Program

pytestmark = pytest.mark.django_db

COMMAND_MODULE = "hope.apps.registration_data.management.commands.export_population_to_hde_es"
ES_HOST = "https://hde-es.test:9200"


@pytest.fixture
def es_client_class(monkeypatch: pytest.MonkeyPatch) -> Generator[mock.MagicMock]:
    monkeypatch.setenv("HDE_ELASTICSEARCH_HOST", ES_HOST)
    with patch(f"{COMMAND_MODULE}.Elasticsearch") as client_class:
        client_class.return_value.indices.exists.return_value = True
        client_class.return_value.indices.get_mapping.side_effect = lambda index: {
            index: {"mappings": {"properties": {"dataset_id": {"type": "keyword"}, "status": {"type": "keyword"}}}}
        }
        yield client_class


@pytest.fixture
def es_client(es_client_class: mock.MagicMock) -> mock.MagicMock:
    return es_client_class.return_value


@pytest.fixture
def written_actions() -> Generator[list[dict]]:
    actions: list[dict] = []

    def consume(client: Any, generator: Any, **kwargs: Any) -> tuple[int, list]:
        batch = list(generator)
        actions.extend(batch)
        return len(batch), []

    with patch(f"{COMMAND_MODULE}.bulk", side_effect=consume):
        yield actions


@pytest.fixture
def afghanistan() -> BusinessArea:
    return BusinessAreaFactory(slug="afghanistan", name="Afghanistan")


@pytest.fixture
def ukraine_individual() -> Individual:
    ukraine = BusinessAreaFactory(slug="ukraine", name="Ukraine")
    ukraine_program = ProgramFactory(business_area=ukraine, code="gh78")
    return IndividualFactory(business_area=ukraine, program=ukraine_program)


@pytest.fixture
def program(afghanistan: BusinessArea) -> Program:
    return ProgramFactory(business_area=afghanistan, code="ab12")


@pytest.fixture
def other_program(afghanistan: BusinessArea) -> Program:
    return ProgramFactory(business_area=afghanistan, code="cd34")


@pytest.fixture
def individual(program: Program) -> Individual:
    return IndividualFactory(
        business_area=program.business_area,
        program=program,
        given_name="Amina",
        family_name="Yusuf",
        full_name="Amina Yusuf",
        middle_name="",
        birth_date=date(1990, 4, 12),
        phone_no="+48500100200",
        phone_no_alternative="",
        sex="FEMALE",
        relationship="HEAD",
    )


@pytest.fixture
def finished_program_individual(afghanistan: BusinessArea) -> Individual:
    finished_program = ProgramFactory(business_area=afghanistan, code="ef56", status=Program.FINISHED)
    return IndividualFactory(business_area=afghanistan, program=finished_program)


@pytest.fixture
def cw_individual(program: Program) -> Individual:
    return IndividualFactory(business_area=program.business_area, program=program, country_workspace_id="cw-17")


@pytest.fixture
def not_exported_individuals(program: Program) -> list[Individual]:
    return [
        IndividualFactory(
            business_area=program.business_area, program=program, rdi_merge_status=MergeStatusModel.PENDING
        ),
        IndividualFactory(business_area=program.business_area, program=program, is_removed=True),
        IndividualFactory(business_area=program.business_area, program=program, withdrawn=True),
    ]


@pytest.fixture
def other_program_individual(other_program: Program) -> Individual:
    return IndividualFactory(business_area=other_program.business_area, program=other_program)


def test_export_writes_individual_as_approved_hde_document(
    es_client: mock.MagicMock, written_actions: list[dict], individual: Individual
) -> None:
    call_command("export_population_to_hde_es", business_areas=["afghanistan"], index_prefix="dev_")

    assert written_actions == [
        {
            "_index": "dev_biographic_afghanistan_ab12",
            "_id": f"0:{individual.id}",
            "_source": {
                "reference_pk": str(individual.id),
                "dataset_id": "0",
                "business_area": "afghanistan",
                "program_code": "ab12",
                "status": "approved",
                "birth_date": "1990-04-12",
                "given_name": "Amina",
                "family_name": "Yusuf",
                "full_name": "Amina Yusuf",
                "middle_name": "",
                "sex": "FEMALE",
                "relationship": "HEAD",
                "phone_no": "+48500100200",
                "phone_no_alternative": "",
            },
        }
    ]
    es_client.indices.refresh.assert_called_once_with(index="dev_biographic_afghanistan_ab12")


def test_export_uses_country_workspace_id_as_reference_pk_when_set(
    es_client: mock.MagicMock, written_actions: list[dict], cw_individual: Individual
) -> None:
    call_command("export_population_to_hde_es", business_areas=["afghanistan"])

    assert [(action["_id"], action["_source"]["reference_pk"]) for action in written_actions] == [("0:cw-17", "cw-17")]


def test_export_skips_pending_removed_and_withdrawn_individuals(
    es_client: mock.MagicMock,
    written_actions: list[dict],
    individual: Individual,
    not_exported_individuals: list[Individual],
) -> None:
    call_command("export_population_to_hde_es", business_areas=["afghanistan"])

    assert [action["_source"]["reference_pk"] for action in written_actions] == [str(individual.id)]


def test_export_of_several_business_areas_writes_each_population_to_its_index(
    es_client: mock.MagicMock,
    written_actions: list[dict],
    individual: Individual,
    ukraine_individual: Individual,
) -> None:
    call_command("export_population_to_hde_es", business_areas=["afghanistan", "ukraine"])

    assert [(action["_index"], action["_source"]["reference_pk"]) for action in written_actions] == [
        ("biographic_afghanistan_ab12", str(individual.id)),
        ("biographic_ukraine_gh78", str(ukraine_individual.id)),
    ]


def test_export_limited_to_program_writes_only_its_population(
    es_client: mock.MagicMock,
    written_actions: list[dict],
    individual: Individual,
    other_program_individual: Individual,
) -> None:
    call_command("export_population_to_hde_es", business_areas=["afghanistan"], program="cd34")

    assert [action["_index"] for action in written_actions] == ["biographic_afghanistan_cd34"]


def test_export_does_not_check_index_of_program_without_population(
    es_client: mock.MagicMock, written_actions: list[dict], individual: Individual, other_program: Program
) -> None:
    call_command("export_population_to_hde_es", business_areas=["afghanistan"])

    es_client.indices.exists.assert_called_once_with(index="biographic_afghanistan_ab12")


def test_export_stops_before_writing_when_any_hde_index_is_missing(
    es_client: mock.MagicMock,
    written_actions: list[dict],
    individual: Individual,
    other_program_individual: Individual,
) -> None:
    es_client.indices.exists.side_effect = lambda index: index == "biographic_afghanistan_ab12"

    with pytest.raises(CommandError, match="biographic_afghanistan_cd34"):
        call_command("export_population_to_hde_es", business_areas=["afghanistan"])

    assert written_actions == []


def test_export_of_several_business_areas_writes_nothing_when_index_of_one_is_missing(
    es_client: mock.MagicMock,
    written_actions: list[dict],
    individual: Individual,
    ukraine_individual: Individual,
) -> None:
    es_client.indices.exists.side_effect = lambda index: index == "biographic_afghanistan_ab12"

    with pytest.raises(CommandError, match="biographic_ukraine_gh78"):
        call_command("export_population_to_hde_es", business_areas=["afghanistan", "ukraine"])

    assert written_actions == []


@pytest.mark.parametrize(
    ("properties", "problem"),
    [
        # An index HDE created before its set ids became UUIDs.
        (
            {"dataset_id": {"type": "long"}, "status": {"type": "keyword"}},
            "biographic_afghanistan_ab12 maps dataset_id as long",
        ),
        # A field missing from the mapping, as in an index Elasticsearch created on its own from a write.
        ({"dataset_id": {"type": "keyword"}}, "biographic_afghanistan_ab12 maps status as nothing"),
    ],
)
def test_export_stops_before_writing_when_hde_index_has_outdated_mapping(
    es_client: mock.MagicMock, written_actions: list[dict], individual: Individual, properties: dict, problem: str
) -> None:
    es_client.indices.get_mapping.side_effect = lambda index: {index: {"mappings": {"properties": properties}}}

    with pytest.raises(CommandError) as error:
        call_command("export_population_to_hde_es", business_areas=["afghanistan"])

    assert str(error.value).endswith(f"Nothing was written: {problem}")
    assert written_actions == []


def test_export_dry_run_reports_count_and_writes_nothing(
    es_client: mock.MagicMock, written_actions: list[dict], individual: Individual
) -> None:
    stdout = StringIO()

    call_command("export_population_to_hde_es", business_areas=["afghanistan"], dry_run=True, stdout=stdout)

    assert stdout.getvalue() == "ab12: 1 individuals would be written to biographic_afghanistan_ab12\n"
    assert written_actions == []
    es_client.indices.refresh.assert_not_called()


def test_export_skips_programs_that_are_not_active(
    es_client: mock.MagicMock,
    written_actions: list[dict],
    individual: Individual,
    finished_program_individual: Individual,
) -> None:
    call_command("export_population_to_hde_es", business_areas=["afghanistan"])

    es_client.indices.exists.assert_called_once_with(index="biographic_afghanistan_ab12")
    assert [action["_index"] for action in written_actions] == ["biographic_afghanistan_ab12"]


def test_export_without_population_reports_nothing_to_export(
    es_client_class: mock.MagicMock, written_actions: list[dict], program: Program
) -> None:
    stdout = StringIO()

    call_command("export_population_to_hde_es", business_areas=["afghanistan"], stdout=stdout)

    assert stdout.getvalue() == "Nothing to export: no active program in afghanistan has a population.\n"
    es_client_class.assert_not_called()


def test_export_reads_es_host_from_environment(
    es_client_class: mock.MagicMock, written_actions: list[dict], individual: Individual
) -> None:
    call_command("export_population_to_hde_es", business_areas=["afghanistan"])

    assert es_client_class.call_args.kwargs["hosts"] == [ES_HOST]


def test_export_without_es_host_raises(afghanistan: BusinessArea, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("HDE_ELASTICSEARCH_HOST", raising=False)

    with pytest.raises(CommandError, match="HDE Elasticsearch host missing"):
        call_command("export_population_to_hde_es", business_areas=["afghanistan"])


def test_export_rejects_unknown_business_area(es_client: mock.MagicMock, afghanistan: BusinessArea) -> None:
    with pytest.raises(CommandError, match="Unknown business area slugs: nowhere"):
        call_command("export_population_to_hde_es", business_areas=["afghanistan", "nowhere"])


def test_export_rejects_unknown_program(es_client: mock.MagicMock, program: Program) -> None:
    with pytest.raises(CommandError, match="No active program with code zz99 in afghanistan"):
        call_command("export_population_to_hde_es", business_areas=["afghanistan"], program="zz99")
