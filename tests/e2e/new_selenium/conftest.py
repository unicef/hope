from typing import Generator

import pytest
from seleniumbase import config as sb_config

from extras.test_utils.selenium import HopeTestBrowser


@pytest.fixture
def browser(live_server_with_static, request) -> Generator[HopeTestBrowser, None, None]:
    sb = HopeTestBrowser("base_method")
    sb.live_server_url = str(live_server_with_static)
    sb.setUp()
    sb._needs_tearDown = True
    sb._using_sb_fixture = True
    sb._using_sb_fixture_no_class = True
    sb_config._sb_node[request.node.nodeid] = sb
    yield sb
    if sb._needs_tearDown:
        sb.tearDown()
        sb._needs_tearDown = False


@pytest.fixture
def login(browser: HopeTestBrowser) -> HopeTestBrowser:
    browser.login()
    return browser


@pytest.fixture(autouse=True)
def test_failed_check():
    """Override parent's test_failed_check which expects a raw Chrome driver.

    HopeTestBrowser handles teardown screenshots via save_teardown_screenshot().
    """
    return
