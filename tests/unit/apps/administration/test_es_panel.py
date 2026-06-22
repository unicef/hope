from typing import Any
from unittest.mock import MagicMock

import pytest

from hope.apps.administration.panels.es import ElasticsearchPanel


@pytest.fixture
def panel() -> ElasticsearchPanel:
    return ElasticsearchPanel()


@pytest.fixture
def model_admin_mock() -> Any:
    mock = MagicMock()
    mock.each_context.return_value = {}
    return mock


def test_es_panel_info_action_calls_conn_info(
    rf: Any, panel: ElasticsearchPanel, model_admin_mock: Any, mocker: Any
) -> None:
    info_result = {"cluster_name": "test-cluster", "name": "node-1"}
    mock_conn = MagicMock()
    mock_conn.info.return_value = MagicMock(body=info_result)
    mocker.patch("hope.apps.administration.panels.es.create_connection", return_value=mock_conn)

    captured: dict = {}

    def capture_render(request: Any, template: str, context: dict) -> MagicMock:
        captured.update(context)
        return MagicMock()

    mocker.patch("hope.apps.administration.panels.es.render", side_effect=capture_render)

    request = rf.post("/", {"action": "info"})
    request.user = MagicMock(is_active=True, is_staff=True)

    panel(model_admin_mock, request)

    mock_conn.info.assert_called_once()
    assert captured["logs"] == info_result
