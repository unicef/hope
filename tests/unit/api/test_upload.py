import pytest
from rest_framework import status
from rest_framework.test import APIClient

from hope.apps.core.utils import IDENTIFICATION_TYPE_TO_KEY_MAPPING
from hope.apps.household.const import (
    HEAD,
    IDENTIFICATION_TYPE_BIRTH_CERTIFICATE,
    MALE,
    NON_BENEFICIARY,
    ROLE_ALTERNATE,
    ROLE_PRIMARY,
    SON_DAUGHTER,
)
from hope.models import DocumentType, PendingHousehold, PendingIndividual, Program, RegistrationDataImport

pytestmark = pytest.mark.django_db


def test_upload_single_household_with_head_as_primary(
    token_api_client: APIClient,
    upload_url: str,
    program: Program,
    afghanistan_country: None,
    mock_elasticsearch: None,
) -> None:
    payload = {
        "name": "aaaa",
        "program": str(program.id),
        "households": [
            {
                "residence_status": "IDP",
                "village": "village1",
                "country": "AF",
                "members": [
                    {
                        "relationship": HEAD,
                        "role": ROLE_PRIMARY,
                        "full_name": "John Doe",
                        "birth_date": "2000-01-01",
                        "sex": "MALE",
                    },
                    {
                        "relationship": SON_DAUGHTER,
                        "full_name": "Mary Doe",
                        "birth_date": "2000-01-01",
                        "role": "",
                        "sex": "FEMALE",
                    },
                ],
                "size": 1,
            }
        ],
    }
    response = token_api_client.post(upload_url, payload, format="json")
    assert response.status_code == status.HTTP_201_CREATED, response.json()
    data = response.json()

    rdi = RegistrationDataImport.objects.filter(id=data["id"]).first()
    assert rdi is not None
    assert rdi.program == program
    assert rdi.deduplication_engine_status == RegistrationDataImport.DEDUP_ENGINE_PENDING

    hh = PendingHousehold.objects.filter(registration_data_import=rdi).first()
    assert hh is not None
    assert hh.head_of_household is not None
    assert hh.primary_collector is not None
    assert hh.alternate_collector is None
    assert hh.head_of_household.full_name == "John Doe"
    assert hh.head_of_household.sex == MALE
    assert data["households"] == 1
    assert data["individuals"] == 2


def test_upload_external_collector(
    token_api_client: APIClient,
    upload_url: str,
    program: Program,
    afghanistan_country: None,
    mock_elasticsearch: None,
) -> None:
    payload = {
        "name": "aaaa",
        "program": str(program.id),
        "households": [
            {
                "residence_status": "IDP",
                "village": "village1",
                "country": "AF",
                "members": [
                    {
                        "relationship": HEAD,
                        "full_name": "John Doe",
                        "birth_date": "2000-01-01",
                        "sex": "MALE",
                        "role": "",
                    },
                    {
                        "relationship": NON_BENEFICIARY,
                        "full_name": "Mary Doe",
                        "birth_date": "2000-01-01",
                        "role": ROLE_PRIMARY,
                        "sex": "FEMALE",
                    },
                ],
                "size": 1,
            }
        ],
    }
    response = token_api_client.post(upload_url, payload, format="json")
    data = response.json()
    assert response.status_code == status.HTTP_201_CREATED, data

    rdi = RegistrationDataImport.objects.filter(id=data["id"]).first()
    assert rdi is not None

    hh = PendingHousehold.objects.filter(registration_data_import=rdi).first()
    assert hh is not None
    assert hh.head_of_household is not None
    assert hh.primary_collector is not None
    assert hh.primary_collector != hh.head_of_household
    assert hh.alternate_collector is None
    assert hh.head_of_household.full_name == "John Doe"
    assert hh.head_of_household.sex == MALE
    assert data["households"] == 1
    assert data["individuals"] == 2


def test_upload_with_documents(
    token_api_client: APIClient,
    upload_url: str,
    program: Program,
    afghanistan_country: None,
    birth_certificate_doc_type: DocumentType,
    mock_elasticsearch: None,
) -> None:
    payload = {
        "name": "aaaa",
        "program": str(program.id),
        "households": [
            {
                "residence_status": "IDP",
                "village": "village1",
                "country": "AF",
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
                                "image": "",
                                "country": "AF",
                                "type": IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_BIRTH_CERTIFICATE],
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
                "size": 1,
            }
        ],
    }
    response = token_api_client.post(upload_url, payload, format="json")
    assert response.status_code == status.HTTP_201_CREATED, response.json()

    hoh = PendingIndividual.objects.filter(birth_date="2000-01-01", full_name="John Doe", sex=MALE).first()
    assert hoh
    hh = hoh.pending_household
    assert hh.village == "village1"
    assert hh.primary_collector != hoh
    assert hh.alternate_collector is None
    members = hh.individuals.all()
    assert len(members) == 1
    assert hoh.documents.exists()


