from typing import Any, Callable

import pytest
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from extras.test_utils.factories import BusinessAreaFactory, DataCollectingTypeFactory, PayeeTypeFactory, UserFactory
from hope.apps.account.permissions import Permissions
from hope.models import BusinessArea, DataCollectingType, PayeeType, User

pytestmark = pytest.mark.django_db


@pytest.fixture
def afghanistan(db: Any) -> BusinessArea:
    return BusinessAreaFactory(name="Afghanistan", slug="afghanistan")


@pytest.fixture
def ukraine(db: Any) -> BusinessArea:
    return BusinessAreaFactory(name="Ukraine", slug="ukraine")


@pytest.fixture
def user(db: Any) -> User:
    return UserFactory()


@pytest.fixture
def authenticated_client(api_client: Callable, user: User) -> Any:
    return api_client(user)


@pytest.fixture
def household_payee_type(db: Any) -> PayeeType:
    return PayeeTypeFactory(name="Household", gl_code="7700410", weight=30)


@pytest.fixture
def incentive_payee_type(db: Any) -> PayeeType:
    return PayeeTypeFactory(name="Incentive Payee", gl_code="7700430", weight=20)


@pytest.fixture
def inactive_payee_type(db: Any) -> PayeeType:
    return PayeeTypeFactory(name="Organization", gl_code="7700430", weight=10, active=False)


@pytest.fixture
def full_collection_dct(household_payee_type: PayeeType) -> DataCollectingType:
    dct = DataCollectingTypeFactory(code="full_collection", payee_type=household_payee_type)
    household_payee_type.default_data_collecting_type = dct
    household_payee_type.save()
    return dct


@pytest.fixture
def frontline_worker_cp_dct(incentive_payee_type: PayeeType) -> DataCollectingType:
    """Active, not deprecated, not limited to any business area."""
    return DataCollectingTypeFactory(
        code="frontline_worker_cp", type=DataCollectingType.Type.SOCIAL, payee_type=incentive_payee_type
    )


@pytest.fixture
def incentive_payee_type_with_default_limited_to_ukraine(
    incentive_payee_type: PayeeType, frontline_worker_cp_dct: DataCollectingType, ukraine: BusinessArea
) -> PayeeType:
    dct = DataCollectingTypeFactory(
        code="frontline_worker_wash", type=DataCollectingType.Type.SOCIAL, payee_type=incentive_payee_type
    )
    dct.limit_to.add(ukraine)
    incentive_payee_type.default_data_collecting_type = dct
    incentive_payee_type.save()
    return incentive_payee_type


@pytest.fixture
def incentive_payee_type_with_inactive_default(
    incentive_payee_type: PayeeType, frontline_worker_cp_dct: DataCollectingType
) -> PayeeType:
    incentive_payee_type.default_data_collecting_type = DataCollectingTypeFactory(
        code="frontline_worker_sp", type=DataCollectingType.Type.SOCIAL, active=False, payee_type=incentive_payee_type
    )
    incentive_payee_type.save()
    return incentive_payee_type


@pytest.fixture
def incentive_payee_type_limited_to_ukraine(incentive_payee_type: PayeeType, ukraine: BusinessArea) -> PayeeType:
    dct = DataCollectingTypeFactory(
        code="frontline_worker_wash", type=DataCollectingType.Type.SOCIAL, payee_type=incentive_payee_type
    )
    dct.limit_to.add(ukraine)
    incentive_payee_type.default_data_collecting_type = dct
    incentive_payee_type.save()
    return incentive_payee_type


@pytest.fixture
def unlimited_dct(household_payee_type: PayeeType) -> DataCollectingType:
    """Active, not deprecated, not limited to any business area."""
    return DataCollectingType.objects.create(
        label="DCT 1",
        code="dct_1",
        description="Description for DCT 1",
        type=DataCollectingType.Type.STANDARD,
        active=True,
        deprecated=False,
        payee_type=household_payee_type,
    )


@pytest.fixture
def afghanistan_dct(afghanistan: BusinessArea) -> DataCollectingType:
    """Active, not deprecated, limited to Afghanistan."""
    dct = DataCollectingType.objects.create(
        label="DCT 2",
        code="dct_2",
        description="Description for DCT 2",
        type=DataCollectingType.Type.STANDARD,
        active=True,
        deprecated=False,
    )
    dct.limit_to.add(afghanistan)
    return dct


