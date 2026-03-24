import contextlib
from unittest.mock import patch

import pytest

from extras.test_utils.factories import (
    ImportDataFactory,
    RegistrationDataImportFactory,
    UserFactory,
)
from hope.apps.generic_import.celery_tasks import process_generic_import_task
from hope.models import ImportData, RegistrationDataImport

pytestmark = pytest.mark.django_db


@pytest.fixture
def user():
    return UserFactory()


@pytest.fixture
def import_data():
    return ImportDataFactory(
        status=ImportData.STATUS_PENDING,
        data_type=ImportData.XLSX,
    )


@pytest.fixture
def rdi_without_business_area(user, import_data):
    rdi = RegistrationDataImportFactory(
        status=RegistrationDataImport.IMPORT_SCHEDULED,
        imported_by=user,
        data_source=RegistrationDataImport.XLS,
        import_data=import_data,
        number_of_households=0,
        number_of_individuals=0,
    )
    # Set business_area to None via queryset update to bypass FK descriptor validation
    RegistrationDataImport.objects.filter(pk=rdi.pk).update(business_area=None)
    rdi.refresh_from_db()
    return rdi


def test_process_generic_import_task_raises_value_error_when_rdi_has_no_business_area(
    import_data, rdi_without_business_area
):
    @contextlib.contextmanager
    def always_locked(key, **kwargs):
        yield True

    with patch("hope.apps.generic_import.celery_tasks.locked_cache", new=always_locked):
        with pytest.raises(ValueError, match=f"RDI {rdi_without_business_area.id} has no business_area"):
            process_generic_import_task(
                registration_data_import_id=str(rdi_without_business_area.id),
                import_data_id=str(import_data.id),
            )
