from selenium.webdriver import Chrome
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By


def printing(
    what: str,
    web_driver: WebDriver,
    label: str = "data-cy",
    page_object_str: str = "self",
) -> None:
    """
    :param web_driver: Selenium WebDriver
    :param what: What type of return will occur:
                Mapping: Mapping every label which you choose
                Methods: Create methods for Page Object Pattern
                Text: Get texts from elements
                Assert: Create asserts for elements by text
    :param label:
        Label of searching elements e.g. data-cy
    :param page_object_str:
        Name page object using during tests
    :return: None
    """
    ids = web_driver.find_elements(By.XPATH, f"//*[@{label}]")
    for ii in ids:
        data_cy_attribute = ii.get_attribute(label)
        var_name = [i.capitalize() for i in data_cy_attribute.lower().replace(".", " ").replace("-", " ").split(" ")]
        "get" + "".join(var_name)
        var_name[0] = var_name[0].lower()
        var_name = "".join(var_name)  # type: ignore
        if what == "Mapping":
            pass
        if what == "Methods":
            pass
        if what == "Text":
            pass
        if what == "Assert":
            pass
        if what == "Input":
            pass


if __name__ == "__main__":
    default_url = "http://localhost:3000"
    url = input(f"Url of page (default is {default_url}):")
    if not url:
        url = default_url

    driver = Chrome()

    driver.get(url)
    label = input("Choose the label (default it data-cy):")
    if not label:
        label = "data-cy"

    exit_loop = ""
    while exit_loop != "exit":
        exit_loop = input("Open the page and press Enter or write exit")
        printing("Mapping", driver)
        printing("Methods", driver)
        printing("Assert", driver)
