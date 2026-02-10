"""Tests for periodic data update admin."""

from typing import Any
from unittest.mock import patch

from django.test import Client
from django.urls import reverse
import pytest

from extras.test_utils.factories import (
    BusinessAreaFactory,
    PDUXlsxTemplateFactory,
    UserFactory,
)
from hope.models import PDUXlsxTemplate, User

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area(db: Any) -> Any:
    return BusinessAreaFactory(slug="afghanistan", name="Afghanistan")


@pytest.fixture
def admin_user(db: Any) -> User:
    user = UserFactory(username="root", email="root@root.com", is_superuser=True, is_staff=True)
    user.set_password("password")
    user.save()
    return user


@pytest.fixture
def admin_client(admin_user: User) -> Client:
    client = Client()
    client.login(username="root", password="password")
    return client


@patch("hope.admin.periodic_data_update.export_periodic_data_update_export_template_service.delay")
def test_post_regenerate_export_xlsx_post(
    mock_delay: Any,
    admin_client: Client,
    business_area: Any,
) -> None:
    xlsx_template = PDUXlsxTemplateFactory(
        program__business_area=business_area,
        business_area=business_area,
        status=PDUXlsxTemplate.Status.FAILED,
    )
    url = reverse("admin:periodic_data_update_pduxlsxtemplate_restart_export_task", args=[xlsx_template.pk])

    response = admin_client.post(url)
    mock_delay.assert_called_once_with(str(xlsx_template.pk))

    assert response.status_code == 302
    assert (
        reverse(
            "admin:periodic_data_update_pduxlsxtemplate_change",
            args=[xlsx_template.pk],
        )
        in response["Location"]
    )


@patch("hope.admin.periodic_data_update.export_periodic_data_update_export_template_service.delay")
def test_get_regenerate_export_xlsx(mock_delay: Any, admin_client: Client, business_area: Any) -> None:
    xlsx_template = PDUXlsxTemplateFactory(
        program__business_area=business_area,
        business_area=business_area,
        status=PDUXlsxTemplate.Status.FAILED,
    )
    url = reverse("admin:periodic_data_update_pduxlsxtemplate_restart_export_task", args=[xlsx_template.pk])

    response = admin_client.get(url)
    assert response.status_code == 200
    assert b"Do you confirm to restart the export task?" in response.content
    assert "admin_extra_buttons/confirm.html" in [t.name for t in response.templates]
