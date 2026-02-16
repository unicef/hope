from unittest.mock import patch

import pytest

from extras.test_utils.factories import (
    BusinessAreaFactory,
    ProgramFactory,
    RegistrationDataImportFactory,
)
from hope.apps.registration_datahub.tasks.rdi_kobo_create import RdiKoboCreateTask

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area():
    return BusinessAreaFactory(name="Afghanistan", slug="afghanistan")


@pytest.fixture
def program(business_area):
    return ProgramFactory(business_area=business_area)


@pytest.fixture
def rdi_with_pull_pictures(program):
    return RegistrationDataImportFactory(
        program=program,
        business_area=program.business_area,
        pull_pictures=True,
    )


@pytest.fixture
def rdi_without_pull_pictures(program):
    return RegistrationDataImportFactory(
        program=program,
        business_area=program.business_area,
        pull_pictures=False,
    )


@pytest.fixture
def kobo_task_pull_pictures(rdi_with_pull_pictures, business_area):
    return RdiKoboCreateTask(str(rdi_with_pull_pictures.id), str(business_area.id))


@pytest.fixture
def kobo_task_no_pull_pictures(rdi_without_pull_pictures, business_area):
    return RdiKoboCreateTask(str(rdi_without_pull_pictures.id), str(business_area.id))


def test_handle_image_field_attachments_none(kobo_task_pull_pictures):
    kobo_task_pull_pictures.attachments = None
    result = kobo_task_pull_pictures._handle_image_field("some_image.png", False)
    assert result is None


def test_handle_image_field_pull_pictures_false(kobo_task_no_pull_pictures):
    kobo_task_no_pull_pictures.attachments = [{"filename": "some_image.png"}]
    result = kobo_task_no_pull_pictures._handle_image_field("some_image.png", False)
    assert result is None


@patch("hope.apps.registration_datahub.tasks.rdi_kobo_create.find_attachment_in_kobo", return_value=None)
def test_handle_image_field_attachment_not_found(mock_find, kobo_task_pull_pictures):
    kobo_task_pull_pictures.attachments = [{"filename": "other.png"}]
    result = kobo_task_pull_pictures._handle_image_field("missing.png", False)
    assert result is None


@patch("hope.apps.registration_datahub.tasks.rdi_kobo_create.default_storage")
@patch("hope.apps.registration_datahub.tasks.rdi_kobo_create.KoboAPI")
@patch("hope.apps.registration_datahub.tasks.rdi_kobo_create.find_attachment_in_kobo")
def test_handle_image_field_success_flex_field(mock_find, mock_api_cls, mock_storage, kobo_task_pull_pictures):
    mock_find.return_value = {"download_url": "http://example.com/img.png?format=json"}
    mock_api_cls.return_value.get_attached_file.return_value = b"image_bytes"
    mock_storage.save.return_value = "stored/path.png"
    kobo_task_pull_pictures.attachments = [{"filename": "img.png"}]
    result = kobo_task_pull_pictures._handle_image_field("img.png", True)
    assert result == "stored/path.png"
    mock_storage.save.assert_called_once()


@patch("hope.apps.registration_datahub.tasks.rdi_kobo_create.KoboAPI")
@patch("hope.apps.registration_datahub.tasks.rdi_kobo_create.find_attachment_in_kobo")
def test_handle_image_field_success_non_flex(mock_find, mock_api_cls, kobo_task_pull_pictures):
    mock_find.return_value = {"download_url": "http://example.com/img.png?format=json"}
    mock_api_cls.return_value.get_attached_file.return_value = b"image_bytes"
    kobo_task_pull_pictures.attachments = [{"filename": "img.png"}]
    result = kobo_task_pull_pictures._handle_image_field("img.png", False)
    assert result is not None
