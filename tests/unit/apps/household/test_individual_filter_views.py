from typing import Any, Callable, Dict, Optional, Tuple

from constance.test import override_config
from django.utils import timezone
import freezegun
import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from extras.test_utils.factories import (
    AreaFactory,
    AreaTypeFactory,
    BusinessAreaFactory,
    CountryFactory,
    DocumentFactory,
    DocumentTypeFactory,
    HouseholdFactory,
    PartnerFactory,
    ProgramFactory,
    RegistrationDataImportFactory,
    UserFactory,
)
from hope.apps.account.permissions import Permissions
from hope.apps.household.const import (
    DUPLICATE,
    FEMALE,
    MALE,
    NEEDS_ADJUDICATION,
    NOT_COLLECTED,
    OTHER,
    STATUS_ACTIVE,
    UNIQUE,
)
from hope.apps.utils.elasticsearch_utils import rebuild_search_index
from hope.models import BusinessArea, Individual, MergeStatusModel, Program

pytestmark = [pytest.mark.django_db]


def _create_test_individuals(
    program: Program,
    afghanistan: BusinessArea,
    individual1_data: Optional[dict] = None,
    individual2_data: Optional[dict] = None,
    household1_data: Optional[dict] = None,
    household2_data: Optional[dict] = None,
) -> Tuple[Individual, Individual]:
    hh1 = HouseholdFactory(program=program, business_area=afghanistan, **(household1_data or {}))
    individual1 = hh1.head_of_household
    for field, value in (individual1_data or {}).items():
        setattr(individual1, field, value)
    if individual1_data:
        individual1.save()

    hh2 = HouseholdFactory(program=program, business_area=afghanistan, **(household2_data or {}))
    individual2 = hh2.head_of_household
    for field, value in (individual2_data or {}).items():
        setattr(individual2, field, value)
    if individual2_data:
        individual2.save()

    return individual1, individual2


@pytest.fixture
def afghanistan() -> BusinessArea:
    return BusinessAreaFactory(name="Afghanistan", slug="afghanistan", code="0060")


@pytest.fixture
def program(afghanistan: BusinessArea) -> Program:
    return ProgramFactory(business_area=afghanistan, status=Program.ACTIVE)


@pytest.fixture
def user(afghanistan: BusinessArea, program: Program, create_user_role_with_permissions: Callable) -> Any:
    partner = PartnerFactory(name="TestPartner")
    user = UserFactory(partner=partner)
    create_user_role_with_permissions(
        user=user,
        permissions=[Permissions.POPULATION_VIEW_INDIVIDUALS_LIST],
        business_area=afghanistan,
        program=program,
    )
    return user


@pytest.fixture
def client(api_client: Callable, user: Any, mock_elasticsearch: Any) -> Any:
    return api_client(user)


@pytest.fixture
def list_url(afghanistan: BusinessArea, program: Program) -> str:
    return reverse(
        "api:households:individuals-list",
        kwargs={"business_area_slug": afghanistan.slug, "program_code": program.code},
    )


def _test_filter_individuals_in_list(
    client: Any,
    list_url: str,
    filters: dict,
    program: Program,
    afghanistan: BusinessArea,
    individual1_data: Optional[dict] = None,
    individual2_data: Optional[dict] = None,
    household1_data: Optional[dict] = None,
    household2_data: Optional[dict] = None,
) -> None:
    individual1, individual2 = _create_test_individuals(
        program,
        afghanistan,
        individual1_data=individual1_data,
        individual2_data=individual2_data,
        household1_data=household1_data,
        household2_data=household2_data,
    )
    response = client.get(list_url, filters)
    assert response.status_code == status.HTTP_200_OK, response.json()
    response_data = response.json()["results"]
    assert len(response_data) == 1
    assert response_data[0]["id"] == str(individual2.id)


def test_filter_by_rdi_id(client: Any, list_url: str, user: Any, afghanistan: BusinessArea, program: Program) -> None:
    registration_data_import_1 = RegistrationDataImportFactory(
        imported_by=user, business_area=afghanistan, program=program
    )
    registration_data_import_2 = RegistrationDataImportFactory(
        imported_by=user, business_area=afghanistan, program=program
    )
    _test_filter_individuals_in_list(
        client,
        list_url,
        {"rdi_id": registration_data_import_2.id},
        program,
        afghanistan,
        individual1_data={"registration_data_import": registration_data_import_1},
        individual2_data={"registration_data_import": registration_data_import_2},
    )


