from unittest.mock import MagicMock, call, patch

import pytest

from extras.test_utils.factories import BusinessAreaFactory, ProgramFactory
from hope.apps.utils.elasticsearch_utils import delete_all_indexes, populate_all_indexes, rebuild_search_index
from hope.models import BusinessArea, Program


@patch("hope.apps.utils.elasticsearch_utils.connections")
def test_ensure_index_ready_healthy_green(mock_connections: MagicMock) -> None:
    from hope.apps.utils.elasticsearch_utils import ensure_index_ready

    mock_conn = MagicMock()
    mock_conn.cluster.health.return_value = {"status": "green"}
    mock_connections.get_connection.return_value = mock_conn

    ensure_index_ready("test_index")

    mock_conn.indices.refresh.assert_called_once_with(index="test_index")


@patch("hope.apps.utils.elasticsearch_utils.connections")
def test_ensure_index_ready_healthy_yellow(mock_connections: MagicMock) -> None:
    from hope.apps.utils.elasticsearch_utils import ensure_index_ready

    mock_conn = MagicMock()
    mock_conn.cluster.health.return_value = {"status": "yellow"}
    mock_connections.get_connection.return_value = mock_conn

    ensure_index_ready("test_index")

    mock_conn.indices.refresh.assert_called_once_with(index="test_index")


@patch("hope.apps.utils.elasticsearch_utils.connections")
def test_ensure_index_ready_red_raises(mock_connections: MagicMock) -> None:
    from hope.apps.utils.elasticsearch_utils import ensure_index_ready

    mock_conn = MagicMock()
    mock_conn.cluster.health.return_value = {"status": "red"}
    mock_connections.get_connection.return_value = mock_conn

    with pytest.raises(Exception, match="ES cluster is RED"):
        ensure_index_ready("test_index")


@pytest.mark.django_db
@patch("hope.apps.utils.elasticsearch_utils._populate")
@patch("hope.apps.household.index_management.populate_program_indexes")
def test_populate_all_indexes_calls_per_program_and_global(
    mock_populate_program: MagicMock, mock_populate: MagicMock
) -> None:
    ba: BusinessArea = BusinessAreaFactory()
    program_1: Program = ProgramFactory(business_area=ba, status=Program.ACTIVE)
    program_2: Program = ProgramFactory(business_area=ba, status=Program.ACTIVE)
    ProgramFactory(business_area=ba, status=Program.DRAFT)

    populate_all_indexes()

    mock_populate_program.assert_has_calls([call(str(program_1.id)), call(str(program_2.id))], any_order=True)
    assert mock_populate_program.call_count == 2
    mock_populate.assert_called_once_with(models=None, options={"parallel": False, "quiet": True})


@pytest.mark.django_db
@patch("hope.apps.utils.elasticsearch_utils._populate")
@patch("hope.apps.household.index_management.populate_program_indexes")
def test_populate_all_indexes_no_active_programs(mock_populate_program: MagicMock, mock_populate: MagicMock) -> None:
    ba: BusinessArea = BusinessAreaFactory()
    ProgramFactory(business_area=ba, status=Program.DRAFT)

    populate_all_indexes()

    mock_populate_program.assert_not_called()
    mock_populate.assert_called_once_with(models=None, options={"parallel": False, "quiet": True})


@pytest.mark.django_db
@patch("hope.apps.utils.elasticsearch_utils._delete")
@patch("hope.apps.household.index_management.delete_program_indexes")
def test_delete_all_indexes_calls_per_program_and_global(
    mock_delete_program: MagicMock, mock_delete: MagicMock
) -> None:
    ba: BusinessArea = BusinessAreaFactory()
    program_1: Program = ProgramFactory(business_area=ba, status=Program.ACTIVE)
    program_2: Program = ProgramFactory(business_area=ba, status=Program.ACTIVE)
    ProgramFactory(business_area=ba, status=Program.DRAFT)

    delete_all_indexes()

    mock_delete_program.assert_has_calls([call(str(program_1.id)), call(str(program_2.id))], any_order=True)
    assert mock_delete_program.call_count == 2
    mock_delete.assert_called_once_with(models=None)


@pytest.mark.django_db
@patch("hope.apps.utils.elasticsearch_utils._delete")
@patch("hope.apps.household.index_management.delete_program_indexes")
def test_delete_all_indexes_no_active_programs(mock_delete_program: MagicMock, mock_delete: MagicMock) -> None:
    ba: BusinessArea = BusinessAreaFactory()
    ProgramFactory(business_area=ba, status=Program.DRAFT)

    delete_all_indexes()

    mock_delete_program.assert_not_called()
    mock_delete.assert_called_once_with(models=None)


@pytest.mark.django_db
@patch("hope.apps.utils.elasticsearch_utils._rebuild")
@patch("hope.apps.household.index_management.rebuild_program_indexes")
def test_rebuild_search_index_calls_per_program_and_global(
    mock_rebuild_program: MagicMock, mock_rebuild: MagicMock
) -> None:
    ba: BusinessArea = BusinessAreaFactory()
    program_1: Program = ProgramFactory(business_area=ba, status=Program.ACTIVE)
    program_2: Program = ProgramFactory(business_area=ba, status=Program.ACTIVE)
    ProgramFactory(business_area=ba, status=Program.DRAFT)

    rebuild_search_index()

    mock_rebuild_program.assert_has_calls([call(str(program_1.id)), call(str(program_2.id))], any_order=True)
    assert mock_rebuild_program.call_count == 2
    mock_rebuild.assert_called_once_with(models=None, options={"parallel": False, "quiet": True})


@pytest.mark.django_db
@patch("hope.apps.utils.elasticsearch_utils._rebuild")
@patch("hope.apps.household.index_management.rebuild_program_indexes")
def test_rebuild_search_index_no_active_programs(mock_rebuild_program: MagicMock, mock_rebuild: MagicMock) -> None:
    ba: BusinessArea = BusinessAreaFactory()
    ProgramFactory(business_area=ba, status=Program.DRAFT)

    rebuild_search_index()

    mock_rebuild_program.assert_not_called()
    mock_rebuild.assert_called_once_with(models=None, options={"parallel": False, "quiet": True})


@pytest.mark.django_db
@patch("hope.apps.utils.elasticsearch_utils._rebuild")
@patch("hope.apps.household.index_management.rebuild_program_indexes")
def test_rebuild_search_index_custom_options(mock_rebuild_program: MagicMock, mock_rebuild: MagicMock) -> None:
    ba: BusinessArea = BusinessAreaFactory()
    ProgramFactory(business_area=ba, status=Program.ACTIVE)

    custom_options: dict = {"parallel": True, "quiet": False}
    rebuild_search_index(options=custom_options)

    mock_rebuild.assert_called_once_with(models=None, options=custom_options)
