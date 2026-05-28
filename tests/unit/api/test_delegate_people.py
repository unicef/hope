from uuid import UUID

import pytest
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from extras.test_utils.factories.core import BeneficiaryGroupFactory, DataCollectingTypeFactory
from extras.test_utils.factories.program import ProgramFactory
from hope.apps.core.utils import IDENTIFICATION_TYPE_TO_KEY_MAPPING
from hope.apps.household.const import (
    IDENTIFICATION_TYPE_BIRTH_CERTIFICATE,
    NON_BENEFICIARY,
)
from hope.models import (
    BusinessArea,
    DataCollectingType,
    PendingHousehold,
    PendingIndividual,
    Program,
    RegistrationDataImport,
)

pytestmark = pytest.mark.django_db


@pytest.fixture
def program(business_area: BusinessArea) -> Program:
    dct = DataCollectingTypeFactory(
        label="Full",
        code="full",
        type=DataCollectingType.Type.SOCIAL.value,
    )
    dct.limit_to.add(business_area)
    beneficiary_group = BeneficiaryGroupFactory(master_detail=False)
    return ProgramFactory(
        status=Program.DRAFT,
        business_area=business_area,
        data_collecting_type=dct,
        beneficiary_group=beneficiary_group,
    )


@pytest.fixture
def people_ids(
    token_api_client: APIClient,
    business_area: BusinessArea,
    rdi_loading: RegistrationDataImport,
    afghanistan_country,
    birth_certificate_doc_type,
) -> list[UUID]:
    data = [
        {
            "residence_status": "IDP",
            "village": "village1",
            "country": "AF",
            "full_name": "John Doe",
            "birth_date": "2000-01-01",
            "sex": "MALE",
            "type": "",
            "documents": [
                {
                    "document_number": "10",
                    "image": "",
                    "doc_date": "2010-01-01",
                    "country": "AF",
                    "type": IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_BIRTH_CERTIFICATE],
                }
            ],
        },
        {
            "residence_status": "IDP",
            "village": "village2",
            "country": "AF",
            "full_name": "Mary Doe",
            "birth_date": "1990-01-01",
            "sex": "FEMALE",
            "type": "",
        },
        {
            "residence_status": "IDP",
            "village": "village3",
            "country": "AF",
            "full_name": "Jack Jones",
            "birth_date": "1980-01-01",
            "sex": "MALE",
            "type": NON_BENEFICIARY,
        },
    ]
    url = reverse("api:rdi-push-people", args=[business_area.slug, str(rdi_loading.id)])
    response = token_api_client.post(url, data, format="json")
    assert response.status_code == status.HTTP_201_CREATED, str(response.json())
    return response.json()["people"]


def test_delegate_people_reassigns_primary_collector(
    token_api_client: APIClient,
    business_area: BusinessArea,
    rdi_loading: RegistrationDataImport,
    people_ids: list[UUID],
) -> None:
    assert PendingHousehold.objects.filter(registration_data_import=rdi_loading).count() == 2
    assert PendingIndividual.objects.filter(registration_data_import=rdi_loading).count() == 3

    url = reverse("api:rdi-delegate-people", args=[business_area.slug, str(rdi_loading.id)])
    data = {"delegates": [{"delegate_id": people_ids[2], "delegated_for": [people_ids[1]]}]}

    response = token_api_client.post(url, data, format="json")

    assert response.status_code == status.HTTP_200_OK, str(response.json())
    assert response.json()["updated"] == 1
    hh1 = PendingHousehold.objects.get(registration_data_import=rdi_loading, village="village1")
    hh2 = PendingHousehold.objects.get(registration_data_import=rdi_loading, village="village2")
    assert hh1.primary_collector.full_name == "John Doe"
    assert hh2.primary_collector.full_name == "Jack Jones"