@pytest.fixture
def ukraine_dct(ukraine: BusinessArea) -> DataCollectingType:
    """Active, not deprecated, limited to Ukraine."""
    dct = DataCollectingType.objects.create(
        label="DCT 3",
        code="dct_3",
        description="Description for DCT 3",
        type=DataCollectingType.Type.STANDARD,
        active=True,
        deprecated=False,
    )
    dct.limit_to.add(ukraine)
    return dct


@pytest.fixture
def inactive_dct(db: Any) -> DataCollectingType:
    return DataCollectingType.objects.create(
        label="DCT 4 (Inactive)",
        code="dct_4",
        description="Description for DCT 4",
        type=DataCollectingType.Type.STANDARD,
        active=False,
        deprecated=False,
    )


@pytest.fixture
def deprecated_dct(db: Any) -> DataCollectingType:
    return DataCollectingType.objects.create(
        label="DCT 5 (Deprecated)",
        code="dct_5",
        description="Description for DCT 5",
        type=DataCollectingType.Type.STANDARD,
        active=True,
        deprecated=True,
    )


@pytest.fixture
def unknown_dct(db: Any) -> DataCollectingType:
    return DataCollectingType.objects.create(
        label="DCT 6 (Unknown Code)",
        code="unknown",
        description="Description for DCT 6",
        type=DataCollectingType.Type.STANDARD,
        active=True,
        deprecated=False,
    )


def _choices_url(business_area_slug: str) -> str:
    return reverse(
        "api:core:data-collecting-types-choices",
        kwargs={"business_area_slug": business_area_slug},
    )


def test_choices_returns_unlimited_and_business_area_types_only(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    create_user_role_with_permissions: Callable,
    unlimited_dct: DataCollectingType,
    afghanistan_dct: DataCollectingType,
    ukraine_dct: DataCollectingType,
    inactive_dct: DataCollectingType,
    deprecated_dct: DataCollectingType,
    unknown_dct: DataCollectingType,
) -> None:
    create_user_role_with_permissions(
        user=user,
        permissions=[Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS],
        business_area=afghanistan,
        whole_business_area_access=True,
    )

    response = authenticated_client.get(_choices_url(afghanistan.slug))

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [
        {
            "name": unlimited_dct.label,
            "value": unlimited_dct.code,
            "description": unlimited_dct.description,
            "type": unlimited_dct.type,
            "payee_type": str(unlimited_dct.payee_type_id),
        },
        {
            "name": afghanistan_dct.label,
            "value": afghanistan_dct.code,
            "description": afghanistan_dct.description,
            "type": afghanistan_dct.type,
            "payee_type": None,
        },
    ]


def test_choices_returns_a_different_list_per_business_area(
    authenticated_client: Any,
    user: User,
    ukraine: BusinessArea,
    create_user_role_with_permissions: Callable,
    unlimited_dct: DataCollectingType,
    afghanistan_dct: DataCollectingType,
    ukraine_dct: DataCollectingType,
) -> None:
    create_user_role_with_permissions(
        user=user,
        permissions=[Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS],
        business_area=ukraine,
        whole_business_area_access=True,
    )

    response = authenticated_client.get(_choices_url(ukraine.slug))

    assert response.status_code == status.HTTP_200_OK
    assert [row["value"] for row in response.json()] == [unlimited_dct.code, ukraine_dct.code]


def test_choices_denies_a_user_without_the_permission_in_the_business_area(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    ukraine: BusinessArea,
    create_user_role_with_permissions: Callable,
    unlimited_dct: DataCollectingType,
) -> None:
    create_user_role_with_permissions(
        user=user,
        permissions=[Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS],
        business_area=ukraine,
        whole_business_area_access=True,
    )

    response = authenticated_client.get(_choices_url(afghanistan.slug))

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_choices_denies_a_user_without_any_role(
    authenticated_client: Any,
    afghanistan: BusinessArea,
    unlimited_dct: DataCollectingType,
) -> None:
    response = authenticated_client.get(_choices_url(afghanistan.slug))

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_choices_denies_anonymous_access(afghanistan: BusinessArea, unlimited_dct: DataCollectingType) -> None:
    response = APIClient().get(_choices_url(afghanistan.slug))

    assert response.status_code == status.HTTP_403_FORBIDDEN


