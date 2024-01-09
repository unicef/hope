from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from .live_server import CustomLiveServer

class HOPE(CustomLiveServer):

    def get(self, element_type=By.ID, locator=""):
        return self.browser.find_element(element_type, locator)

    def wait_for(self, element_type=By.ID, locator=""):
        return WebDriverWait(self.browser, 10).until(EC.visibility_of_element_located((element_type, locator)))
