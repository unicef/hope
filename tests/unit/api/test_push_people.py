from collections.abc import Callable

import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from extras.test_utils.factories.core import BeneficiaryGroupFactory, DataCollectingTypeFactory
from extras.test_utils.factories.geo import AreaFactory, AreaTypeFactory
from extras.test_utils.factories.household import DocumentTypeFactory
from extras.test_utils.factories.program import ProgramFactory
from extras.test_utils.factories.registration_data import RegistrationDataImportFactory
from hope.api.endpoints.rdi.push_people import PeopleUploadMixin, PushPeopleSerializer
from hope.api.endpoints.rdi.stored_images import get_stored_image_prefix
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
    PendingAccount,
    PendingDocument,
    PendingHousehold,
    PendingIndividual,
    Program,
    RegistrationDataImport,
)

pytestmark = pytest.mark.django_db

PHOTO_MAX_LENGTH = PendingIndividual._meta.get_field("photo").max_length


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
    assert response.json() == {
        "0": {
            "birth_date": ["This field is required."],
            "documents": {
                "0": {
                    "document_number": ["This field is required."],
                    "type": ["This field is required."],
                }
            },
            "type": ["This field is required."],
        },
        "1": {
            "birth_date": ["This field is required."],
            "type": ["This field is required."],
        },
    }


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


def test_push_single_person_with_currency(
    token_api_client, push_people_url, program, rdi, afghanistan_country, currency_usd
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
            "currency": "USD",
            "program": str(program.id),
            "country_workspace_id": "cw-currency-1",
        }
    ]
    response = token_api_client.post(push_people_url, data, format="json")
    assert response.status_code == status.HTTP_201_CREATED, str(response.json())
    response_json = response.json()

    rdi_obj = RegistrationDataImport.objects.filter(id=response_json["id"]).first()
    assert rdi_obj is not None
    ind = PendingIndividual.objects.filter(registration_data_import=rdi_obj).first()
    assert ind is not None
    assert ind.household.currency is not None
    assert ind.household.currency.code == "USD"


@pytest.mark.parametrize(("code", "expected_queries"), [("SYP", 27), ("SYP01", 29)])
def test_push_single_person_resolves_the_currency_code_to_the_active_row(
    token_api_client,
    push_people_url,
    program,
    rdi,
    afghanistan_country,
    currency_syp,
    code,
    expected_queries,
    django_assert_num_queries,
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
            "currency": code,
            "program": str(program.id),
            "country_workspace_id": "cw-currency-1",
        }
    ]

    with django_assert_num_queries(expected_queries):
        response = token_api_client.post(push_people_url, data, format="json")

    assert response.status_code == status.HTTP_201_CREATED, str(response.json())
    household = PendingHousehold.objects.get(registration_data_import_id=response.json()["id"])
    assert household.currency == currency_syp


def test_push_single_person_with_a_retired_currency_is_rejected(
    token_api_client, push_people_url, program, rdi, afghanistan_country, currency_retired
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
            "currency": "VEF",
            "program": str(program.id),
            "country_workspace_id": "cw-currency-1",
        }
    ]

    response = token_api_client.post(push_people_url, data, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"0": {"currency": ["Object with code=VEF does not exist."]}}
    assert not PendingHousehold.objects.exists()


@pytest.fixture
def file_prefix(business_area, program) -> str:
    return get_stored_image_prefix(business_area.code, program.code)


@pytest.fixture
def stored_image(store_image: Callable[[str], str], file_prefix: str) -> str:
    return store_image(f"{file_prefix}CW_ind_1_photo.png")


@pytest.fixture
def person_payload(program) -> dict:
    return {
        "residence_status": "IDP",
        "village": "village1",
        "country": "AF",
        "full_name": "John Doe",
        "birth_date": "2000-01-01",
        "sex": "NOT_COLLECTED",
        "type": "",
        "program": str(program.id),
        "country_workspace_id": "cw-files-1",
    }


def test_upload_person_with_files_keeps_the_file_names(
    token_api_client,
    push_people_url,
    person_payload,
    stored_image,
    store_image,
    file_prefix,
    birth_certificate_doc_type,
    afghanistan_country,
) -> None:
    certificate = store_image(f"{file_prefix}CW_ind_1_disability_certificate_picture.png")
    document_image = store_image(f"{file_prefix}CW_doc_1_image.png")
    person_payload |= {
        "photo": f"/{stored_image}",
        "disability_certificate_picture": certificate,
        "documents": [
            {
                "document_number": "10",
                "image": document_image,
                "country": "AF",
                "type": birth_certificate_doc_type.key,
            }
        ],
    }

    response = token_api_client.post(push_people_url, [person_payload], format="json")

    assert response.status_code == status.HTTP_201_CREATED, str(response.json())
    individual = PendingIndividual.objects.get(country_workspace_id="cw-files-1")
    assert individual.photo.name == stored_image
    assert individual.disability_certificate_picture.name == certificate
    assert individual.documents.get().photo.name == document_image


