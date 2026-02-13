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
