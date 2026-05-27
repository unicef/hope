import base64
from io import BytesIO

from PIL import Image
import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from extras.test_utils.factories.core import BeneficiaryGroupFactory, DataCollectingTypeFactory
from extras.test_utils.factories.geo import AreaFactory, AreaTypeFactory
from extras.test_utils.factories.household import DocumentTypeFactory
from extras.test_utils.factories.program import ProgramFactory
from extras.test_utils.factories.registration_data import RegistrationDataImportFactory
from hope.api.endpoints.rdi.push_people import PeopleUploadMixin, PushPeopleSerializer
from hope.apps.core.utils import IDENTIFICATION_TYPE_TO_KEY_MAPPING
from hope.apps.household.const import (
    DISABLED,
    FEMALE,
    HEAD,
    IDENTIFICATION_TYPE_BIRTH_CERTIFICATE,
    MALE,
    NOT_COLLECTED,
    NOT_DISABLED,
)
from hope.models import (
    Area,
    DataCollectingType,
    DocumentType,
    PendingDocument,
    PendingHousehold,
    PendingIndividual,
    Program,
    RegistrationDataImport,
)

pytestmark = pytest.mark.django_db


@pytest.fixture
def program(business_area) -> Program:
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
def rdi(business_area, program) -> RegistrationDataImport:
    return RegistrationDataImportFactory(
        business_area=business_area,
        program=program,
        number_of_individuals=0,
        number_of_households=0,
        status=RegistrationDataImport.LOADING,
    )


@pytest.fixture
def push_people_url(business_area, rdi) -> str:
    return reverse("api:rdi-push-people", args=[business_area.slug, str(rdi.id)])


@pytest.fixture
def birth_certificate_doc_type() -> DocumentType:
    return DocumentTypeFactory(
        key=IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_BIRTH_CERTIFICATE],
        label="--",
    )


@pytest.fixture
def admin_areas(afghanistan_country) -> tuple[Area, Area]:
    country = afghanistan_country
    admin_type_1 = AreaTypeFactory(country=country, area_level=1)
    admin_type_2 = AreaTypeFactory(country=country, area_level=2, parent=admin_type_1)
    admin_type_3 = AreaTypeFactory(country=country, area_level=3, parent=admin_type_2)
    area1 = AreaFactory(parent=None, p_code="AF01", area_type=admin_type_1)
    area2 = AreaFactory(parent=area1, p_code="AF0101", area_type=admin_type_2)
    # area3 is not directly matched by test payloads (admin3=""), but establishes
    # the parent-child tree structure needed by area validation logic.
    AreaFactory(parent=area2, p_code="AF010101", area_type=admin_type_3)
    return area1, area2


def test_upload_single_person(token_api_client, push_people_url, program, rdi, afghanistan_country) -> None:
    data = [
        {
            "residence_status": "IDP",
            "village": "village1",
            "country": "AF",
            "full_name": "John Doe",
            "birth_date": "2000-01-01",
            "sex": "NOT_COLLECTED",
            "type": "",
            "program": str(program.id),
            "country_workspace_id": "cw-single-1",
        }
    ]
    response = token_api_client.post(push_people_url, data, format="json")
    assert response.status_code == status.HTTP_201_CREATED, str(response.json())
    response_json = response.json()

    rdi_obj = RegistrationDataImport.objects.filter(id=response_json["id"]).first()
    assert rdi_obj is not None
    assert rdi_obj.program == program

    hh = PendingHousehold.objects.filter(registration_data_import=rdi_obj).first()
    ind = PendingIndividual.objects.filter(registration_data_import=rdi_obj).first()
    assert hh is not None
    assert ind is not None
    assert hh.head_of_household == ind
    assert hh.primary_collector == ind
    assert hh.village == "village1"

    assert ind.full_name == "John Doe"
    assert ind.sex == NOT_COLLECTED
    assert ind.relationship == HEAD

    assert response_json["id"] == str(rdi.id)
    assert len(response_json["people"]) == 1