@pytest.mark.parametrize("empty_certificate", ["", None])
def test_upload_person_with_empty_files(
    token_api_client,
    push_people_url,
    person_payload,
    birth_certificate_doc_type,
    afghanistan_country,
    empty_certificate,
) -> None:
    person_payload |= {
        "photo": "",
        "disability_certificate_picture": empty_certificate,
        "documents": [{"document_number": "10", "image": "", "country": "AF", "type": birth_certificate_doc_type.key}],
    }

    response = token_api_client.post(push_people_url, [person_payload], format="json")

    assert response.status_code == status.HTTP_201_CREATED, str(response.json())
    individual = PendingIndividual.objects.get(country_workspace_id="cw-files-1")
    assert not individual.photo
    assert not individual.disability_certificate_picture
    assert not individual.documents.get().photo


@pytest.mark.parametrize("field", ["photo", "disability_certificate_picture"])
def test_upload_person_with_missing_file_returns_error(
    token_api_client, push_people_url, person_payload, file_prefix, field
) -> None:
    person_payload[field] = f"{file_prefix}does_not_exist.png"

    response = token_api_client.post(push_people_url, [person_payload], format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"0": {field: [f"File '{file_prefix}does_not_exist.png' does not exist in storage."]}}
    assert not PendingIndividual.objects.exists()


def test_upload_person_with_missing_document_image_returns_error(
    token_api_client, push_people_url, person_payload, file_prefix, birth_certificate_doc_type, afghanistan_country
) -> None:
    person_payload["documents"] = [
        {
            "document_number": "10",
            "image": f"{file_prefix}does_not_exist.png",
            "country": "AF",
            "type": birth_certificate_doc_type.key,
        }
    ]

    response = token_api_client.post(push_people_url, [person_payload], format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        "0": {"documents": {"0": {"image": [f"File '{file_prefix}does_not_exist.png' does not exist in storage."]}}}
    }
    assert not PendingIndividual.objects.exists()


def test_upload_person_with_unsafe_file_name_returns_error(token_api_client, push_people_url, person_payload) -> None:
    person_payload["photo"] = "../../etc/passwd"

    response = token_api_client.post(push_people_url, [person_payload], format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"0": {"photo": ["Invalid file name '../../etc/passwd'."]}}


@pytest.mark.parametrize("field", ["photo", "disability_certificate_picture"])
def test_upload_person_with_file_name_longer_than_the_column_returns_error(
    token_api_client, push_people_url, person_payload, file_prefix, field
) -> None:
    person_payload[field] = f"{file_prefix}{'a' * PHOTO_MAX_LENGTH}.png"

    response = token_api_client.post(push_people_url, [person_payload], format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"0": {field: [f"File name must have no more than {PHOTO_MAX_LENGTH} characters."]}}


@pytest.mark.parametrize("field", ["photo", "disability_certificate_picture"])
def test_upload_person_with_file_of_another_program_returns_error(
    token_api_client, push_people_url, person_payload, file_prefix, store_image, field
) -> None:
    other_program_file = store_image("OTH/zz99/CW_ind_1_photo.png")
    person_payload[field] = other_program_file

    response = token_api_client.post(push_people_url, [person_payload], format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"0": {field: [f"File name must start with '{file_prefix}'."]}}
    assert not PendingIndividual.objects.exists()


def test_create_individual_passes_the_file_names_through(rdi, stored_image) -> None:
    person_data = {
        "type": "NON_BENEFICIARY",
        "photo": stored_image,
        "first_name": "WithPhoto",
        "birth_date": "2000-01-01",
        "first_registration_date": "2000-01-01",
        "last_registration_date": "2000-01-01",
    }
    people_upload_mixin = PeopleUploadMixin()
    people_upload_mixin.selected_rdi = rdi

    individual = people_upload_mixin._create_individual(
        documents=[],
        accounts=[],
        hh=None,
        person_data=person_data,
        rdi=rdi,
    )

    assert individual.photo.name == stored_image


def test_create_individual_resolves_the_programme_without_refetching_it(rdi, stored_image, django_assert_num_queries):
    person_data = {
        "type": "NON_BENEFICIARY",
        "photo": stored_image,
        "first_name": "WithPhoto",
        "birth_date": "2000-01-01",
        "first_registration_date": "2000-01-01",
        "last_registration_date": "2000-01-01",
    }
    people_upload_mixin = PeopleUploadMixin()
    people_upload_mixin.selected_rdi = rdi

    with django_assert_num_queries(6):
        individual = people_upload_mixin._create_individual(
            documents=[],
            accounts=[],
            hh=None,
            person_data=person_data,
            rdi=rdi,
        )

    assert individual.program == rdi.program


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


def test_push_people_creates_account_attachments(
    token_api_client,
    push_people_url,
    program,
    rdi,
    afghanistan_country,
    bank_account_type,
    generic_bank,
    base64_image,
) -> None:
    data = [
        {
            "residence_status": "IDP",
            "country": "AF",
            "full_name": "Jane Wallet",
            "birth_date": "2000-01-01",
            "sex": "FEMALE",
            "type": "",
            "program": str(program.id),
            "country_workspace_id": "cw-wallet-attachments",
            "accounts": [
                {
                    "type": "bank",
                    "number": "123",
                    "attachments": [{"title": "Wallet number image", "file": base64_image}],
                }
            ],
        }
    ]

    response = token_api_client.post(push_people_url, data, format="json")

    assert response.status_code == status.HTTP_201_CREATED, str(response.json())
    account = PendingAccount.objects.get(individual__full_name="Jane Wallet")
    attachment = account.attachments.get()
    assert attachment.title == "Wallet number image"
    assert attachment.file.name
