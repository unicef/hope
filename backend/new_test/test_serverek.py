import os
from datetime import datetime
from time import sleep

import pytest
from selenium.webdriver.common.by import By


pytestmark = pytest.mark.django_db(transaction=True)

def take_screenshot(driver, node_id: str) -> None:
    sleep(1)
    if not os.path.exists('screenshot'):
        os.makedirs('screenshot')
    file_name = os.path.join('screenshot',
                             f'{node_id}_{datetime.today().strftime("%Y-%m-%d_%H:%M")}.png'.replace("/", "_").replace(
                                 "::", "__"))
    driver.get_screenshot_as_file(file_name)

@pytest.mark.usefixtures("login")
class TestTestowy:

    @pytest.mark.parametrize("bubu", [1, 2, 3])
    def test_user_profile(self, browser, bubu):
        take_screenshot(browser, str(bubu))

    def test_testu(self, browser):
        take_screenshot(browser, "ta sama baza")
