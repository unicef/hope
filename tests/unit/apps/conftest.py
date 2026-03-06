from typing import Any

from django.conf import settings
import pytest


@pytest.fixture(autouse=True)
def create_unicef_partner(db: Any) -> None:
    from hope.models import Partner

    unicef, _ = Partner.objects.get_or_create(name="UNICEF")
    return Partner.objects.get_or_create(name=settings.UNICEF_HQ_PARTNER, parent=unicef)


@pytest.fixture(scope="class", autouse=True)
def create_unicef_partner_session(django_db_setup: Any, django_db_blocker: Any) -> None:
    with django_db_blocker.unblock():
        from hope.models import Partner

        unicef, _ = Partner.objects.get_or_create(name="UNICEF")
        Partner.objects.get_or_create(name=settings.UNICEF_HQ_PARTNER, parent=unicef)


@pytest.fixture(autouse=True)
def create_role_with_all_permissions(db: Any) -> None:
    from hope.models import Role

    return Role.objects.get_or_create(name="Role with all permissions")


@pytest.fixture(scope="class", autouse=True)
def create_role_with_all_permissions_session(django_db_setup: Any, django_db_blocker: Any) -> None:
    with django_db_blocker.unblock():
        from hope.models import Role

        Role.objects.get_or_create(name="Role with all permissions")
