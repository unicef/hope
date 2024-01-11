from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

class Common:
    def __init__(self, driver):
        self.driver = driver
        self._wait = WebDriverWait(self.driver, 10)

    def get(self, locator, element_type=By.CSS_SELECTOR):
        return self.driver.find_element(element_type, locator)

    def get_elements(self, locator, element_type=By.CSS_SELECTOR):
        return self.driver.find_elements(element_type, locator)

    def wait_for(self, locator, element_type=By.CSS_SELECTOR):
        return self._wait.until(EC.visibility_of_element_located((element_type, locator)))

    def wait_for_disappear(self, locator, element_type=By.CSS_SELECTOR):
        return self._wait.until_not(EC.visibility_of_element_located((element_type, locator)))
