import contextlib
import logging
import os
import time
from time import sleep
from typing import Callable, Literal, Tuple, Union

from selenium.common import NoSuchElementException
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver import Chrome, Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait

logger = logging.getLogger(__name__)


def text_to_be_exact_in_element(locator: Tuple[str, str], expected: str) -> Callable:
    def _predicate(driver):
        try:
            actual = driver.find_element(*locator).text.strip()
            return actual == expected
        except (StaleElementReferenceException, NoSuchElementException):
            return False

    return _predicate


class StaleSafeElement(WebElement):
    """An element that re-locates itself when its DOM node gets replaced.

    React re-renders and page navigations swap the node out between the moment
    ``wait_for`` returns an element and the moment a test reads it, which raises
    ``StaleElementReferenceException``. Every element operation goes through
    ``_execute``, so retrying there covers ``.text``, ``.click()``, attribute
    reads and nested lookups alike.

    A click that lands on something drawn over the element is retried the same way,
    which is what the fixed sleeps in front of the old call sites were for.
    """

    def __init__(self, element: WebElement, relocate: Callable[[], WebElement], attempts: int = 5) -> None:
        super().__init__(element.parent, element.id)
        self._relocate = relocate
        self._attempts = attempts

    def _execute(self, command: str, params: dict | None = None) -> dict:
        for attempt in range(self._attempts):
            try:
                return super()._execute(command, params)
            except StaleElementReferenceException:
                if attempt == self._attempts - 1:
                    raise
                self._id = self._relocate().id
            except ElementClickInterceptedException:
                # A sticky header or a MUI backdrop that is still fading out covers the
                # element. The click did not land, so centre the element away from the
                # sticky edges and retry once the transition has had time to finish.
                if attempt == self._attempts - 1:
                    raise
                with contextlib.suppress(Exception):
                    self.parent.execute_script("arguments[0].scrollIntoView({block: 'center'});", self)
                sleep(0.2)
        raise StaleElementReferenceException(f"Element stayed stale after {self._attempts} attempts")