def test_filter_by_document_number(client: Any, list_url: str, afghanistan: BusinessArea, program: Program) -> None:
    document_passport = DocumentTypeFactory(key="passport")
    document_id_card = DocumentTypeFactory(key="id_card")
    individual1, individual2 = _create_test_individuals(program, afghanistan)
    individual3, individual4 = _create_test_individuals(program, afghanistan)
    DocumentFactory(individual=individual1, type=document_passport, document_number="123")
    DocumentFactory(individual=individual2, type=document_passport, document_number="456")
    DocumentFactory(individual=individual3, type=document_id_card, document_number="123")
    DocumentFactory(individual=individual4, type=document_id_card, document_number="456")
    response = client.get(list_url, {"document_number": "456", "document_type": "passport"})
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()["results"]
    assert len(response_data) == 1
    assert response_data[0]["id"] == str(individual2.id)


def test_filter_by_full_name(client: Any, list_url: str, afghanistan: BusinessArea, program: Program) -> None:
    _test_filter_individuals_in_list(
        client,
        list_url,
        {"full_name": "John"},
        program,
        afghanistan,
        individual1_data={"full_name": "Jane Doe"},
        individual2_data={"full_name": "John Doe"},
    )


def test_filter_by_sex(client: Any, list_url: str, afghanistan: BusinessArea, program: Program) -> None:
    individual_m, individual_f = _create_test_individuals(
        program, afghanistan, individual1_data={"sex": MALE}, individual2_data={"sex": FEMALE}
    )
    individual_o, individual_nc = _create_test_individuals(
        program, afghanistan, individual1_data={"sex": OTHER}, individual2_data={"sex": NOT_COLLECTED}
    )
    response_male = client.get(list_url, {"sex": "MALE"})
    assert response_male.status_code == status.HTTP_200_OK
    response_data_male = response_male.json()["results"]
    assert len(response_data_male) == 1
    assert response_data_male[0]["id"] == str(individual_m.id)

    response_male_female = client.get(list_url, {"sex": ["MALE", "FEMALE"]})
    assert response_male_female.status_code == status.HTTP_200_OK
    response_data_male_female = response_male_female.json()["results"]
    assert len(response_data_male_female) == 2
    individuals_ids = [individual["id"] for individual in response_data_male_female]
    assert str(individual_m.id) in individuals_ids
    assert str(individual_f.id) in individuals_ids
    assert str(individual_o.id) not in individuals_ids
    assert str(individual_nc.id) not in individuals_ids


def test_filter_by_status(client: Any, list_url: str, afghanistan: BusinessArea, program: Program) -> None:
    _test_filter_individuals_in_list(
        client,
        list_url,
        {"status": STATUS_ACTIVE},
        program,
        afghanistan,
        individual1_data={"duplicate": True},
        individual2_data={"duplicate": False, "withdrawn": False},
    )


def test_filter_by_flags(client: Any, list_url: str, afghanistan: BusinessArea, program: Program) -> None:
    _test_filter_individuals_in_list(
        client,
        list_url,
        {"flags": NEEDS_ADJUDICATION},
        program,
        afghanistan,
        individual2_data={"deduplication_golden_record_status": NEEDS_ADJUDICATION},
    )


def test_filter_by_withdrawn(client: Any, list_url: str, afghanistan: BusinessArea, program: Program) -> None:
    _test_filter_individuals_in_list(
        client,
        list_url,
        {"withdrawn": True},
        program,
        afghanistan,
        individual1_data={"withdrawn": False},
        individual2_data={"withdrawn": True},
    )


def test_filter_by_excluded_id(client: Any, list_url: str, afghanistan: BusinessArea, program: Program) -> None:
    individual1, individual2 = _create_test_individuals(program, afghanistan)
    response = client.get(list_url, {"excluded_id": str(individual1.id)})
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()["results"]
    assert len(response_data) == 1
    assert response_data[0]["id"] == str(individual2.id)


