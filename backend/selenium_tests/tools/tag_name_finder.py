from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By

url = input("Url of page (default is localhost:3000/):")
if not url:
    url = "http://localhost:3000/"

driver = Chrome()

driver.get(url)
label = input("Choose the label (default it data-cy):")
if not label:
    label = "data-cy"
input("Open the page and press Enter")
ids = driver.find_elements(By.XPATH, f"//*[@{label}]")


def printing(what: str) -> None:
    for ii in ids:
        data_cy_attribute = ii.get_attribute("data-cy")  # type: ignore
        var_name = [i.capitalize() for i in data_cy_attribute.lower().replace("-", " ").split(" ")]
        method_name = "get" + "".join(var_name)
        var_name[0] = var_name[0].lower()
        var_name = "".join(var_name)  # type: ignore
        if what == "Labels":
            print(f"{var_name} = '{ii.tag_name}[data-cy=\"{data_cy_attribute}\"]'")
        if what == "Methods":
            print(f"def {method_name}(self) -> WebElement: \n\treturn self.wait_for(self.{var_name})\n")


printing("Labels")
print("\n")
printing("Methods")
