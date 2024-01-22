import pytest
from page_object.programme_management.programme_management import ProgrammeManagement
from page_object.programme_details.programme_details import ProgrammeDetails
from selenium import webdriver
from page_object.admin_panel.admin_panel import AdminPanel


class TestAdminPanel:

    def test_login_superuser(self, browser: webdriver, logout, PageAdminPanel: AdminPanel):
        browser.get("http://localhost:8082/api/unicorn/")
        PageAdminPanel.getLogin().send_keys('root')
        PageAdminPanel.getPassword().send_keys('fKXRA1FRYTA1lKfdg')
        PageAdminPanel.getLoginButton().click()
        assert "Root Rootkowski" in PageAdminPanel.getLoggedName().text
        assert "Permissions" in PageAdminPanel.getPermissionText().text

    def test_login_normal_user(self, browser: webdriver, logout, PageAdminPanel: AdminPanel):
        browser.get("http://localhost:8082/api/unicorn/")
        PageAdminPanel.getLogin().send_keys('cypress-username')
        PageAdminPanel.getPassword().send_keys('cypress-password')
        PageAdminPanel.getLoginButton().click()
        assert "Cypress User" in PageAdminPanel.getLoggedName().text
        assert "You don't have permission to view or edit anything." in PageAdminPanel.getPermissionText().text

    @pytest.mark.skip(reason="ToDo")
    def test_login_with_valid_username_and_invalid_password(self,
                                                            pageProgrammeManagement: ProgrammeManagement,
                                                            pageProgrammeDetails: ProgrammeDetails):
        pass

    @pytest.mark.skip(reason="ToDo")
    def test_login_with_invalid_username_and_valid_password(self,
                                                            pageProgrammeManagement: ProgrammeManagement,
                                                            pageProgrammeDetails: ProgrammeDetails):
        pass

    @pytest.mark.skip(reason="ToDo")
    def test_login_with_invalid_username_and_invalid_password(self,
                                                              pageProgrammeManagement: ProgrammeManagement,
                                                              pageProgrammeDetails: ProgrammeDetails):
        pass

    @pytest.mark.skip(reason="ToDo")
    def test_not_logged_main_page(self,
                                  pageProgrammeManagement: ProgrammeManagement,
                                  pageProgrammeDetails: ProgrammeDetails):
        pass

    @pytest.mark.skip(reason="ToDo")
    def test_log_out_via_admin_panel(self,
                                     pageProgrammeManagement: ProgrammeManagement,
                                     pageProgrammeDetails: ProgrammeDetails):
        pass
