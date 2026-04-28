import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from extras.test_utils.factories.core import BeneficiaryGroupFactory, DataCollectingTypeFactory
from extras.test_utils.factories.program import ProgramFactory
from extras.test_utils.factories.registration_data import RegistrationDataImportFactory
from hope.models import (
    BusinessArea,
    DataCollectingType,
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
def rdi(business_area: BusinessArea, program: Program) -> RegistrationDataImport:
    return RegistrationDataImportFactory(
        business_area=business_area,
        program=program,
        number_of_individuals=0,
        number_of_households=0,
        status=RegistrationDataImport.LOADING,
    )


@pytest.fixture
def push_people_url(business_area: BusinessArea, rdi: RegistrationDataImport) -> str:
    return reverse("api:rdi-push-people", args=[business_area.slug, str(rdi.id)])


@pytest.fixture
def base_person_data(program: Program) -> dict:
    return {
        "residence_status": "IDP",
        "village": "village1",
        "country": "AF",
        "full_name": "John Doe",
        "birth_date": "2000-01-01",
        "sex": "MALE",
        "type": "",
        "program": str(program.id),
    }


def test_cw_individual_push_with_country_workspace_id_persists(
    token_api_client,
    push_people_url: str,
    rdi: RegistrationDataImport,
    afghanistan_country,
    base_person_data: dict,
    django_assert_num_queries,
) -> None:
    payload = [{**base_person_data, "country_workspace_id": "cw-ind-001"}]

    with django_assert_num_queries(0):
        response = token_api_client.post(push_people_url, payload, format="json")

    assert response.status_code == status.HTTP_201_CREATED, str(response.json())
    ind = PendingIndividual.objects.filter(registration_data_import=rdi).first()
    assert ind is not None
    assert ind.country_workspace_id == "cw-ind-001"


def test_cw_individual_push_without_country_workspace_id_returns_400(
    token_api_client,
    push_people_url: str,
    rdi: RegistrationDataImport,
    afghanistan_country,
    base_person_data: dict,
) -> None:
    response = token_api_client.post(push_people_url, [base_person_data], format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST, str(response.json())
    assert response.json() == [{"country_workspace_id": ["This field is required."]}]
    assert PendingIndividual.objects.filter(registration_data_import=rdi).count() == 0


def test_cw_individual_push_blank_country_workspace_id_returns_400(
    token_api_client,
    push_people_url: str,
    rdi: RegistrationDataImport,
    afghanistan_country,
    base_person_data: dict,
) -> None:
    payload = [{**base_person_data, "country_workspace_id": ""}]

    response = token_api_client.post(push_people_url, payload, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST, str(response.json())
    assert response.json() == [{"country_workspace_id": ["This field may not be blank."]}]


def test_cw_individual_push_partial_failure_when_one_missing_field(
    token_api_client,
    push_people_url: str,
    rdi: RegistrationDataImport,
    afghanistan_country,
    base_person_data: dict,
) -> None:
    payload = [
        {**base_person_data, "full_name": "John Doe", "country_workspace_id": "cw-ind-good"},
        {**base_person_data, "full_name": "Mary Doe"},
    ]

    response = token_api_client.post(push_people_url, payload, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST, str(response.json())
    assert response.json() == [{}, {"country_workspace_id": ["This field is required."]}]
    assert PendingIndividual.objects.filter(registration_data_import=rdi).count() == 0


def test_cw_individual_push_duplicate_country_workspace_id_in_same_payload_returns_400(
    token_api_client,
    push_people_url: str,
    rdi: RegistrationDataImport,
    afghanistan_country,
    base_person_data: dict,
) -> None:
    payload = [
        {**base_person_data, "full_name": "John Doe", "country_workspace_id": "cw-ind-dup"},
        {**base_person_data, "full_name": "Mary Doe", "country_workspace_id": "cw-ind-dup"},
    ]

    response = token_api_client.post(push_people_url, payload, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST, str(response.json())
    assert "country_workspace_id" in str(response.json())
    assert PendingIndividual.objects.filter(registration_data_import=rdi).count() == 0


def test_cw_individual_push_roundtrip_distinct_ids_persist_per_individual(
    token_api_client,
    push_people_url: str,
    rdi: RegistrationDataImport,
    afghanistan_country,
    base_person_data: dict,
) -> None:
    payload = [
        {**base_person_data, "full_name": "John Doe", "country_workspace_id": "cw-ind-aaa"},
        {**base_person_data, "full_name": "Mary Doe", "country_workspace_id": "cw-ind-bbb"},
    ]

    response = token_api_client.post(push_people_url, payload, format="json")

    assert response.status_code == status.HTTP_201_CREATED, str(response.json())
    john = PendingIndividual.objects.get(registration_data_import=rdi, full_name="John Doe")
    mary = PendingIndividual.objects.get(registration_data_import=rdi, full_name="Mary Doe")
    assert john.country_workspace_id == "cw-ind-aaa"
    assert mary.country_workspace_id == "cw-ind-bbb"
