from django.urls import reverse
import pytest

from extras.test_utils.factories import CountryFactory, PartnerFactory, UserFactory
from hope.apps.core.languages import LANGUAGES, Languages

# === Fixtures ===


@pytest.fixture
def user():
    partner = PartnerFactory(name="unittest")
    return UserFactory(partner=partner, first_name="Test", last_name="User")


@pytest.fixture
def authenticated_client(api_client, user):
    return api_client(user)


@pytest.fixture
def countries():
    return [
        CountryFactory(name="Afghanistan", short_name="Afghanistan", iso_code2="AF", iso_code3="AFG", iso_num="0004"),
        CountryFactory(name="Poland", short_name="Poland", iso_code2="PL", iso_code3="POL", iso_num="0616"),
    ]


# === Tests ===


@pytest.mark.django_db
def test_choices_payment_verification_plan_sampling_returns_sampling_options(authenticated_client):
    response = authenticated_client.get(reverse("api:choices-payment-verification-plan-sampling"))

    assert response.status_code == 200
    assert response.data == [
        {"name": "Full list", "value": "FULL_LIST"},
        {"name": "Random sampling", "value": "RANDOM"},
    ]


@pytest.mark.django_db
def test_choices_payment_verification_summary_status_returns_status_options(authenticated_client):
    response = authenticated_client.get(reverse("api:choices-payment-verification-summary-status"))

    assert response.status_code == 200
    assert response.data == [
        {"name": "Active", "value": "ACTIVE"},
        {"name": "Finished", "value": "FINISHED"},
        {"name": "Pending", "value": "PENDING"},
    ]


@pytest.mark.django_db
def test_choices_languages_returns_all_languages_when_no_filter(authenticated_client):
    response = authenticated_client.get(reverse("api:choices-languages"))

    assert response.status_code == 200
    assert len(response.data) == len(LANGUAGES)
    expected_data = sorted(
        [{"name": lang.english, "value": lang.code} for lang in LANGUAGES],
        key=lambda x: x["name"].lower(),
    )
    assert sorted(response.data, key=lambda x: x["name"].lower()) == expected_data


@pytest.mark.django_db
def test_choices_languages_filters_by_code_en(authenticated_client):
    response = authenticated_client.get(reverse("api:choices-languages"), {"code": "en"})

    assert response.status_code == 200
    filtered_langs = Languages.filter_by_code("en")
    expected_data = sorted(
        [{"name": lang.english, "value": lang.code} for lang in filtered_langs],
        key=lambda x: x["name"].lower(),
    )
    assert len(response.data) == len(expected_data)
    assert sorted(response.data, key=lambda x: x["name"].lower()) == expected_data
    assert any(lang["value"] == "en-us" for lang in response.data)


@pytest.mark.django_db
def test_choices_languages_filters_by_code_pols(authenticated_client):
    response = authenticated_client.get(reverse("api:choices-languages"), {"code": "Pols"})

    assert response.status_code == 200
    assert len(response.data) == 1
    filtered_langs = Languages.filter_by_code("Pols")
    expected_data = sorted(
        [{"name": lang.english, "value": lang.code} for lang in filtered_langs],
        key=lambda x: x["name"].lower(),
    )
    assert sorted(response.data, key=lambda x: x["name"].lower()) == expected_data
    assert any(lang["value"] == "pl-pl" for lang in response.data)


@pytest.mark.django_db
def test_choices_languages_returns_empty_list_for_nonexistent_code(authenticated_client):
    response = authenticated_client.get(reverse("api:choices-languages"), {"code": "xyzabc"})

    assert response.status_code == 200
    assert len(response.data) == 0


@pytest.mark.django_db
def test_choices_countries_returns_available_countries(authenticated_client, countries):
    response = authenticated_client.get(reverse("api:choices-countries"))

    assert response.status_code == 200
    assert len(response.data) == 2
    assert response.data[0] == {"name": "Afghanistan", "value": "AFG"}
