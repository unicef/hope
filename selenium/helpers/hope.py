from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from .server import CustomServer

class HOPE(object):

    def get(self, locator, element_type=By.CSS_SELECTOR):
        return self.browser.find_element(element_type, locator)

    def wait_for(self, locator, element_type=By.CSS_SELECTOR):
        return WebDriverWait(self.browser, 10).until(EC.visibility_of_element_located((element_type, locator)))

    def wait_for_disappear(self, locator, element_type=By.CSS_SELECTOR):
        return WebDriverWait(self.browser, 10).until_not(EC.visibility_of_element_located((element_type, locator)))
