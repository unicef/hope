from collections.abc import Iterator
import contextlib
from typing import Any, Generator
import uuid

import pytest
from seleniumbase import config as sb_config

from extras.test_utils.factories import PartnerFactory
from extras.test_utils.selenium import HopeTestBrowser
from hope.apps.account.permissions import Permissions
from hope.models import BusinessArea, Role, RoleAssignment, User


@pytest.fixture
def user_with_no_permissions(create_super_user: Any) -> User:
    partner = PartnerFactory(name=f"isolated-partner-{uuid.uuid4()}")
    return User.objects.create_user(
        username="noperm_user",
        email="noperm@example.com",
        password="testtest2",
        is_superuser=False,
        is_staff=True,
        partner=partner,
    )


@contextlib.contextmanager
def grant_permission(
    user: User,
    business_area: BusinessArea,
    *permissions: Permissions,
) -> Iterator[None]:
    role = Role.objects.create(
        name=f"tmp-e2e-{uuid.uuid4()}",
        permissions=[p.value for p in permissions],
    )
    assignment = RoleAssignment.objects.create(
        user=user,
        business_area=business_area,
        role=role,
    )
    user.partner.allowed_business_areas.add(business_area)
    try:
        yield
    finally:
        user.partner.allowed_business_areas.remove(business_area)
        assignment.delete()
        role.delete()


@pytest.fixture
def browser(live_server_with_static, request) -> Generator[HopeTestBrowser, None, None]:
    sb = HopeTestBrowser("base_method")
    sb.live_server_url = str(live_server_with_static)
    sb.setUp()
    sb._using_sb_fixture = True
    sb._using_sb_fixture_no_class = True
    sb_config._sb_node[request.node.nodeid] = sb
    yield sb
    sb.tearDown()


@pytest.fixture
def login(browser: HopeTestBrowser) -> HopeTestBrowser:
    browser.login()
    return browser