@pytest.mark.parametrize(
    ("program_status", "filter_value", "expected_results"),
    [
        (Program.ACTIVE, True, 2),
        (Program.FINISHED, True, 0),
        (Program.ACTIVE, False, 0),
        (Program.FINISHED, False, 2),
    ],
)
def test_filter_by_is_active_program(
    client: Any,
    list_url: str,
    afghanistan: BusinessArea,
    program: Program,
    program_status: str,
    filter_value: bool,
    expected_results: int,
) -> None:
    program.status = program_status
    program.save()
    _create_test_individuals(program, afghanistan)
    response = client.get(list_url, {"is_active_program": filter_value})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["results"]) == expected_results


def test_filter_by_rdi_merge_status(client: Any, list_url: str, afghanistan: BusinessArea, program: Program) -> None:
    _test_filter_individuals_in_list(
        client,
        list_url,
        {"rdi_merge_status": MergeStatusModel.PENDING},
        program,
        afghanistan,
        individual1_data={"rdi_merge_status": MergeStatusModel.MERGED},
        individual2_data={"rdi_merge_status": MergeStatusModel.PENDING},
    )


@pytest.mark.parametrize("filter_by_field", ["admin1", "admin2"])
def test_filter_by_area(
    client: Any, list_url: str, afghanistan: BusinessArea, program: Program, filter_by_field: str
) -> None:
    country = CountryFactory()
    admin_type_1 = AreaTypeFactory(country=country, area_level=1)
    admin_type_2 = AreaTypeFactory(country=country, area_level=2, parent=admin_type_1)
    area1 = AreaFactory(parent=None, p_code="AF01", area_type=admin_type_1)
    area2 = AreaFactory(parent=area1, p_code="AF0101", area_type=admin_type_2)
    _test_filter_individuals_in_list(
        client,
        list_url,
        {filter_by_field: str(area2.id)},
        program,
        afghanistan,
        household1_data={filter_by_field: area1},
        household2_data={filter_by_field: area2},
    )


def test_filter_by_last_registration_date(
    client: Any, list_url: str, afghanistan: BusinessArea, program: Program
) -> None:
    import datetime

    individual1, individual2 = _create_test_individuals(
        program,
        afghanistan,
        individual1_data={"last_registration_date": timezone.make_aware(datetime.datetime(2021, 1, 1))},
        individual2_data={"last_registration_date": timezone.make_aware(datetime.datetime(2023, 1, 1))},
    )
    response_after = client.get(list_url, {"last_registration_date_after": "2022-12-31"})
    assert response_after.status_code == status.HTTP_200_OK
    response_data_after = response_after.json()["results"]
    assert len(response_data_after) == 1
    assert response_data_after[0]["id"] == str(individual2.id)

    response_before = client.get(list_url, {"last_registration_date_before": "2022-12-31"})
    assert response_before.status_code == status.HTTP_200_OK
    response_data_before = response_before.json()["results"]
    assert len(response_data_before) == 1
    assert response_data_before[0]["id"] == str(individual1.id)


def test_filter_by_duplicates_only(client: Any, list_url: str, afghanistan: BusinessArea, program: Program) -> None:
    _test_filter_individuals_in_list(
        client,
        list_url,
        {"duplicates_only": True},
        program,
        afghanistan,
        individual1_data={"deduplication_golden_record_status": UNIQUE},
        individual2_data={"deduplication_golden_record_status": DUPLICATE},
    )


