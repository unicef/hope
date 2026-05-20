import base64
from pathlib import Path

import pytest
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from extras.test_utils.factories.geo import AreaFactory, AreaTypeFactory
from extras.test_utils.factories.registration_data import RegistrationDataImportFactory
from hope.apps.core.utils import IDENTIFICATION_TYPE_TO_KEY_MAPPING
from hope.apps.household.const import (
    HEAD,
    IDENTIFICATION_TYPE_BIRTH_CERTIFICATE,
    NON_BENEFICIARY,
    ROLE_ALTERNATE,
    ROLE_PRIMARY,
    SON_DAUGHTER,
)
from hope.models import (
    Area,
    BusinessArea,
    Country,
    DocumentType,
    PendingHousehold,
    Program,
    RegistrationDataImport,
)

pytestmark = pytest.mark.django_db


@pytest.fixture
def rdi_in_review(business_area: BusinessArea, program: Program) -> RegistrationDataImport:
    return RegistrationDataImportFactory(
        name="test_push_error_if_not_loading",
        business_area=business_area,
        program=program,
        number_of_individuals=0,
        number_of_households=0,
        status=RegistrationDataImport.IN_REVIEW,
    )


@pytest.fixture
def admin_areas(afghanistan_country: Country) -> tuple[Area, Area, Area]:
    admin_type_1 = AreaTypeFactory(country=afghanistan_country, area_level=1)
    admin_type_2 = AreaTypeFactory(country=afghanistan_country, area_level=2, parent=admin_type_1)
    admin_type_3 = AreaTypeFactory(country=afghanistan_country, area_level=3, parent=admin_type_2)
    area1 = AreaFactory(parent=None, p_code="AF01", area_type=admin_type_1)
    area2 = AreaFactory(parent=area1, p_code="AF0101", area_type=admin_type_2)
    area3 = AreaFactory(parent=area2, p_code="AF010101", area_type=admin_type_3)
    return area1, area2, area3


