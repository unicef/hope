from typing import Any

from django.contrib.messages import get_messages
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.http import Http404
from django.test import RequestFactory
import pytest

from extras.test_utils.factories.account import UserFactory
from extras.test_utils.factories.aurora import RegistrationFactory
from hope.contrib.aurora.views import FetchDataView, RegistrationDataView

pytestmark = pytest.mark.django_db


def _request_with_messages(rf: RequestFactory, **post: Any):
    request = rf.post("/fetch/", data=post, HTTP_REFERER="/referrer/")
    request.user = UserFactory()
    SessionMiddleware(lambda r: None).process_request(request)
    MessageMiddleware(lambda r: None).process_request(request)
    return request


def test_fetch_data_get_redirects_to_referrer() -> None:
    request = RequestFactory().get("/fetch/", HTTP_REFERER="/referrer/")

    response = FetchDataView().get(request)

    assert response.status_code == 302
    assert response.url == "/referrer/"


def test_fetch_data_post_fetches_and_reports_success(mocker: Any) -> None:
    fetch = mocker.patch("hope.contrib.aurora.views.fetch_metadata")
    request = _request_with_messages(RequestFactory(), _fetch="1")

    response = FetchDataView().post(request)

    assert response.status_code == 302
    fetch.assert_called_once()
    assert [str(m) for m in get_messages(request)] == ["Data fetched"]


def test_fetch_data_post_reports_error_on_exception(mocker: Any) -> None:
    mocker.patch("hope.contrib.aurora.views.fetch_metadata", side_effect=RuntimeError("RuntimeError test"))
    request = _request_with_messages(RequestFactory(), _fetch="1")

    response = FetchDataView().post(request)

    assert response.status_code == 302
    assert [str(m) for m in get_messages(request)] == ["RuntimeError test"]


def test_fetch_data_post_without_fetch_flag_just_redirects(mocker: Any) -> None:
    fetch = mocker.patch("hope.contrib.aurora.views.fetch_metadata")
    request = _request_with_messages(RequestFactory())

    response = FetchDataView().post(request)

    assert response.status_code == 302
    fetch.assert_not_called()


def test_registration_resolves_by_slug() -> None:
    registration = RegistrationFactory(slug="my-slug")
    view = RegistrationDataView()
    view.kwargs = {"slug": "my-slug"}

    assert view.registration == registration


def test_registration_resolves_by_pk() -> None:
    registration = RegistrationFactory()
    view = RegistrationDataView()
    view.kwargs = {"pk": registration.pk}

    assert view.registration == registration


def test_registration_without_slug_or_pk_raises_http404() -> None:
    view = RegistrationDataView()
    view.kwargs = {}

    with pytest.raises(Http404):
        _ = view.registration


def test_registration_missing_record_raises_http404() -> None:
    view = RegistrationDataView()
    view.kwargs = {"slug": "does-not-exist"}

    with pytest.raises(Http404):
        _ = view.registration


def test_get_context_data_includes_registration_and_page_size() -> None:
    registration = RegistrationFactory(slug="ctx-slug")
    view = RegistrationDataView()
    view.kwargs = {"slug": "ctx-slug"}

    context = view.get_context_data()

    assert context["registration"] == registration
    assert "drf_page_size" in context