def test_filter_by_age(client: Any, list_url: str, afghanistan: BusinessArea, program: Program) -> None:
    individual_age_5, individual_age_10 = _create_test_individuals(
        program,
        afghanistan,
        individual1_data={"birth_date": "2014-10-10"},
        individual2_data={"birth_date": "2009-10-10"},
    )
    individual_age_15, individual_age_20 = _create_test_individuals(
        program,
        afghanistan,
        individual1_data={"birth_date": "2004-10-10"},
        individual2_data={"birth_date": "1999-10-10"},
    )
    with freezegun.freeze_time("2019-11-10"):
        response_min = client.get(list_url, {"age_min": 8})
        assert response_min.status_code == status.HTTP_200_OK
        individuals_ids_min = [individual["id"] for individual in response_min.json()["results"]]
        assert len(individuals_ids_min) == 3
        assert str(individual_age_10.id) in individuals_ids_min
        assert str(individual_age_15.id) in individuals_ids_min
        assert str(individual_age_20.id) in individuals_ids_min
        assert str(individual_age_5.id) not in individuals_ids_min

        response_max = client.get(list_url, {"age_max": 12})
        assert response_max.status_code == status.HTTP_200_OK
        individuals_ids_max = [individual["id"] for individual in response_max.json()["results"]]
        assert len(individuals_ids_max) == 2
        assert str(individual_age_5.id) in individuals_ids_max
        assert str(individual_age_10.id) in individuals_ids_max
        assert str(individual_age_15.id) not in individuals_ids_max
        assert str(individual_age_20.id) not in individuals_ids_max

        response_min_max = client.get(list_url, {"age_min": 8, "age_max": 12})
        assert response_min_max.status_code == status.HTTP_200_OK
        individuals_ids_min_max = [individual["id"] for individual in response_min_max.json()["results"]]
        assert len(individuals_ids_min_max) == 1
        assert str(individual_age_10.id) in individuals_ids_min_max
        assert str(individual_age_5.id) not in individuals_ids_min_max
        assert str(individual_age_15.id) not in individuals_ids_min_max
        assert str(individual_age_20.id) not in individuals_ids_min_max


@pytest.fixture
def search_user(afghanistan: BusinessArea, create_user_role_with_permissions: Callable) -> Any:
    partner = PartnerFactory(name="SearchPartner")
    user = UserFactory(partner=partner)
    create_user_role_with_permissions(
        user=user,
        permissions=[Permissions.POPULATION_VIEW_INDIVIDUALS_LIST],
        business_area=afghanistan,
        whole_business_area_access=True,
    )
    return user


@pytest.fixture
def search_client(api_client: Callable, search_user: Any) -> Any:
    return api_client(search_user)


def _test_search(
    client: Any,
    list_url: str,
    afghanistan: BusinessArea,
    program: Program,
    filters: Dict,
    individual1_data: Dict,
    individual2_data: Dict,
    household1_data: Dict,
    household2_data: Dict,
    is_elasticsearch_enabled: bool = False,
) -> tuple[Any, list[Individual]]:
    program2 = ProgramFactory(business_area=afghanistan, status=Program.ACTIVE)

    individual1_p1, individual2_p1 = _create_test_individuals(
        program,
        afghanistan,
        individual1_data={**individual1_data},
        individual2_data={**individual2_data},
        household1_data={**household1_data},
        household2_data={**household2_data},
    )
    individual1_p2, individual2_p2 = _create_test_individuals(
        program2,
        afghanistan,
        individual1_data={**individual1_data},
        individual2_data={**individual2_data},
        household1_data={**household1_data},
        household2_data={**household2_data},
    )
    if is_elasticsearch_enabled:
        rebuild_search_index()
    response = client.get(list_url, filters)
    assert response.status_code == status.HTTP_200_OK, response.json()
    return response.json()["results"], [individual1_p1, individual2_p1, individual1_p2, individual2_p2]


@pytest.mark.xdist_group(name="elasticsearch")
@override_config(IS_ELASTICSEARCH_ENABLED=True)
@pytest.mark.elasticsearch
@pytest.mark.usefixtures("django_elasticsearch_setup")
@pytest.mark.parametrize(
    ("filters", "individual1_data", "individual2_data", "household1_data", "household2_data"),
    [
        ({"search": "IND-123"}, {"unicef_id": "IND-321"}, {"unicef_id": "IND-123"}, {}, {}),
        ({"search": "HH-123"}, {}, {}, {"unicef_id": "HH-321"}, {"unicef_id": "HH-123"}),
        ({"search": "John Root"}, {"full_name": "Jack Root"}, {"full_name": "John Root"}, {}, {}),
        ({"search": "+48010101010"}, {"phone_no": "+48 609 456 008"}, {"phone_no": "+48 010 101 010"}, {}, {}),
        ({"search": "HOPE-123"}, {"detail_id": "HOPE-321"}, {"detail_id": "HOPE-123"}, {}, {}),
        ({"search": "456"}, {"program_registration_id": "123"}, {"program_registration_id": "456"}, {}, {}),
    ],
)
def test_search(
    search_client: Any,
    list_url: str,
    afghanistan: BusinessArea,
    program: Program,
    filters: Dict,
    individual1_data: Dict,
    individual2_data: Dict,
    household1_data: Dict,
    household2_data: Dict,
) -> None:
    response_data, individuals = _test_search(
        search_client,
        list_url,
        afghanistan,
        program,
        filters,
        individual1_data,
        individual2_data,
        household1_data,
        household2_data,
        is_elasticsearch_enabled=True,
    )
    assert len(response_data) == 1
    assert response_data[0]["id"] == str(individuals[1].id)


