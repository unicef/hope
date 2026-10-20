from django.contrib.auth.models import Permission
from django.test import Client
from django.urls import reverse
import pytest

from extras.test_utils.factories import (
    BiographicDeduplicationEngineSimilarityPairFactory,
    BiometricDeduplicationEngineSimilarityPairFactory,
    ProgramFactory,
    UserFactory,
)
from hope.models import BiographicDedupeSimilarityPair, BiometricDedupeSimilarityPair, Program, User

pytestmark = pytest.mark.django_db


@pytest.fixture
def program() -> Program:
    return ProgramFactory()


@pytest.fixture
def staff_user() -> User:
    return UserFactory(is_staff=True, is_superuser=False)


@pytest.fixture
def biometric_pairs(program: Program) -> list[BiometricDedupeSimilarityPair]:
    return BiometricDeduplicationEngineSimilarityPairFactory.create_batch(2, program=program)


@pytest.fixture
def biographic_pairs(program: Program) -> list[BiographicDedupeSimilarityPair]:
    return BiographicDeduplicationEngineSimilarityPairFactory.create_batch(2, program=program)


@pytest.fixture
def biometric_client(client: Client, staff_user: User) -> Client:
    staff_user.user_permissions.add(Permission.objects.get(codename="view_biometricdedupesimilaritypair"))
    client.force_login(staff_user)
    return client


@pytest.fixture
def biographic_client(client: Client, staff_user: User) -> Client:
    staff_user.user_permissions.add(Permission.objects.get(codename="view_biographicdedupesimilaritypair"))
    client.force_login(staff_user)
    return client


def test_biometric_pair_changelist_search_by_individual_unicef_id_returns_matching_pair(
    biometric_client: Client,
    biometric_pairs: list[BiometricDedupeSimilarityPair],
) -> None:
    matching_pair = biometric_pairs[0]
    url = reverse("admin:registration_data_biometricdedupesimilaritypair_changelist")

    response = biometric_client.get(url, {"q": matching_pair.individual1.unicef_id})

    assert response.status_code == 200
    assert list(response.context["cl"].result_list) == [matching_pair]


def test_biographic_pair_changelist_search_by_individual_unicef_id_returns_matching_pair(
    biographic_client: Client,
    biographic_pairs: list[BiographicDedupeSimilarityPair],
) -> None:
    matching_pair = biographic_pairs[0]
    url = reverse("admin:registration_data_biographicdedupesimilaritypair_changelist")

    response = biographic_client.get(url, {"q": matching_pair.individual1.unicef_id})

    assert response.status_code == 200
    assert list(response.context["cl"].result_list) == [matching_pair]
