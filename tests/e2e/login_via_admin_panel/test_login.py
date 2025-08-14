import pytest
from e2e.page_object.admin_panel.admin_panel import AdminPanel
from selenium.webdriver import Chrome
from extras.test_utils.factories.account import UserFactory
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
    def test_login_superuser(self, browser: Chrome, pageAdminPanel: AdminPanel) -> None:
        browser.get(f"{browser.live_server.url}/api/unicorn/")
        pageAdminPanel.getLogin().send_keys("superuser")
        pageAdminPanel.getPassword().send_keys("testtest2")
        pageAdminPanel.getLoginButton().click()
        assert "Permissions" in pageAdminPanel.getPermissionText().text

    def test_login_normal_user(self, browser: Chrome, pageAdminPanel: AdminPanel) -> None:
        create_normal_user()
        browser.get(f"{browser.live_server.url}/api/unicorn/")
        pageAdminPanel.getLogin().send_keys("normal_user")
        pageAdminPanel.getPassword().send_keys("normal_password")
        pageAdminPanel.getLoginButton().click()
        assert "You don't have permission to view or edit anything." in pageAdminPanel.getPermissionText().text

    def test_login_with_valid_username_and_invalid_password(self, browser: Chrome, pageAdminPanel: AdminPanel) -> None:
        browser.get(f"{browser.live_server.url}/api/unicorn/")
        pageAdminPanel.getLogin().send_keys("normal_user")
        pageAdminPanel.getPassword().send_keys("wrong")
        pageAdminPanel.getLoginButton().click()
        assert (
            "Please enter the correct username and password for a staff account. Note that both fields may be "
            "case-sensitive."
        ) in pageAdminPanel.getErrorLogin().text

    def test_login_with_invalid_username_and_valid_password(self, browser: Chrome, pageAdminPanel: AdminPanel) -> None:
        browser.get(f"{browser.live_server.url}/api/unicorn/")
        pageAdminPanel.getLogin().send_keys("wrong")
        pageAdminPanel.getPassword().send_keys("normal_password")
        pageAdminPanel.getLoginButton().click()
        assert (
            "Please enter the correct username and password for a staff account. Note that both fields may be "
            "case-sensitive."
        ) in pageAdminPanel.getErrorLogin().text

    def test_login_with_invalid_username_and_invalid_password(
        self, browser: Chrome, pageAdminPanel: AdminPanel
    ) -> None:
        browser.get(f"{browser.live_server.url}/api/unicorn/")
        pageAdminPanel.getLogin().send_keys("wrong")
        pageAdminPanel.getPassword().send_keys("wrong123123312")
        pageAdminPanel.getLoginButton().click()
        assert (
            "Please enter the correct username and password for a staff account. Note that both fields may be "
            "case-sensitive."
        ) in pageAdminPanel.getErrorLogin().text

    def test_not_logged_main_page(self, browser: Chrome, pageAdminPanel: AdminPanel) -> None:
        browser.get(f"{browser.live_server.url}/")
        assert "Login via Active Directory" in pageAdminPanel.wait_for('//*[@id="root"]/div/div', By.XPATH).text

    def test_log_out_via_admin_panel(self, login: Chrome, pageAdminPanel: AdminPanel) -> None:
        login.get(f"{login.live_server.url}/api/unicorn/")
        pageAdminPanel.getButtonLogout().click()
        assert "Logged out" in pageAdminPanel.getLoggedOut().text
