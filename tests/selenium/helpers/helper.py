import os
import time
from time import sleep
from typing import Literal, Union

from selenium.common import NoSuchElementException
from selenium.webdriver import Chrome, Keys
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

    @staticmethod
    def _wait_using_element(element: WebElement, timeout: int = DEFAULT_TIMEOUT) -> WebDriverWait:
        # find and wait only in other element area (instead of whole driver)
        return WebDriverWait(element, timeout)

    def get(self, locator: str, element_type: str = By.CSS_SELECTOR) -> WebElement:
        return self.driver.find_element(element_type, locator)

    def get_elements(self, locator: str, element_type: str = By.CSS_SELECTOR, attempts: int = 1) -> list[WebElement]:
        for _ in range(attempts):
            try:
                elements = self.driver.find_elements(element_type, locator)
            except (ValueError, IndexError):
                sleep(1)
            else:
                return elements
        else:
            raise Exception("No elements found")

    def wait_for(self, locator: str, element_type: str = By.CSS_SELECTOR, timeout: int = DEFAULT_TIMEOUT) -> WebElement:
        from selenium.common.exceptions import TimeoutException

        try:
            return self._wait(timeout).until(EC.visibility_of_element_located((element_type, locator)))
        except TimeoutException:
            pass
        raise NoSuchElementException(f"Element: {locator} not found")

    def wait_for_disappear(
        self, locator: str, element_type: str = By.CSS_SELECTOR, timeout: int = DEFAULT_TIMEOUT
    ) -> Union[Literal[False, True], WebElement]:
        return self._wait(timeout).until_not(EC.visibility_of_element_located((element_type, locator)))

    def wait_for_text_disappear(
        self, text: str, locator: str, element_type: str = By.CSS_SELECTOR, timeout: int = DEFAULT_TIMEOUT
    ) -> Union[Literal[False, True], WebElement]:
        return self._wait(timeout).until_not(EC.text_to_be_present_in_element((element_type, locator), text))

    def wait_for_text(
        self, text: str, locator: str, element_type: str = By.CSS_SELECTOR, timeout: int = DEFAULT_TIMEOUT
    ) -> Union[Literal[False, True], bool]:
        return self._wait(timeout).until(EC.text_to_be_present_in_element((element_type, locator), text))

    def wait_for_new_url(self, old_url: str, retry: int = 5) -> str:
        for _ in range(retry):
            sleep(1)
            if old_url == self.driver.current_url:
                break
        return self.driver.current_url

    def element_clickable(
        self, locator: str, element_type: str = By.CSS_SELECTOR, timeout: int = DEFAULT_TIMEOUT
    ) -> bool:
        return self._wait(timeout).until(EC.element_to_be_clickable((element_type, locator)))

    def select_listbox_element(
        self,
        name: str,
        listbox: str = 'ul[role="listbox"]',
        tag_name: str = "li",
        delay_before: int = 2,
        delay_between_checks: float = 0.5,
    ) -> None:
        sleep(delay_before)
        select_element = self.wait_for(listbox)
        items = select_element.find_elements("tag name", tag_name)
        for item in items:
            sleep(delay_between_checks)
            if name in item.text:
                self._wait().until(EC.element_to_be_clickable((By.XPATH, f"//*[contains(text(), '{name}')]")))
                item.click()
                self.wait_for_disappear('ul[role="listbox"]')
                break
        else:
            raise AssertionError(f"Element: {name} is not in the list: {[item.text for item in items]}")

    def get_listbox_element(
        self,
        name: str,
        listbox: str = 'ul[role="listbox"]',
        tag_name: str = "li",
        delay_before: int = 2,
        delay_between_checks: float = 0.5,
    ) -> WebElement:
        sleep(delay_before)
        select_element = self.wait_for(listbox)
        items = select_element.find_elements("tag name", tag_name)
        for item in items:
            sleep(delay_between_checks)
            if name in item.text:
                return item
        else:
            raise AssertionError(f"Element: {name} is not in the list: {[item.text for item in items]}")

    def check_page_after_click(self, button: WebElement, url_fragment: str) -> None:
        programme_creation_url = self.driver.current_url
        button.click()
        assert url_fragment in self.wait_for_new_url(programme_creation_url).split("/")[-1]

    def upload_file(
        self, upload_file: str, xpath: str = "//input[@type='file']", timeout: int = DEFAULT_TIMEOUT
    ) -> None:
        from time import sleep

        sleep(5)
        self._wait(timeout).until(EC.presence_of_element_located((By.XPATH, xpath))).send_keys(upload_file)
        sleep(2)

    def select_option_by_name(self, optionName: str) -> None:
        selectOption = f'li[data-cy="select-option-{optionName}"]'
        try:
            self.wait_for(selectOption).click()
            self.wait_for_disappear(selectOption)
        except BaseException:
            sleep(1)
            self.wait_for(selectOption).click()
            self.wait_for_disappear(selectOption)

    def select_multiple_option_by_name(self, *optionNames: [str]) -> None:
        for optionName in optionNames:
            selectOption = f'li[data-cy="select-option-{optionName}"]'
            self.wait_for(selectOption).click()
        actions = ActionChains(self.driver)
        actions.send_keys(Keys.ESCAPE).perform()  # type: ignore
        try:
            self.wait_for_disappear(selectOption)
        except BaseException:
            sleep(1)
            self.wait_for(selectOption).click()
            self.wait_for_disappear(selectOption)

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
        self, file_name: str = "test", file_type: str = "png", file_path: str = "screenshot", delay_sec: float = 1
    ) -> None:
        sleep(delay_sec)
        self.driver.get_screenshot_as_file(os.path.join(f"{file_path}", f"{file_name}.{file_type}"))

    def get_value_of_attributes(self, attribute: str = "data-cy") -> None:
        sleep(1)
        ids = self.driver.find_elements(By.XPATH, f"//*[@{attribute}]")
        for ii in ids:
            try:
                print(f"{ii.text}: {ii.get_attribute(attribute)}")  # type: ignore
            except BaseException:
                print(f"No text: {ii.get_attribute(attribute)}")  # type: ignore

    def mouse_on_element(self, element: WebElement) -> None:
        hover = ActionChains(self.driver).move_to_element(element)  # type: ignore
        hover.perform()

    def wait_for_element_clickable(self, locator: str) -> bool:
        return self._wait().until(EC.element_to_be_clickable((By.XPATH, locator)))

    def check_file_exists(self, filepath: str, timeout: int = DEFAULT_TIMEOUT) -> bool:
        start_time = time.time()
        while True:
            if os.path.exists(filepath):
                return True
            elif time.time() - start_time > timeout:
                raise TimeoutError(f"File {filepath} not found after {timeout} seconds")
            sleep(0.02)