def test_upload_with_document_photo(
    token_api_client: APIClient,
    upload_url: str,
    program: Program,
    afghanistan_country: None,
    birth_certificate_doc_type: DocumentType,
    base64_image: str,
    mock_elasticsearch: None,
) -> None:
    payload = {
        "name": "aaaa",
        "program": str(program.id),
        "households": [
            {
                "residence_status": "IDP",
                "village": "village1",
                "country": "AF",
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
                                "image": base64_image,
                                "country": "AF",
                                "type": IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_BIRTH_CERTIFICATE],
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
                "size": 1,
            }
        ],
    }
    response = token_api_client.post(upload_url, payload, format="json")
    assert response.status_code == status.HTTP_201_CREATED, response.json()
    data = response.json()

    rdi = RegistrationDataImport.objects.filter(id=data["id"]).first()
    assert rdi is not None

    hh = PendingHousehold.objects.filter(registration_data_import=rdi).first()
    assert hh is not None
    assert hh.head_of_household is not None
    assert hh.primary_collector is not None
    assert hh.alternate_collector is None
    assert hh.head_of_household.full_name == "John Doe"
    assert hh.head_of_household.sex == MALE

    hoh = PendingIndividual.objects.filter(full_name="John Doe", sex=MALE).first()
    assert hoh is not None
    assert hoh.documents.exists()
    assert hoh.documents.first().photo
    assert data["households"] == 1
    assert data["individuals"] == 2


def test_upload_multiple_households(
    token_api_client: APIClient,
    upload_url: str,
    program: Program,
    afghanistan_country: None,
    birth_certificate_doc_type: DocumentType,
    base64_image: str,
    mock_elasticsearch: None,
) -> None:
    payload = {
        "name": "aaaa",
        "program": str(program.id),
        "households": [
            {
                "residence_status": "IDP",
                "village": "village1",
                "country": "AF",
                "members": [
                    {
                        "relationship": NON_BENEFICIARY,
                        "full_name": "Jhon Primary #1",
                        "birth_date": "2000-01-01",
                        "role": ROLE_PRIMARY,
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
                                "type": IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_BIRTH_CERTIFICATE],
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
                "size": 1,
            },
            {
                "residence_status": "",
                "village": "village2",
                "country": "AF",
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
                                "image": base64_image,
                                "country": "AF",
                                "type": IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_BIRTH_CERTIFICATE],
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
                "size": 1,
            },
            {
                "residence_status": "",
                "village": "village3",
                "country": "AF",
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
                                "image": base64_image,
                                "country": "AF",
                                "type": IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_BIRTH_CERTIFICATE],
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
                "size": 1,
            },
        ],
    }
    response = token_api_client.post(upload_url, payload, format="json")
    assert response.status_code == status.HTTP_201_CREATED, response.json()
    data = response.json()

    rdi = RegistrationDataImport.objects.filter(id=data["id"]).first()
    assert rdi is not None

    hh = PendingHousehold.objects.filter(registration_data_import=rdi, village="village1").first()
    assert hh is not None
    assert hh.head_of_household is not None
    assert hh.primary_collector is not None
    assert hh.alternate_collector is not None
    assert hh.primary_collector.full_name == "Jhon Primary #1"
    assert hh.head_of_household.full_name == "James Head #1"
    assert data["households"] == 3
    assert data["individuals"] == 8


def test_upload_error_too_many_heads_of_household(
    token_api_client: APIClient,
    upload_url: str,
    program: Program,
    afghanistan_country: None,
    mock_elasticsearch: None,
) -> None:
    payload = {
        "name": "aaaa",
        "program": str(program.id),
        "households": [
            {
                "residence_status": "",
                "village": "village1",
                "country": "AF",
                "members": [
                    {
                        "relationship": HEAD,
                        "role": ROLE_PRIMARY,
                        "full_name": "John Doe",
                        "birth_date": "2000-01-01",
                        "sex": "MALE",
                    },
                    {
                        "relationship": HEAD,
                        "full_name": "Mary Doe",
                        "birth_date": "2000-01-01",
                        "role": "",
                        "sex": "FEMALE",
                    },
                ],
                "size": 1,
            }
        ],
    }
    response = token_api_client.post(upload_url, payload, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"households": [{"Household #1": [{"head_of_household": ["Only one HoH allowed"]}]}]}


