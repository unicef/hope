from unittest.mock import MagicMock, call, patch

from constance.test import override_config
from elasticsearch import NotFoundError
import pytest

from extras.test_utils.factories import BusinessAreaFactory, IndividualFactory, ProgramFactory
from hope.apps.utils.elasticsearch_utils import (
    populate_all_indexes,
    populate_index,
    rebuild_search_index,
    remove_elasticsearch_documents_by_matching_ids,
)
from hope.models import BusinessArea, Individual, Program

pytestmark = [
    pytest.mark.elasticsearch,
    pytest.mark.xdist_group(name="elasticsearch"),
    pytest.mark.usefixtures("django_elasticsearch_setup"),
]


@patch("hope.apps.utils.elasticsearch_utils.connections")
@override_config(IS_ELASTICSEARCH_ENABLED=True)
def test_ensure_index_ready_healthy_green(mock_connections: MagicMock) -> None:
    from hope.apps.utils.elasticsearch_utils import ensure_index_ready

    mock_conn = MagicMock()
    mock_conn.cluster.health.return_value = {"status": "green"}
    mock_connections.get_connection.return_value = mock_conn

    ensure_index_ready("test_index")

    mock_conn.indices.refresh.assert_called_once_with(index="test_index")


@patch("hope.apps.utils.elasticsearch_utils.connections")
@override_config(IS_ELASTICSEARCH_ENABLED=True)
def test_ensure_index_ready_healthy_yellow(mock_connections: MagicMock) -> None:
    from hope.apps.utils.elasticsearch_utils import ensure_index_ready

    mock_conn = MagicMock()
    mock_conn.cluster.health.return_value = {"status": "yellow"}
    mock_connections.get_connection.return_value = mock_conn

    ensure_index_ready("test_index")

    mock_conn.indices.refresh.assert_called_once_with(index="test_index")


@patch("hope.apps.utils.elasticsearch_utils.connections")
@override_config(IS_ELASTICSEARCH_ENABLED=True)
def test_ensure_index_ready_red_raises(mock_connections: MagicMock) -> None:
    from hope.apps.utils.elasticsearch_utils import ensure_index_ready

    mock_conn = MagicMock()
    mock_conn.cluster.health.return_value = {"status": "red"}
    mock_connections.get_connection.return_value = mock_conn

    with pytest.raises(Exception, match="ES cluster is RED"):
        ensure_index_ready("test_index")


@pytest.mark.django_db
@patch("hope.apps.household.services.index_management.populate_program_indexes")
@override_config(IS_ELASTICSEARCH_ENABLED=True)
def test_populate_all_indexes_calls_per_program_and_global(mock_populate_program: MagicMock) -> None:
    ba: BusinessArea = BusinessAreaFactory()
    with override_config(IS_ELASTICSEARCH_ENABLED=False):
        program_1: Program = ProgramFactory(business_area=ba, status=Program.ACTIVE)
        program_2: Program = ProgramFactory(business_area=ba, status=Program.ACTIVE)
        ProgramFactory(business_area=ba, status=Program.DRAFT)

    populate_all_indexes()

    mock_populate_program.assert_has_calls([call(str(program_1.id)), call(str(program_2.id))], any_order=True)
    assert mock_populate_program.call_count == 2


@pytest.mark.django_db
@patch("hope.apps.household.services.index_management.populate_program_indexes")
@override_config(IS_ELASTICSEARCH_ENABLED=True)
def test_populate_all_indexes_no_active_programs(mock_populate_program: MagicMock) -> None:
    ba: BusinessArea = BusinessAreaFactory()
    ProgramFactory(business_area=ba, status=Program.DRAFT)

    populate_all_indexes()

    mock_populate_program.assert_not_called()


@pytest.mark.django_db
@patch("hope.apps.household.services.index_management.rebuild_program_indexes")
@override_config(IS_ELASTICSEARCH_ENABLED=True)
def test_rebuild_search_index_calls_per_program_and_global(mock_rebuild_program: MagicMock) -> None:
    ba: BusinessArea = BusinessAreaFactory()
    with override_config(IS_ELASTICSEARCH_ENABLED=False):
        program_1: Program = ProgramFactory(business_area=ba, status=Program.ACTIVE)
        program_2: Program = ProgramFactory(business_area=ba, status=Program.ACTIVE)
        ProgramFactory(business_area=ba, status=Program.DRAFT)

    rebuild_search_index()

    mock_rebuild_program.assert_has_calls([call(str(program_1.id)), call(str(program_2.id))], any_order=True)
    assert mock_rebuild_program.call_count == 2


