from time import sleep
from typing import Literal, Union

from selenium.webdriver import Chrome
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class Common:
    def __init__(self, driver: Chrome):
        self.driver = driver
        self.action = ActionChains(self.driver)
        self._wait = WebDriverWait(self.driver, 60)

    def get(self, locator: str, element_type: str = By.CSS_SELECTOR) -> WebElement:
        return self.driver.find_element(element_type, locator)

    def get_elements(self, locator: str, element_type: str = By.CSS_SELECTOR) -> list[WebElement]:
        return self.driver.find_elements(element_type, locator)

    def wait_for(self, locator: str, element_type: str = By.CSS_SELECTOR) -> WebElement:
        return self._wait.until(EC.visibility_of_element_located((element_type, locator)))

    def wait_for_disappear(
        self, locator: str, element_type: str = By.CSS_SELECTOR
    ) -> Union[Literal[False, True], WebElement]:
        return self._wait.until_not(EC.visibility_of_element_located((element_type, locator)))

    def wait_for_new_url(self, old_url: str, retry: int = 5) -> str:
        for _ in range(retry):
            sleep(1)
            if old_url == self.driver.current_url:
                break
        return self.driver.current_url

    @staticmethod
    def find_in_element(element: WebElement, locator: str, element_type: str = By.CSS_SELECTOR) -> list[WebElement]:
        return element.find_elements(element_type, locator)
