import os
from time import sleep
from typing import Literal, Union

from selenium.webdriver import Chrome
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class Common:
    DEFAULT_TIMEOUT = 60

    def __init__(self, driver: Chrome):
        self.driver = driver
        self.action = ActionChains(self.driver)

    def _wait(self, timeout: int = DEFAULT_TIMEOUT) -> WebDriverWait:
        return WebDriverWait(self.driver, timeout)

    def get(self, locator: str, element_type: str = By.CSS_SELECTOR) -> WebElement:
        return self.driver.find_element(element_type, locator)

    def get_elements(self, locator: str, element_type: str = By.CSS_SELECTOR) -> list[WebElement]:
        return self.driver.find_elements(element_type, locator)

    def wait_for(self, locator: str, element_type: str = By.CSS_SELECTOR, timeout: int = DEFAULT_TIMEOUT) -> WebElement:
        return self._wait(timeout).until(EC.visibility_of_element_located((element_type, locator)))

    def wait_for_disappear(
        self, locator: str, element_type: str = By.CSS_SELECTOR, timeout: int = DEFAULT_TIMEOUT
    ) -> Union[Literal[False, True], WebElement]:
        return self._wait(timeout).until_not(EC.visibility_of_element_located((element_type, locator)))

    def wait_for_new_url(self, old_url: str, retry: int = 5) -> str:
        for _ in range(retry):
            sleep(1)
            if old_url == self.driver.current_url:
                break
        return self.driver.current_url

    def select_listbox_element(
        self, name: str, listbox: str = 'ul[role="listbox"]', tag_name: str = "li"
    ) -> WebElement:
        select_element = self.wait_for(listbox)
        items = select_element.find_elements("tag name", tag_name)
        for item in items:
            if name in item.text:
                return item
        return select_element

    def check_page_after_click(self, button: WebElement, url_fragment: str) -> None:
        programme_creation_url = self.driver.current_url
        button.click()
        assert url_fragment in self.wait_for_new_url(programme_creation_url).split("/")[-1]

    @staticmethod
    def choose_option(list_options: list, name: str) -> bool:
        for option in list_options:
            if name in option.text:
                option.click()
                return True
        return False

    @staticmethod
    def find_in_element(element: WebElement, locator: str, element_type: str = By.CSS_SELECTOR) -> list[WebElement]:
        return element.find_elements(element_type, locator)

    def screenshot(
        self, file_name: str = "test", file_type: str = "png", file_path: str = "screenshot", delay_sec: int = 1
    ) -> None:
        sleep(delay_sec)
        self.driver.get_screenshot_as_file(os.path.join(f"{file_path}", f"{file_name}.{file_type}"))