@pytest.mark.django_db
@patch("hope.apps.household.services.index_management.rebuild_program_indexes")
@override_config(IS_ELASTICSEARCH_ENABLED=True)
def test_rebuild_search_index_no_active_programs(mock_rebuild_program: MagicMock) -> None:
    ba: BusinessArea = BusinessAreaFactory()
    with override_config(IS_ELASTICSEARCH_ENABLED=False):
        ProgramFactory(business_area=ba, status=Program.DRAFT)

    rebuild_search_index()

    mock_rebuild_program.assert_not_called()


@pytest.mark.django_db
@patch("hope.apps.household.services.index_management.rebuild_program_indexes")
@override_config(IS_ELASTICSEARCH_ENABLED=True)
def test_rebuild_search_index_custom_options(mock_rebuild_program: MagicMock) -> None:
    ba: BusinessArea = BusinessAreaFactory()
    with override_config(IS_ELASTICSEARCH_ENABLED=False):
        ProgramFactory(business_area=ba, status=Program.ACTIVE)

    custom_options: dict = {"parallel": True, "quiet": False}
    rebuild_search_index(options=custom_options)

    mock_rebuild_program.assert_called_once()


@override_config(IS_ELASTICSEARCH_ENABLED=True)
def test_remove_elasticsearch_documents_by_matching_ids_deletes_docs() -> None:
    mock_document = MagicMock()

    remove_elasticsearch_documents_by_matching_ids(["id-1", "id-2"], mock_document)

    mock_document.search.return_value.params.return_value.update_from_dict.return_value.delete.assert_called_once()


@override_config(IS_ELASTICSEARCH_ENABLED=True)
def test_remove_elasticsearch_documents_by_matching_ids_skips_empty_list() -> None:
    mock_document = MagicMock()

    remove_elasticsearch_documents_by_matching_ids([], mock_document)

    mock_document.search.assert_not_called()


@override_config(IS_ELASTICSEARCH_ENABLED=False)
def test_remove_elasticsearch_documents_by_matching_ids_skips_when_disabled() -> None:
    mock_document = MagicMock()

    remove_elasticsearch_documents_by_matching_ids(["id-1"], mock_document)

    mock_document.search.assert_not_called()


@override_config(IS_ELASTICSEARCH_ENABLED=True)
def test_remove_elasticsearch_documents_by_matching_ids_ignores_not_found() -> None:
    mock_document = MagicMock()
    mock_document.search.return_value.params.return_value.update_from_dict.return_value.delete.side_effect = (
        NotFoundError(message="index_not_found_exception", meta=MagicMock(), body={})
    )

    remove_elasticsearch_documents_by_matching_ids(["id-1"], mock_document)


@override_config(IS_ELASTICSEARCH_ENABLED=False)
def test_populate_index_noops_when_elasticsearch_disabled() -> None:
    mock_queryset = MagicMock()
    mock_doc = MagicMock()

    populate_index(mock_queryset, mock_doc)

    mock_queryset.iterator.assert_not_called()
    mock_doc.assert_not_called()


@pytest.fixture
def program_with_three_individuals() -> Program:
    ba: BusinessArea = BusinessAreaFactory()
    with override_config(IS_ELASTICSEARCH_ENABLED=False):
        program: Program = ProgramFactory(business_area=ba, status=Program.ACTIVE)
        IndividualFactory(program=program, business_area=ba)
        IndividualFactory(program=program, business_area=ba)
        IndividualFactory(program=program, business_area=ba)
    return program


@pytest.mark.django_db
@override_config(IS_ELASTICSEARCH_ENABLED=True)
def test_populate_index_streams_the_queryset_to_the_doc(program_with_three_individuals: Program) -> None:
    consumed: list = []
    mock_doc_class = MagicMock()
    mock_doc_class.return_value.update.side_effect = lambda rows, parallel: consumed.extend(rows)
    queryset = Individual.all_merge_status_objects.filter(program=program_with_three_individuals)

    populate_index(queryset, mock_doc_class)

    assert len(consumed) == 3


@pytest.mark.django_db
@override_config(IS_ELASTICSEARCH_ENABLED=True)
def test_populate_index_reports_progress_per_chunk_and_at_the_end(
    program_with_three_individuals: Program, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("hope.apps.utils.elasticsearch_utils.PROGRESS_EVERY", 2)
    ticks: list[int] = []
    mock_doc_class = MagicMock()
    mock_doc_class.return_value.update.side_effect = lambda rows, parallel: list(rows)
    queryset = Individual.all_merge_status_objects.filter(program=program_with_three_individuals)

    populate_index(queryset, mock_doc_class, progress_cb=ticks.append)

    assert ticks == [2, 3]
