from e2e.page_object.admin_panel.admin_panel import AdminPanel
from extras.test_utils.factories.account import UserFactory
import pytest
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By

from hope.apps.account.models import User

pytestmark = pytest.mark.django_db()


def create_normal_user() -> User:
    return UserFactory.create(
        is_superuser=False,
        is_staff=True,
        username="normal_user",
        password="normal_password",
        email="normal@user.com",
    )


class TestAdminPanel:
    def test_login_superuser(self, browser: Chrome, page_admin_panel: AdminPanel) -> None:
        browser.get(f"{browser.live_server.url}/api/unicorn/")
        page_admin_panel.get_login().send_keys("superuser")
        page_admin_panel.get_password().send_keys("testtest2")
        page_admin_panel.get_login_button().click()
        assert "Permissions" in page_admin_panel.get_permission_text().text

    def test_login_normal_user(self, browser: Chrome, page_admin_panel: AdminPanel) -> None:
        create_normal_user()
        browser.get(f"{browser.live_server.url}/api/unicorn/")
        page_admin_panel.get_login().send_keys("normal_user")
        page_admin_panel.get_password().send_keys("normal_password")
        page_admin_panel.get_login_button().click()
        assert "You don't have permission to view or edit anything." in page_admin_panel.get_permission_text().text

    def test_login_with_valid_username_and_invalid_password(
        self, browser: Chrome, page_admin_panel: AdminPanel
    ) -> None:
        browser.get(f"{browser.live_server.url}/api/unicorn/")
        page_admin_panel.get_login().send_keys("normal_user")
        page_admin_panel.get_password().send_keys("wrong")
        page_admin_panel.get_login_button().click()
        assert (
            "Please enter the correct username and password for a staff account. Note that both fields may be "
            "case-sensitive."
        ) in page_admin_panel.get_error_login().text

    def test_login_with_invalid_username_and_valid_password(
        self, browser: Chrome, page_admin_panel: AdminPanel
    ) -> None:
        browser.get(f"{browser.live_server.url}/api/unicorn/")
        page_admin_panel.get_login().send_keys("wrong")
        page_admin_panel.get_password().send_keys("normal_password")
        page_admin_panel.get_login_button().click()
        assert (
            "Please enter the correct username and password for a staff account. Note that both fields may be "
            "case-sensitive."
        ) in page_admin_panel.get_error_login().text

    def test_login_with_invalid_username_and_invalid_password(
        self, browser: Chrome, page_admin_panel: AdminPanel
    ) -> None:
        browser.get(f"{browser.live_server.url}/api/unicorn/")
        page_admin_panel.get_login().send_keys("wrong")
        page_admin_panel.get_password().send_keys("wrong123123312")
        page_admin_panel.get_login_button().click()
        assert (
            "Please enter the correct username and password for a staff account. Note that both fields may be "
            "case-sensitive."
        ) in page_admin_panel.get_error_login().text

    def test_not_logged_main_page(self, browser: Chrome, page_admin_panel: AdminPanel) -> None:
        browser.get(f"{browser.live_server.url}/")
        assert "Login via Active Directory" in page_admin_panel.wait_for('//*[@id="root"]/div/div', By.XPATH).text

    def test_log_out_via_admin_panel(self, login: Chrome, page_admin_panel: AdminPanel) -> None:
        login.get(f"{login.live_server.url}/api/unicorn/")
        page_admin_panel.get_button_logout().click()
        assert "Logged out" in page_admin_panel.get_logged_out().text