@pytest.mark.parametrize(
    ("filters", "individual1_data", "individual2_data", "household1_data", "household2_data"),
    [
        ({"search": "IND-987"}, {"unicef_id": "IND-654"}, {"unicef_id": "IND-987"}, {}, {}),
        ({"search": "HH-987"}, {}, {}, {"unicef_id": "HH-654"}, {"unicef_id": "HH-987"}),
        ({"search": "John Root"}, {"full_name": "Jack Root"}, {"full_name": "John Root"}, {}, {}),
        ({"search": "+48010101010"}, {"phone_no": "+48 609 456 008"}, {"phone_no": "+48 010 101 010"}, {}, {}),
        ({"search": "HOPE-987"}, {"detail_id": "HOPE-654"}, {"detail_id": "HOPE-987"}, {}, {}),
        ({"search": "786"}, {"program_registration_id": "456"}, {"program_registration_id": "786"}, {}, {}),
    ],
)
def test_search_db(
    search_client: Any,
    list_url: str,
    afghanistan: BusinessArea,
    program: Program,
    filters: Dict,
    individual1_data: Dict,
    individual2_data: Dict,
    household1_data: Dict,
    household2_data: Dict,
) -> None:
    program.status = Program.FINISHED
    program.save()
    response_data, individuals = _test_search(
        search_client,
        list_url,
        afghanistan,
        program,
        filters,
        individual1_data,
        individual2_data,
        household1_data,
        household2_data,
    )
    assert len(response_data) == 1
    assert response_data[0]["id"] == str(individuals[1].id)


@pytest.mark.parametrize(
    ("filters", "individual1_data", "individual2_data", "household1_data", "household2_data"),
    [
        ({"search": "IND-987"}, {"unicef_id": "IND-654"}, {"unicef_id": "IND-987"}, {}, {}),
        ({"search": "HH-987"}, {}, {}, {"unicef_id": "HH-654"}, {"unicef_id": "HH-987"}),
        ({"search": "John Root"}, {"full_name": "Jack Root"}, {"full_name": "John Root"}, {}, {}),
        ({"search": "+48010101010"}, {"phone_no": "+48 609 456 008"}, {"phone_no": "+48 010 101 010"}, {}, {}),
        ({"search": "HOPE-987"}, {"detail_id": "HOPE-654"}, {"detail_id": "HOPE-987"}, {}, {}),
        ({"search": "786"}, {"program_registration_id": "456"}, {"program_registration_id": "786"}, {}, {}),
    ],
)
def test_search_db_no_program_filter(
    search_client: Any,
    afghanistan: BusinessArea,
    program: Program,
    filters: Dict,
    individual1_data: Dict,
    individual2_data: Dict,
    household1_data: Dict,
    household2_data: Dict,
) -> None:
    list_url = reverse(
        "api:households:individuals-global-list",
        kwargs={"business_area_slug": afghanistan.slug},
    )
    response_data, individuals = _test_search(
        search_client,
        list_url,
        afghanistan,
        program,
        filters,
        individual1_data,
        individual2_data,
        household1_data,
        household2_data,
    )
    assert len(response_data) == 2
    result_ids = [result["id"] for result in response_data]
    assert str(individuals[1].id) in result_ids
    assert str(individuals[3].id) in result_ids
