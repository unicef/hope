"""Cross business area scoping of the registration data import actions (GHSA-2xf8-jjc2-9pmv).

Permissions are checked against the business area of the url path, while the uploaded file an
import starts from is named by a global id in the request body.
"""

from typing import Any, Callable

import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from extras.test_utils.factories import (
    BusinessAreaFactory,
    ProgramFactory,
    UserFactory,
)
from hope.apps.account.permissions import Permissions
from hope.models import BusinessArea, ImportData, KoboImportData, Program, RegistrationDataImport, User

pytestmark = pytest.mark.django_db


@pytest.fixture
def attacker_business_area() -> BusinessArea:
    return BusinessAreaFactory(name="Afghanistan", slug="afghanistan")


@pytest.fixture
def attacker_program(attacker_business_area: BusinessArea) -> Program:
    return ProgramFactory(business_area=attacker_business_area, status=Program.ACTIVE)


@pytest.fixture
def attacker(
    attacker_business_area: BusinessArea,
    attacker_program: Program,
    create_user_role_with_permissions: Callable,
) -> User:
    user = UserFactory()
    create_user_role_with_permissions(
        user,
        [Permissions.RDI_IMPORT_DATA],
        attacker_business_area,
        attacker_program,
    )
    return user


@pytest.fixture
def api_client(api_client: Callable, attacker: User) -> Any:
    return api_client(attacker)


@pytest.fixture
def victim_business_area() -> BusinessArea:
    return BusinessAreaFactory(name="Ukraine", slug="ukraine")


@pytest.fixture
def victim_import_data(victim_business_area: BusinessArea) -> ImportData:
    return ImportData.objects.create(
        status=ImportData.STATUS_FINISHED,
        business_area_slug=victim_business_area.slug,
        data_type=ImportData.XLSX,
        number_of_households=1,
        number_of_individuals=1,
    )


@pytest.fixture
def victim_kobo_import_data(victim_business_area: BusinessArea) -> KoboImportData:
    return KoboImportData.objects.create(
        status=ImportData.STATUS_FINISHED,
        business_area_slug=victim_business_area.slug,
        data_type=ImportData.JSON,
        number_of_households=1,
        number_of_individuals=1,
    )


def test_xlsx_import_from_file_of_other_business_area_is_denied(
    api_client: Any,
    attacker_business_area: BusinessArea,
    attacker_program: Program,
    victim_import_data: ImportData,
) -> None:
    url = reverse(
        "api:registration-data:registration-data-imports-registration-xlsx-import",
        kwargs={"business_area_slug": attacker_business_area.slug, "program_code": attacker_program.code},
    )

    response = api_client.post(
        url,
        {
            "import_data_id": str(victim_import_data.id),
            "name": "cross business area xlsx import",
            "screen_beneficiary": False,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.status_code
    assert not RegistrationDataImport.objects.exists()


def test_kobo_import_from_file_of_other_business_area_is_denied(
    api_client: Any,
    attacker_business_area: BusinessArea,
    attacker_program: Program,
    victim_kobo_import_data: KoboImportData,
) -> None:
    url = reverse(
        "api:registration-data:registration-data-imports-registration-kobo-import",
        kwargs={"business_area_slug": attacker_business_area.slug, "program_code": attacker_program.code},
    )

    response = api_client.post(
        url,
        {
            "import_data_id": str(victim_kobo_import_data.id),
            "name": "cross business area kobo import",
            "pull_pictures": False,
            "screen_beneficiary": False,
        },
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.status_code
    assert not RegistrationDataImport.objects.exists()
