from live_server import HopeLiveServer
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class HOPE(HopeLiveServer):
    def get(self, element_type: str = By.ID, locator: str = "") -> WebElement:
        return self.browser.find_element(element_type, locator)

    def wait_for(self, element_type: str = By.ID, locator: str = "") -> WebElement:
        return WebDriverWait(self.browser, 10).until(EC.visibility_of_element_located((element_type, locator)))
