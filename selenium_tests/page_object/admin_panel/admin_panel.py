from page_object.base_components import BaseComponents
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement


class AdminPanel(BaseComponents):
    login = "id_username"
    password = "id_password"
    permissionText = "content-main"
    loginButton = '//*[@id="login-form"]/div[3]/input'
    loggedName = '//*[@class="changelink"]/a'

    def getLogin(self) -> WebElement:
        return self.wait_for(self.login, By.ID)

    def getPassword(self) -> WebElement:
        return self.wait_for(self.password, By.ID)

    def getPermissionText(self) -> WebElement:
        return self.wait_for(self.permissionText, By.ID)

    def getLoginButton(self):
        return self.wait_for(self.loginButton, By.XPATH)

    def getLoggedName(self):
        return self.wait_for(self.loggedName, By.XPATH)