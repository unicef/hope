from django.conf import settings
from django.core.cache import cache
import pytest
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from e2e.page_object.error_page.access_denied import AccessDenied
from extras.test_utils.factories import UserFactory
from hope.models import User

pytestmark = pytest.mark.django_db()


@pytest.fixture
def restricted_user() -> User:
    user = UserFactory(
        username="restricted",
        email="restricted@example.com",
        first_name="Restricted",
        last_name="User",
        is_staff=True,
        is_superuser=False,
    )
    user.set_password("testtest2")
    user.save()
    return user


@pytest.fixture
def login_as_restricted(browser: Chrome, restricted_user: User) -> Chrome:
    browser.get(f"{browser.live_server.url}/api/{settings.ADMIN_PANEL_URL}/")
    browser.execute_script(
        """
    window.indexedDB.databases().then(dbs => dbs.forEach(db => indexedDB.deleteDatabase(db.name)));
    window.localStorage.clear();
    window.sessionStorage.clear();
    """
    )
    login_button = '#login-form input[type="submit"]'
    WebDriverWait(browser, 10).until(expected_conditions.visibility_of_element_located((By.CSS_SELECTOR, login_button)))
    browser.find_element(By.ID, "id_username").send_keys("restricted")
    browser.find_element(By.ID, "id_password").send_keys("testtest2")
    browser.find_element(By.CSS_SELECTOR, login_button).click()
    WebDriverWait(browser, 10).until(expected_conditions.invisibility_of_element_located((By.ID, "login-form")))
    cache.clear()
    return browser


@pytest.mark.usefixtures("login_as_restricted")
def test_access_denied_for_user_without_business_area(page_access_denied: AccessDenied) -> None:
    page_access_denied.navigate_to_home()
    page_access_denied.wait_for_text("Access Denied", page_access_denied.access_denied_title)
    assert "REFRESH PAGE" in page_access_denied.get_button_refresh_page().text
    assert "GO BACK" in page_access_denied.get_button_go_back().text
