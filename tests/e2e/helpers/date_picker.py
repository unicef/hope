import re
import sys

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement

# MUI X v9 dropped the legacy single-<input> date field (it no longer accepts
# `enableAccessibleFieldDOMStructure={false}`). The visible field is now a set of
# contenteditable section spans (Year/Month/Day) inside `.MuiPickersSectionList-root`;
# the element callers locate by name/data-cy is a hidden, non-typeable <input> that
# only carries the value for form submission. To enter a date we must focus the
# section list and type the digits — the field fills sections left-to-right and
# auto-advances. Our pickers use format="yyyy-MM-dd", so the digits of a yyyy-MM-dd
# value are already in the right order.

_SECTION_LIST_CLASS = "MuiPickersSectionList-root"


def _resolve_section_list(field_element: WebElement) -> WebElement:
    """Find the editable section list for a date field, given any element of it.

    Works whether `field_element` is the hidden <input> (look up to the input base,
    then down) or a wrapper element that contains the field (look down).
    """
    own = field_element.find_elements(By.XPATH, f"descendant-or-self::*[contains(@class, '{_SECTION_LIST_CLASS}')]")
    if own:
        return own[0]
    return field_element.find_element(
        By.XPATH,
        f"./ancestor::*[contains(@class, 'MuiPickersInputBase-root')][1]//*[contains(@class, '{_SECTION_LIST_CLASS}')]",
    )


def fill_mui_date(driver, field_element: WebElement, value: str) -> None:
    """Enter a yyyy-MM-dd date into a MUI X v9 section-based date field.

    `field_element` is any element of the field (typically the hidden input that
    page objects already locate). Separators in `value` are ignored; only the
    digits are typed.
    """
    section_list = _resolve_section_list(field_element)
    section_list.click()
    digits = re.sub(r"\D", "", value)
    select_all = Keys.COMMAND if sys.platform == "darwin" else Keys.CONTROL
    actions = ActionChains(driver)
    actions.key_down(select_all).send_keys("a").key_up(select_all)
    actions.send_keys(Keys.DELETE)
    actions.send_keys(digits)
    actions.perform()