def test_upload_multiple_people_with_documents(
    token_api_client, push_people_url, program, rdi, birth_certificate_doc_type, afghanistan_country
) -> None:
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
            "program": str(program.id),
            "country_workspace_id": "cw-multi-john",
        },
        {
            "residence_status": "IDP",
            "village": "village2",
            "country": "AF",
            "full_name": "Mary Doe",
            "birth_date": "1990-01-01",
            "sex": "FEMALE",
            "type": "",
            "program": str(program.id),
            "country_workspace_id": "cw-multi-mary",
        },
    ]
    response = token_api_client.post(push_people_url, data, format="json")
    assert response.status_code == status.HTTP_201_CREATED, str(response.json())
    response_json = response.json()

    rdi_obj = RegistrationDataImport.objects.filter(id=response_json["id"]).first()
    assert rdi_obj is not None
    assert len(response_json["people"]) == 2

    households = PendingHousehold.objects.filter(registration_data_import=rdi_obj)
    assert len(households) == 2

    individuals = PendingIndividual.objects.filter(registration_data_import=rdi_obj)
    assert len(individuals) == 2

    john_doe = PendingIndividual.objects.filter(full_name="John Doe").first()
    assert john_doe is not None
    assert john_doe.full_name == "John Doe"
    assert john_doe.sex == MALE

    mary_doe = PendingIndividual.objects.filter(full_name="Mary Doe").first()
    assert mary_doe is not None
    assert mary_doe.full_name == "Mary Doe"
    assert mary_doe.sex == FEMALE

    document = PendingDocument.objects.filter(individual=john_doe).first()
    assert document is not None
    assert document.document_number == "10"