def _payee_type_choices_url(business_area_slug: str) -> str:
    return reverse(
        "api:core:payee-types-choices",
        kwargs={"business_area_slug": business_area_slug},
    )


def test_payee_type_choices_returns_active_payee_types_with_gl_code_and_default_dct(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    create_user_role_with_permissions: Callable,
    household_payee_type: PayeeType,
    inactive_payee_type: PayeeType,
    full_collection_dct: DataCollectingType,
) -> None:
    create_user_role_with_permissions(
        user=user,
        permissions=[Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS],
        business_area=afghanistan,
        whole_business_area_access=True,
    )

    response = authenticated_client.get(_payee_type_choices_url(afghanistan.slug))

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [
        {
            "id": str(household_payee_type.id),
            "name": "Household",
            "gl_code": "7700410",
            "default_data_collecting_type": "full_collection",
        },
    ]


def test_payee_type_choices_denies_a_user_without_any_role(
    authenticated_client: Any,
    afghanistan: BusinessArea,
    household_payee_type: PayeeType,
) -> None:
    response = authenticated_client.get(_payee_type_choices_url(afghanistan.slug))

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_payee_type_choices_returns_default_dct_limited_to_the_business_area(
    authenticated_client: Any,
    user: User,
    ukraine: BusinessArea,
    create_user_role_with_permissions: Callable,
    incentive_payee_type_with_default_limited_to_ukraine: PayeeType,
) -> None:
    create_user_role_with_permissions(
        user=user,
        permissions=[Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS],
        business_area=ukraine,
        whole_business_area_access=True,
    )

    response = authenticated_client.get(_payee_type_choices_url(ukraine.slug))

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [
        {
            "id": str(incentive_payee_type_with_default_limited_to_ukraine.id),
            "name": "Incentive Payee",
            "gl_code": "7700430",
            "default_data_collecting_type": "frontline_worker_wash",
        }
    ]


def test_payee_type_choices_hides_default_dct_not_available_in_the_business_area(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    create_user_role_with_permissions: Callable,
    incentive_payee_type_with_default_limited_to_ukraine: PayeeType,
) -> None:
    create_user_role_with_permissions(
        user=user,
        permissions=[Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS],
        business_area=afghanistan,
        whole_business_area_access=True,
    )

    response = authenticated_client.get(_payee_type_choices_url(afghanistan.slug))

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [
        {
            "id": str(incentive_payee_type_with_default_limited_to_ukraine.id),
            "name": "Incentive Payee",
            "gl_code": "7700430",
            "default_data_collecting_type": None,
        }
    ]


def test_payee_type_choices_hides_inactive_default_dct(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    create_user_role_with_permissions: Callable,
    incentive_payee_type_with_inactive_default: PayeeType,
) -> None:
    create_user_role_with_permissions(
        user=user,
        permissions=[Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS],
        business_area=afghanistan,
        whole_business_area_access=True,
    )

    response = authenticated_client.get(_payee_type_choices_url(afghanistan.slug))

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [
        {
            "id": str(incentive_payee_type_with_inactive_default.id),
            "name": "Incentive Payee",
            "gl_code": "7700430",
            "default_data_collecting_type": None,
        }
    ]


def test_payee_type_choices_hides_payee_type_without_usable_dct_in_the_business_area(
    authenticated_client: Any,
    user: User,
    afghanistan: BusinessArea,
    create_user_role_with_permissions: Callable,
    household_payee_type: PayeeType,
    full_collection_dct: DataCollectingType,
    incentive_payee_type_limited_to_ukraine: PayeeType,
) -> None:
    create_user_role_with_permissions(
        user=user,
        permissions=[Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS],
        business_area=afghanistan,
        whole_business_area_access=True,
    )

    response = authenticated_client.get(_payee_type_choices_url(afghanistan.slug))

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [
        {
            "id": str(household_payee_type.id),
            "name": "Household",
            "gl_code": "7700410",
            "default_data_collecting_type": "full_collection",
        },
    ]