class Common:
    DEFAULT_TIMEOUT = 20
    DEFAULT_TIMEOUT_WAITING_PAGE = 10

    def __init__(self, driver: Chrome):
        self.driver = driver
        self.action = ActionChains(self.driver)

    def _wait(self, timeout: int = DEFAULT_TIMEOUT) -> WebDriverWait:
        # driver.get() already blocks until the document has loaded, and the SPA never
        # reloads the document on client-side navigation, so no readyState check here.
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
        raise Exception("No elements found")

    def wait_for(
        self,
        locator: str,
        element_type: str = By.CSS_SELECTOR,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> WebElement:
        """Wait for the element to be visible and return it.

        The element re-locates itself if the node is replaced before it is used,
        so callers can hold on to it across a re-render (see ``StaleSafeElement``).
        """

        def locate() -> WebElement:
            try:
                return self._wait(timeout).until(
                    expected_conditions.visibility_of_element_located((element_type, locator))
                )
            except TimeoutException as e:
                raise NoSuchElementException(f"Element {locator} not visible after {timeout}s") from e

        return StaleSafeElement(locate(), locate)

    def wait_for_header_text(self, locator: str, text: str, timeout: int = DEFAULT_TIMEOUT):
        WebDriverWait(self.driver, timeout).until(
            expected_conditions.text_to_be_present_in_element(
                (By.CSS_SELECTOR, locator),
                text,
            )
        )
        return self.driver.find_element(By.CSS_SELECTOR, locator)

    def wait_for_page_ready(self, timeout: int = DEFAULT_TIMEOUT_WAITING_PAGE):
        WebDriverWait(self.driver, timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )

    def wait_for_disappear(
        self,
        locator: str,
        element_type: str = By.CSS_SELECTOR,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> Union[Literal[False, True], WebElement]:
        return self._wait(timeout).until_not(expected_conditions.visibility_of_element_located((element_type, locator)))

    def wait_for_text_disappear(
        self,
        text: str,
        locator: str,
        element_type: str = By.CSS_SELECTOR,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> Union[Literal[False, True], WebElement]:
        return self._wait(timeout).until_not(
            expected_conditions.text_to_be_present_in_element((element_type, locator), text)
        )

    def wait_for_text(
        self,
        text: str,
        locator: str,
        element_type: str = By.CSS_SELECTOR,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> Union[Literal[False, True], bool]:
        try:
            return self._wait(timeout).until(
                expected_conditions.text_to_be_present_in_element((element_type, locator), text)
            )
        except TimeoutException:
            pass
        raise NoSuchElementException(
            f"Element: {text} not found in {locator}. Displayed text:"
            f" {self.driver.find_element(element_type, locator).text}"
        )

    def wait_for_text_to_be_exact(
        self,
        text: str,
        locator: str,
        element_type: str = By.CSS_SELECTOR,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> bool:
        """
        Wait until element text equals *exactly* ``text``.
        Returns True on success, otherwise raises TimeoutException.
        """
        try:
            WebDriverWait(self.driver, timeout).until(text_to_be_exact_in_element((element_type, locator), text))
            return True  # success!
        except TimeoutException:
            actual = ""
            with contextlib.suppress(Exception):
                actual = self.driver.find_element(element_type, locator).text.strip()
            raise TimeoutException(
                f"Timed out after {timeout}s waiting for "
                f"text '{text}' in element {locator}. "
                f"Last seen text: '{actual}'."
            )

    def wait_for_text_in_any_element(
        self,
        text: str,
        locator: str,
        element_type: str = By.CSS_SELECTOR,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> bool:
        try:
            return self._wait(timeout).until(
                lambda driver: any(text in el.text for el in driver.find_elements(element_type, locator))
            )
        except TimeoutException:
            pass
        raise NoSuchElementException(f"Text '{text}' not found in any element matching {locator}.")

    def wait_for_new_url(self, old_url: str, retry: int = 5) -> str:
        """Wait up to ``retry`` seconds for the URL to change and return the current URL."""
        with contextlib.suppress(TimeoutException):
            WebDriverWait(self.driver, retry, poll_frequency=0.1).until(lambda d: d.current_url != old_url)
        return self.driver.current_url

    def element_clickable(
        self,
        locator: str,
        element_type: str = By.CSS_SELECTOR,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> bool:
        return self._wait(timeout).until(expected_conditions.element_to_be_clickable((element_type, locator)))

    def click(
        self,
        locator: str,
        element_type: str = By.CSS_SELECTOR,
        timeout: int = DEFAULT_TIMEOUT,
        attempts: int = 5,
    ) -> WebElement:
        """Wait for the element to be clickable and click it, re-locating on each attempt.

        Re-locating makes the click resilient to the element going stale between the
        lookup and the click, and to a click that lands on an overlay instead.
        """
        for attempt in range(attempts):
            try:
                element = self._wait(timeout).until(
                    expected_conditions.element_to_be_clickable((element_type, locator))
                )
                element.click()
                return element
            except (StaleElementReferenceException, ElementClickInterceptedException):
                if attempt == attempts - 1:
                    raise
                sleep(0.2)
        raise StaleElementReferenceException(f"Element {locator} stayed stale after {attempts} attempts")

    def scroll_to_and_wait_for(
        self,
        locator: str,
        element_type: str = By.CSS_SELECTOR,
        scroll_by: int = -600,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> WebElement:
        """Scroll the main content and return the element once it is clickable.

        Page objects used to scroll and then sleep a fixed amount, because a button can be
        covered by the sticky header or a still-animating panel even though Selenium
        reports it visible. Waiting for it to be clickable gives the same guarantee, and
        the returned element retries a click that gets intercepted anyway.
        """
        self.scroll(scroll_by)
        element = self.wait_for(locator, element_type, timeout)
        self._wait(timeout).until(expected_conditions.element_to_be_clickable(element))
        return element

    def _find_listbox_item(
        self,
        name: str,
        listbox: str,
        tag_name: str,
        timeout: int,
    ) -> WebElement:
        """Poll the listbox until an item containing ``name`` shows up and return it.

        Options of async listboxes render after the listbox itself, so a single read
        can miss them; polling replaces the fixed sleeps the callers used to need.
        """
        deadline = time.monotonic() + timeout
        labels: list[str] = []
        while True:
            try:
                items = self.wait_for(listbox, timeout=timeout).find_elements("tag name", tag_name)
                labels = [item.text for item in items]
                for item, label in zip(items, labels, strict=True):
                    if name in label:
                        return item
            except StaleElementReferenceException:
                labels = []
            if time.monotonic() >= deadline:
                raise AssertionError(f"Element: {name} is not in the list: {labels}")
            sleep(0.1)

    def select_listbox_element(
        self,
        name: str,
        listbox: str = 'ul[role="listbox"]',
        tag_name: str = "li",
        timeout: int = DEFAULT_TIMEOUT,
    ) -> None:
        item = self._find_listbox_item(name, listbox, tag_name, timeout)
        self._wait().until(expected_conditions.element_to_be_clickable(item))
        item.click()
        self.wait_for_disappear('ul[role="listbox"]')

    def get_listbox_element(
        self,
        name: str,
        listbox: str = 'ul[role="listbox"]',
        tag_name: str = "li",
        timeout: int = DEFAULT_TIMEOUT,
    ) -> WebElement:
        return self._find_listbox_item(name, listbox, tag_name, timeout)

    def check_page_after_click(self, button: WebElement, url_fragment: str) -> None:
        current_page_url = self.driver.current_url
        button.click()
        assert url_fragment in self.wait_for_new_url(current_page_url).split("/")[-1], (
            current_page_url,
            url_fragment,
        )

    def upload_file(
        self,
        upload_file: str,
        xpath: str = "//input[@type='file']",
        timeout: int = DEFAULT_TIMEOUT,
    ) -> None:
        self._wait(timeout).until(expected_conditions.presence_of_element_located((By.XPATH, xpath))).send_keys(
            upload_file
        )

    def select_option_by_name(self, option_name: str) -> None:
        select_option = f'li[data-cy="select-option-{option_name}"]'
        try:
            self.wait_for(select_option).click()
            self.wait_for_disappear(select_option)
        except TimeoutException:
            sleep(1)
            self.wait_for(select_option).click()
            self.wait_for_disappear(select_option)

    def select_multiple_option_by_name(self, *args: [str]) -> None:
        for option_name in args:
            select_option = f'li[data-cy="select-option-{option_name}"]'
            self.wait_for(select_option).click()
        actions = ActionChains(self.driver)
        actions.send_keys(Keys.ESCAPE).perform()
        try:
            self.wait_for_disappear(select_option)
        except TimeoutException:
            sleep(1)
            self.wait_for(select_option).click()
            self.wait_for_disappear(select_option)

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
        self,
        file_path: str,
        file_name: str = "test",
        file_type: str = "png",
        delay_sec: float = 1,
    ) -> None:
        os.makedirs(file_path, exist_ok=True)
        sleep(delay_sec)
        full_filename = os.path.join(f"{file_path}", f"{file_name}.{file_type}")
        self.driver.get_screenshot_as_file(full_filename)

    def scroll(
        self,
        scroll_by: int = 600,
        wait_after_start_scrolling: float = 0,
        execute: int = 1,
    ) -> None:
        for _ in range(execute):
            self.driver.execute_script(
                f"""
                const container = document.querySelector("div[data-cy='main-content']")
                if (container) {{ container.scrollBy(0,{scroll_by}) }}
                """
            )
            if wait_after_start_scrolling:
                sleep(wait_after_start_scrolling)

    def get_value_of_attributes(self, attribute: str = "data-cy") -> None:
        sleep(1)
        ids = self.driver.find_elements(By.XPATH, f"//*[@{attribute}]")
        for ii in ids:
            try:
                logger.info(f"{ii.text}: {ii.get_attribute(attribute)}")
            except TimeoutException:
                logger.info(f"No text: {ii.get_attribute(attribute)}")

    def mouse_on_element(self, element: WebElement) -> None:
        hover = ActionChains(self.driver).move_to_element(element)
        hover.perform()

    def wait_for_element_clickable(self, locator: str) -> bool:
        return self._wait().until(expected_conditions.element_to_be_clickable((By.XPATH, locator)))

    def check_file_exists(self, filepath: str, timeout: int = DEFAULT_TIMEOUT) -> bool:
        start_time = time.time()
        while True:
            if os.path.exists(filepath):
                return True
            if time.time() - start_time > timeout:
                raise TimeoutError(f"File {filepath} not found after {timeout} seconds")
            sleep(0.02)
