from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from e2e.page_object.base_components import BaseComponents


class AdminPanel(BaseComponents):
    login = "id_username"
    password = "id_password"
    permission_text = "content-main"
    login_button = '//*[@id="login-form"]/div[3]/input'
    logged_name = '//*[@class="changelink"]/a'
    button_logout = '//*[@id="user-tools"]/a[3]'
    logged_out = '//*[@id="content"]'
    error_note = '//*[@class="errornote"]'
    unicef_id = '//*[@id="content"]/h2'

    def get_unicef_id(self) -> WebElement:
        return self.wait_for(self.unicef_id, By.XPATH)

    def get_error_login(self) -> WebElement:
        return self.wait_for(self.error_note, By.XPATH)

    def get_logged_out(self) -> WebElement:
        return self.wait_for(self.logged_out, By.XPATH)

    def get_button_logout(self) -> WebElement:
        return self.wait_for(self.button_logout, By.XPATH)

    def get_login(self) -> WebElement:
        return self.wait_for(self.login, By.ID)

    def get_password(self) -> WebElement:
        return self.wait_for(self.password, By.ID)

    def get_permission_text(self) -> WebElement:
        return self.wait_for(self.permission_text, By.ID)

    def get_login_button(self) -> WebElement:
        return self.wait_for(self.login_button, By.XPATH)

    def get_logged_name(self) -> WebElement:
        return self.wait_for(self.logged_name, By.XPATH)
