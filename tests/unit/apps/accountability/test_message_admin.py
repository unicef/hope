from django.urls import reverse
import pytest

from extras.test_utils.factories import CommunicationMessageFactory, HouseholdFactory, UserFactory

pytestmark = pytest.mark.django_db


@pytest.fixture
def admin_user():
    return UserFactory(
        is_staff=True,
        is_superuser=True,
    )


@pytest.fixture
def admin_client(client, admin_user):
    client.force_login(admin_user, backend="django.contrib.auth.backends.ModelBackend")
    return client


@pytest.fixture
def message():
    return CommunicationMessageFactory()


@pytest.fixture
def recipient_household(message):
    household = HouseholdFactory(create_role=False)
    message.households.add(household)
    return household


@pytest.fixture
def unrelated_household():
    return HouseholdFactory(create_role=False)


def test_recipient_households_button_shows_only_recipients(
    admin_client, message, recipient_household, unrelated_household
) -> None:
    url = reverse("admin:accountability_message_recipient_households", args=[message.pk])
    response = admin_client.get(url, follow=True)

    assert response.status_code == 200
    content = response.content.decode()
    assert str(recipient_household.unicef_id) in content
    assert str(unrelated_household.unicef_id) not in content
