from unittest.mock import MagicMock, patch

import pytest

pytestmark = pytest.mark.django_db


class TestEnsureIndexReady:
    @patch("hope.apps.utils.elasticsearch_utils.connections")
    def test_ensure_index_ready_healthy_green(self, mock_connections):
        from hope.apps.utils.elasticsearch_utils import ensure_index_ready

        mock_conn = MagicMock()
        mock_conn.cluster.health.return_value = {"status": "green"}
        mock_connections.get_connection.return_value = mock_conn

        ensure_index_ready("test_index")

        mock_conn.indices.refresh.assert_called_once_with(index="test_index")

    @patch("hope.apps.utils.elasticsearch_utils.connections")
    def test_ensure_index_ready_healthy_yellow(self, mock_connections):
        from hope.apps.utils.elasticsearch_utils import ensure_index_ready

        mock_conn = MagicMock()
        mock_conn.cluster.health.return_value = {"status": "yellow"}
        mock_connections.get_connection.return_value = mock_conn

        ensure_index_ready("test_index")

        mock_conn.indices.refresh.assert_called_once_with(index="test_index")

    @patch("hope.apps.utils.elasticsearch_utils.connections")
    def test_ensure_index_ready_red_raises(self, mock_connections):
        from hope.apps.utils.elasticsearch_utils import ensure_index_ready

        mock_conn = MagicMock()
        mock_conn.cluster.health.return_value = {"status": "red"}
        mock_connections.get_connection.return_value = mock_conn

        with pytest.raises(Exception, match="ES cluster is RED"):
            ensure_index_ready("test_index")
