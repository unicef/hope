from selenium.page_object.base_components import BaseComponents
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement


class AdminPanel(BaseComponents):
    login = "id_username"
    password = "id_password"
    permissionText = "content-main"
    loginButton = '//*[@id="login-form"]/div[3]/input'
    loggedName = '//*[@class="changelink"]/a'
    buttonLogout = '//*[@id="user-tools"]/a[3]'
    loggedOut = '//*[@id="content"]'
    errorNote = '//*[@class="errornote"]'
    unicefID = '//*[@id="content"]/h2'

    def getUnicefID(self) -> WebElement:
        return self.wait_for(self.unicefID, By.XPATH)

    def getErrorLogin(self) -> WebElement:
        return self.wait_for(self.errorNote, By.XPATH)

    def getLoggedOut(self) -> WebElement:
        return self.wait_for(self.loggedOut, By.XPATH)

    def getButtonLogout(self) -> WebElement:
        return self.wait_for(self.buttonLogout, By.XPATH)

    def getLogin(self) -> WebElement:
        return self.wait_for(self.login, By.ID)

    def getPassword(self) -> WebElement:
        return self.wait_for(self.password, By.ID)

    def getPermissionText(self) -> WebElement:
        return self.wait_for(self.permissionText, By.ID)

    def getLoginButton(self) -> WebElement:
        return self.wait_for(self.loginButton, By.XPATH)

    def getLoggedName(self) -> WebElement:
        return self.wait_for(self.loggedName, By.XPATH)