def test_push_lax_returns_404_when_rdi_not_loading(
    token_api_client: APIClient,
    business_area: BusinessArea,
    rdi_in_review: RegistrationDataImport,
) -> None:
    url = reverse("api:rdi-push-lax", args=[business_area.slug, str(rdi_in_review.id)])

    response = token_api_client.post(url, {}, format="json")

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_push_lax_creates_households_and_reports_errors(
    token_api_client: APIClient,
    business_area: BusinessArea,
    program: Program,
    rdi_loading: RegistrationDataImport,
    afghanistan_country: Country,
    birth_certificate_doc_type: DocumentType,
    admin_areas: tuple[Area, Area, Area],
) -> None:
    image = Path(__file__).parent / "logo.png"
    base64_encoded_data = base64.b64encode(image.read_bytes())
    birth_cert_key = IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_BIRTH_CERTIFICATE]
    url = reverse("api:rdi-push-lax", args=[business_area.slug, str(rdi_loading.id)])
    input_data = [
        {
            "residence_status": "",
            "village": "village1",
            "country": "AF",
            "admin1": "AF01",
            "admin2": None,
            "members": [
                {
                    "relationship": HEAD,
                    "full_name": "James Head #1",
                    "birth_date": "2000-01-01",
                    "sex": "MALE",
                    "role": "",
                    "documents": [
                        {
                            "document_number": 10,
                            "image": base64_encoded_data,
                            "country": "AF",
                            "type": birth_cert_key,
                        }
                    ],
                },
                {
                    "relationship": NON_BENEFICIARY,
                    "full_name": "Mary Primary #1",
                    "birth_date": "2000-01-01",
                    "role": ROLE_PRIMARY,
                    "sex": "FEMALE",
                },
            ],
            "size": 1,
        },
        {
            "residence_status": "",
            "village": "village2",
            "country": "AF",
            "members": [
                {
                    "relationship": HEAD,
                    "full_name": "James Head #1",
                    "birth_date": "2000-01-01",
                    "sex": "MALE",
                    "role": ROLE_PRIMARY,
                    "documents": [
                        {
                            "document_number": 10,
                            "image": base64_encoded_data,
                            "country": "AF",
                            "type": birth_cert_key,
                        }
                    ],
                }
            ],
        },
        {
            "residence_status": "IDP",
            "village": "village3",
            "country": "AF",
            "size": 1,
            "members": [
                {
                    "full_name": "Jhon Primary #1",
                    "birth_date": "2000-01-01",
                    "role": "",
                    "sex": "FEMALE",
                },
                {
                    "relationship": NON_BENEFICIARY,
                    "full_name": "Mary Alternate #1",
                    "birth_date": "2000-01-01",
                    "role": ROLE_ALTERNATE,
                    "sex": "MALE",
                },
                {
                    "relationship": HEAD,
                    "full_name": "James Head #1",
                    "birth_date": "2000-01-01",
                    "sex": "MALE",
                    "role": "",
                    "documents": [
                        {
                            "document_number": 10,
                            "country": "AF",
                            "type": birth_cert_key,
                        }
                    ],
                },
                {
                    "relationship": SON_DAUGHTER,
                    "full_name": "Mary Son #1",
                    "birth_date": "2000-01-01",
                    "role": "",
                    "sex": "MALE",
                },
            ],
        },
        {
            "residence_status": "",
            "village": "village4",
            "country": "AF",
            "size": 1,
            "members": [
                {
                    "relationship": HEAD,
                    "full_name": "John Head #2",
                    "birth_date": "2000-01-01",
                    "sex": "MALE",
                    "role": "",
                    "documents": [
                        {
                            "document_number": 10,
                            "image": base64_encoded_data,
                            "country": "AF",
                            "type": birth_cert_key,
                        }
                    ],
                },
                {
                    "relationship": NON_BENEFICIARY,
                    "full_name": "Mary Primary #2",
                    "birth_date": "2000-01-01",
                    "role": ROLE_PRIMARY,
                    "sex": "FEMALE",
                },
            ],
        },
        {
            "residence_status": "",
            "village": "village5",
            "country": "AF",
            "size": 1,
            "members": [
                {
                    "relationship": HEAD,
                    "full_name": "John Doe",
                    "birth_date": "2000-01-01",
                    "sex": "MALE",
                    "role": "",
                    "documents": [
                        {
                            "document_number": 10,
                            "image": base64_encoded_data,
                            "country": "AF",
                            "type": birth_cert_key,
                        }
                    ],
                },
                {
                    "relationship": NON_BENEFICIARY,
                    "full_name": "Mary Doe",
                    "birth_date": "2000-01-01",
                    "role": ROLE_PRIMARY,
                    "sex": "FEMALE",
                },
            ],
        },
        {
            "residence_status": "",
            "village": "village6",
            "country": "AF",
            "size": 1,
            "members": [
                {
                    "full_name": "James Head #1",
                    "birth_date": "2000-01-01",
                    "sex": "MALE",
                    "role": "",
                    "documents": [
                        {
                            "document_number": 10,
                            "image": base64_encoded_data,
                            "country": "AF",
                            "type": birth_cert_key,
                        }
                    ],
                },
                {
                    "relationship": NON_BENEFICIARY,
                    "full_name": "Mary Primary #1",
                    "birth_date": "2000-01-01",
                    "role": ROLE_PRIMARY,
                    "sex": "FEMALE",
                },
            ],
        },
    ]

    response = token_api_client.post(url, input_data, format="json")

    assert response.status_code == status.HTTP_201_CREATED, str(response.json())
    data = response.json()
    assert len(data["households"]) == 6
    assert data["processed"] == 6
    assert data["errors"] == 2
    assert data["accepted"] == 4
    rdi = RegistrationDataImport.objects.filter(id=data["id"]).first()
    assert rdi is not None
    assert PendingHousehold.objects.filter(registration_data_import=rdi, village="village1").exists()
    assert PendingHousehold.objects.filter(registration_data_import=rdi, village="village4").exists()
    assert PendingHousehold.objects.filter(registration_data_import=rdi, village="village5").exists()
    assert data["households"][2] == {"Household #3": [{"primary_collector": ["Missing Primary Collector"]}]}
    assert data["households"][5] == {"Household #6": [{"head_of_household": ["Missing Head Of Household"]}]}
    pk1 = list(data["households"][0].values())[0][0]["pk"]
    hh = PendingHousehold.objects.get(pk=pk1)
    assert hh.program_id == program.id
    assert hh.head_of_household.full_name == "James Head #1"
    assert hh.primary_collector.full_name == "Mary Primary #1"
    assert hh.head_of_household.program_id == program.id
    assert hh.primary_collector.program_id == program.id
    pk2 = list(data["households"][1].values())[0][0]["pk"]
    hh = PendingHousehold.objects.get(pk=pk2)
    assert hh.program_id == program.id
    assert hh.head_of_household.full_name == "James Head #1"
    assert hh.primary_collector.full_name == "James Head #1"
    assert hh.head_of_household.program_id == program.id
    assert hh.primary_collector.program_id == program.id