def test_upload_with_errors(token_api_client, push_people_url, program, afghanistan_country) -> None:
    data = [
        {
            "residence_status": "IDP",
            "country": "AF",
            "full_name": "John Doe",
            "sex": "MALE",
            "documents": [
                {
                    "image": "",
                    "country": "AF",
                }
            ],
            "program": str(program.id),
            "country_workspace_id": "cw-err-john",
        },
        {
            "residence_status": "IDP",
            "village": "village2",
            "country": "AF",
            "full_name": "Mary Doe",
            "sex": "FEMALE",
            "program": str(program.id),
            "country_workspace_id": "cw-err-mary",
        },
    ]
    response = token_api_client.post(push_people_url, data, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST, str(response.json())
    assert response.json() == [
        {
            "birth_date": ["This field is required."],
            "documents": [
                {
                    "document_number": ["This field is required."],
                    "type": ["This field is required."],
                }
            ],
            "type": ["This field is required."],
        },
        {
            "birth_date": ["This field is required."],
            "type": ["This field is required."],
        },
    ]


@pytest.mark.parametrize(
    ("field_name", "phone_number", "expected_value"),
    [
        ("phone_no", "invalid", False),
        ("phone_no_alternative", "invalid", False),
        ("phone_no", "+48 632 215 789", True),
        ("phone_no_alternative", "+48 632 215 789", True),
        ("phone_no_alternative", None, False),
        ("phone_no", None, False),
    ],
    ids=[
        "invalid_phone_no",
        "invalid_phone_no_alternative",
        "valid_phone_no",
        "valid_phone_no_alternative",
        "phone_no_alternative_as_null",
        "phone_no_as_null",
    ],
)
def test_upload_single_person_with_phone_number(
    token_api_client, push_people_url, program, rdi, afghanistan_country, field_name, phone_number, expected_value
) -> None:
    data = [
        {
            "residence_status": "IDP",
            "village": "village1",
            "country": "AF",
            "full_name": "John Doe",
            "birth_date": "2000-01-01",
            "sex": "MALE",
            "type": "",
            field_name: phone_number,
            "program": str(program.id),
            "country_workspace_id": "cw-phone-1",
        }
    ]
    response = token_api_client.post(push_people_url, data, format="json")
    assert response.status_code == status.HTTP_201_CREATED, str(response.json())
    response_json = response.json()

    rdi_obj = RegistrationDataImport.objects.filter(id=response_json["id"]).first()
    assert rdi_obj is not None
    ind = PendingIndividual.objects.filter(registration_data_import=rdi_obj).first()
    assert ind is not None
    assert ind.full_name == "John Doe"
    assert getattr(ind, f"{field_name}_valid") == expected_value


@pytest.mark.parametrize(
    ("village", "expected_value"),
    [
        ("village1", "village1"),
        ("", ""),
        (None, ""),
    ],
    ids=["valid-village", "empty-village", "null-village"],
)
def test_push_single_person_with_village(
    token_api_client, push_people_url, program, rdi, afghanistan_country, village, expected_value
) -> None:
    data = [
        {
            "residence_status": "IDP",
            "village": village,
            "country": "AF",
            "full_name": "John Doe",
            "birth_date": "2000-01-01",
            "sex": "MALE",
            "type": "",
            "program": str(program.id),
            "country_workspace_id": "cw-village-1",
        }
    ]
    response = token_api_client.post(push_people_url, data, format="json")
    assert response.status_code == status.HTTP_201_CREATED, str(response.json())
    response_json = response.json()

    rdi_obj = RegistrationDataImport.objects.filter(id=response_json["id"]).first()
    assert rdi_obj is not None
    ind = PendingIndividual.objects.filter(registration_data_import=rdi_obj).first()
    assert ind.household.village == expected_value


def test_push_single_person_with_admin_areas(token_api_client, push_people_url, program, rdi, admin_areas) -> None:
    data = [
        {
            "residence_status": "IDP",
            "village": "village1",
            "country": "AF",
            "full_name": "John Doe",
            "birth_date": "2000-01-01",
            "sex": "MALE",
            "type": "",
            "admin1": "AF01",
            "admin2": "AF0101",
            "admin3": "",
            "admin4": None,
            "program": str(program.id),
            "country_workspace_id": "cw-admin-1",
        }
    ]
    response = token_api_client.post(push_people_url, data, format="json")
    assert response.status_code == status.HTTP_201_CREATED, str(response.json())
    response_json = response.json()

    rdi_obj = RegistrationDataImport.objects.filter(id=response_json["id"]).first()
    assert rdi_obj is not None
    ind = PendingIndividual.objects.filter(registration_data_import=rdi_obj).first()
    assert ind.household.admin1.p_code == "AF01"
    assert ind.household.admin2.p_code == "AF0101"
    assert ind.household.admin3 is None
    assert ind.household.admin4 is None


@pytest.fixture
def base64_photo() -> tuple[str, str]:
    prefix = "data:image/png;base64,"
    buffer = BytesIO()
    image = Image.new("RGB", (1, 1), color="blue")
    image.save(buffer, format="PNG")
    photo_data = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"{prefix}{photo_data}", photo_data


def test_create_individual_with_photo_remove_prefix(rdi, base64_photo) -> None:
    base64_photo_with_prefix, photo_data = base64_photo
    prefix = "data:image/png;base64,"

    person_data = {
        "type": "NON_BENEFICIARY",
        "photo": base64_photo_with_prefix,
        "first_name": "WithPhoto",
        "birth_date": "2000-01-01",
        "first_registration_date": "2000-01-01",
        "last_registration_date": "2000-01-01",
    }
    assert base64_photo_with_prefix.startswith(prefix) is True
    people_upload_mixin = PeopleUploadMixin()
    people_upload_mixin.selected_rdi = rdi
    individual = people_upload_mixin._create_individual(
        documents=[],
        accounts=[],
        hh=None,
        person_data=person_data,
        rdi=rdi,
    )

    assert individual.photo.name.startswith(rdi.program.code)
    assert individual.photo.name.endswith(".png")
    photo_saved = base64.b64encode(individual.photo.read()).decode("utf-8")
    assert photo_saved.startswith(prefix) is False
    assert photo_saved == photo_data


@pytest.fixture
def common_serializer_data() -> dict[str, str]:
    return {
        "type": "",
        "birth_date": "2000-01-01",
        "full_name": "John Doe",
        "sex": "MALE",
        "country_origin": "",
        "country_workspace_id": "cw-serializer-1",
    }


@pytest.mark.parametrize(
    ("disability_value", "expected"),
    [
        ("", NOT_DISABLED),
        ("disabled", DISABLED),
    ],
    ids=["empty-disability", "disabled"],
)
def test_people_serializer_disability(common_serializer_data, disability_value, expected) -> None:
    serializer = PushPeopleSerializer(data={**common_serializer_data, "disability": disability_value})
    serializer.is_valid()
    assert serializer.validated_data.get("disability") == expected


def test_push_single_person_stores_country_workspace_id(
    token_api_client, push_people_url, program, rdi, afghanistan_country
) -> None:
    data = [
        {
            "residence_status": "IDP",
            "village": "village1",
            "country": "AF",
            "full_name": "John Doe",
            "birth_date": "2000-01-01",
            "sex": "MALE",
            "type": "",
            "program": str(program.id),
            "country_workspace_id": "42",
        }
    ]
    response = token_api_client.post(push_people_url, data, format="json")
    assert response.status_code == status.HTTP_201_CREATED, str(response.json())
    response_json = response.json()

    rdi_obj = RegistrationDataImport.objects.filter(id=response_json["id"]).first()
    assert rdi_obj is not None
    ind = PendingIndividual.objects.filter(registration_data_import=rdi_obj).first()
    assert ind is not None
    assert ind.country_workspace_id == "42"
