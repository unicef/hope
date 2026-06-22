from typing import Any

from django.contrib.messages import get_messages
from django.test import Client
from django.urls import reverse
from elasticsearch.exceptions import ConnectionError as ElasticsearchConnectionError
import pytest

from extras.test_utils.factories import UserFactory
from hope.apps.administration.panels.es import panel_elasticsearch
from hope.models import User

pytestmark = pytest.mark.django_db


def test_panel_rebuild_search_index_method_delegates_to_helper(mocker: Any) -> None:
    rebuild = mocker.patch("hope.apps.administration.panels.es.rebuild_search_index")

    panel_elasticsearch.rebuild_search_index(request=mocker.Mock())

    rebuild.assert_called_once_with()


@pytest.fixture
def superuser() -> User:
    return UserFactory(is_staff=True, is_superuser=True)


@pytest.fixture
def superuser_client(client: Client, superuser: User) -> Client:
    client.force_login(superuser, "django.contrib.auth.backends.ModelBackend")
    return client


def test_es_panel_get_renders_config(superuser_client: Client) -> None:
    response = superuser_client.get(reverse("admin:console-es"))

    assert response.status_code == 200
    assert "ELASTICSEARCH_HOST" in response.context["config"]
    assert response.context["logs"] == {}


def test_es_panel_post_info_returns_cluster_info(superuser_client: Client, mocker: Any) -> None:
    conn = mocker.Mock()
    conn.info.return_value = {"version": {"number": "8.14.0"}}
    mocker.patch("hope.apps.administration.panels.es.create_connection", return_value=conn)

    response = superuser_client.post(reverse("admin:console-es"), {"action": "info"})

    assert response.status_code == 200
    assert response.context["logs"] == {"version": {"number": "8.14.0"}}


def test_es_panel_post_test_connection_pings(superuser_client: Client, mocker: Any) -> None:
    conn = mocker.Mock()
    create_connection = mocker.patch("hope.apps.administration.panels.es.create_connection", return_value=conn)

    response = superuser_client.post(reverse("admin:console-es"), {"action": "test_connection"})

    assert response.status_code == 200
    create_connection.assert_called_once()
    conn.ping.assert_called_once()


def test_es_panel_post_rebuild_search_index_invokes_helper(superuser_client: Client, mocker: Any) -> None:
    rebuild = mocker.patch("hope.apps.administration.panels.es.rebuild_search_index")

    response = superuser_client.post(reverse("admin:console-es"), {"action": "rebuild_search_index"})

    assert response.status_code == 200
    rebuild.assert_called_once()


def test_es_panel_post_populate_all_indexes_invokes_helper(superuser_client: Client, mocker: Any) -> None:
    populate = mocker.patch("hope.apps.administration.panels.es.populate_all_indexes")

    response = superuser_client.post(reverse("admin:console-es"), {"action": "populate_all_indexes"})

    assert response.status_code == 200
    populate.assert_called_once()


def test_es_panel_post_connection_error_adds_error_message(superuser_client: Client, mocker: Any) -> None:
    mocker.patch(
        "hope.apps.administration.panels.es.create_connection",
        side_effect=ElasticsearchConnectionError("no cluster"),
    )

    response = superuser_client.post(reverse("admin:console-es"), {"action": "test_connection"})

    assert response.status_code == 200
    messages = [str(message) for message in get_messages(response.wsgi_request)]
    assert len(messages) == 1
    assert messages[0].startswith("ConnectionError")


def test_es_panel_post_invalid_action_keeps_form_errors(superuser_client: Client) -> None:
    response = superuser_client.post(reverse("admin:console-es"), {"action": "not_a_choice"})

    assert response.status_code == 200
    assert response.context["form"].errors
    assert response.context["logs"] == {}