def test_upload_error_missing_primary_collector(
    token_api_client: APIClient,
    upload_url: str,
    program: Program,
    afghanistan_country: None,
    birth_certificate_doc_type: DocumentType,
    mock_elasticsearch: None,
) -> None:
    payload = {
        "name": "aaaa",
        "program": str(program.id),
        "households": [
            {
                "residence_status": "",
                "village": "village1",
                "country": "AF",
                "members": [
                    {
                        "relationship": NON_BENEFICIARY,
                        "full_name": "Jhon Primary #1",
                        "birth_date": "2000-01-01",
                        "role": ROLE_PRIMARY,
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
                                "type": IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_BIRTH_CERTIFICATE],
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
                "size": 1,
            },
            {
                "residence_status": "",
                "village": "village1",
                "country": "AF",
                "members": [
                    {
                        "relationship": HEAD,
                        "role": ROLE_ALTERNATE,
                        "full_name": "John Doe",
                        "birth_date": "2000-01-01",
                        "sex": "MALE",
                    },
                    {
                        "relationship": SON_DAUGHTER,
                        "full_name": "Mary Doe",
                        "birth_date": "2000-01-01",
                        "role": "",
                        "sex": "FEMALE",
                    },
                ],
                "size": 1,
            },
        ],
    }
    response = token_api_client.post(upload_url, payload, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"households": [{"Household #2": [{"primary_collector": ["Missing Primary Collector"]}]}]}


def test_upload_multiple_validation_errors(
    token_api_client: APIClient,
    upload_url: str,
    afghanistan_country: None,
    birth_certificate_doc_type: DocumentType,
    mock_elasticsearch: None,
) -> None:
    payload = {
        "name": "aaaa",
        "households": [
            {
                "residence_status": "",
                "village": "village1",
                "country": "AF",
                "members": [
                    {
                        "relationship": NON_BENEFICIARY,
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
                        "relationship": SON_DAUGHTER,
                        "full_name": "James Head #1",
                        "birth_date": "2000-01-01",
                        "sex": "MALE",
                        "role": ROLE_ALTERNATE,
                        "documents": [
                            {
                                "document_number": 10,
                                "country": "AF",
                                "type": IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_BIRTH_CERTIFICATE],
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
                "size": 1,
            },
            {
                "residence_status": "",
                "village": "village1",
                "country": "AF",
                "members": [
                    {
                        "relationship": HEAD,
                        "full_name": "John Doe",
                        "birth_date": "2000-01-01",
                        "role": "",
                        "sex": "MALE",
                    },
                    {
                        "relationship": HEAD,
                        "full_name": "Mary Doe",
                        "birth_date": "2000-01-01",
                        "role": "",
                        "sex": "FEMALE",
                    },
                ],
                "size": 1,
            },
        ],
    }
    response = token_api_client.post(upload_url, payload, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        "households": [
            {
                "Household #1": [
                    {
                        "alternate_collector": ["Only one Alternate Collector allowed"],
                        "head_of_household": ["Missing Head Of Household"],
                        "primary_collector": ["Missing Primary Collector"],
                    }
                ]
            },
            {
                "Household #2": [
                    {
                        "head_of_household": ["Only one HoH allowed"],
                        "primary_collector": ["Missing Primary Collector"],
                    }
                ]
            },
        ],
        "program": ["This field is required."],
    }


def test_upload_error_empty_members(
    token_api_client: APIClient,
    upload_url: str,
    program: Program,
    afghanistan_country: None,
    mock_elasticsearch: None,
) -> None:
    payload = {
        "name": "aaaa",
        "program": str(program.id),
        "households": [
            {
                "residence_status": "IDP",
                "village": "village1",
                "country": "AF",
                "members": [],
            }
        ],
    }
    response = token_api_client.post(upload_url, payload, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"households": [{"Household #1": [{"members": ["This field is required"]}]}]}


def test_upload_error_multiple_primary_collectors(
    token_api_client: APIClient,
    upload_url: str,
    program: Program,
    afghanistan_country: None,
    mock_elasticsearch: None,
) -> None:
    payload = {
        "name": "aaaa",
        "program": str(program.id),
        "households": [
            {
                "residence_status": "IDP",
                "village": "village1",
                "country": "AF",
                "members": [
                    {
                        "relationship": HEAD,
                        "role": ROLE_PRIMARY,
                        "full_name": "John Doe",
                        "birth_date": "2000-01-01",
                        "sex": "MALE",
                    },
                    {
                        "relationship": NON_BENEFICIARY,
                        "role": ROLE_PRIMARY,
                        "full_name": "Jane Doe",
                        "birth_date": "2000-01-01",
                        "sex": "FEMALE",
                    },
                ],
            }
        ],
    }
    response = token_api_client.post(upload_url, payload, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        "households": [{"Household #1": [{"primary_collector": ["Only one Primary Collector allowed"]}]}]
    }


def test_upload_error_empty_households(
    token_api_client: APIClient,
    upload_url: str,
    program: Program,
    afghanistan_country: None,
    mock_elasticsearch: None,
) -> None:
    payload = {
        "name": "aaaa",
        "program": str(program.id),
        "households": [],
    }
    response = token_api_client.post(upload_url, payload, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"households": ["This field is required."]}
