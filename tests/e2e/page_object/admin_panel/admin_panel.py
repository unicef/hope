from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from e2e.page_object.base_components import BaseComponents


class AdminPanel(BaseComponents):
    login = "id_username"
    password = "id_password"
    # Unfold uses id="main" as the main content wrapper (no id="content-main" on the index page)
    permission_text = "main"
    login_button = '//form[@id="login-form"]//*[@type="submit"]'
    logged_name = '//*[@class="changelink"]/a'
    button_logout = '//*[@id="logout-form"]/button'
    # Unfold's logged-out page uses id="page" with an h1
    logged_out = '//*[@id="page"]//h1'
    # Unfold renders errornote as a <p> ("Please correct...") and the actual message as a <div>;
    # target the <div> to get the specific error text the tests assert against.
    error_note = '//div[contains(@class,"errornote")]'
    unicef_id = '//*[@id="header-inner"]//h1'
    # Selector for the user-nav toggle that reveals the logout dropdown in Unfold
    user_nav_toggle = (
        '//div[contains(@class,"cursor-pointer") '
        'and @*[local-name()="x-on:click" and contains(., "openUserLinks")]]'
    )

    def get_unicef_id(self) -> WebElement:
        return self.wait_for(self.unicef_id, By.XPATH)

    def get_error_login(self) -> WebElement:
        return self.wait_for(self.error_note, By.XPATH)

    def get_logged_out(self) -> WebElement:
        return self.wait_for(self.logged_out, By.XPATH)

    def open_user_dropdown(self) -> None:
        self.wait_for(self.user_nav_toggle, By.XPATH).click()

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
