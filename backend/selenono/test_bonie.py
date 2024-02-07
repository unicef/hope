import os
from datetime import datetime
from time import sleep
import requests
from selenium.webdriver.support.ui import WebDriverWait

import pytest
from django.core.management import call_command
from hct_mis_api.apps.account.models import Partner, Role, User, UserRole
from hct_mis_api.apps.account.fixtures import UserFactory

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from hct_mis_api.apps.core.models import BusinessArea
import os
from selenium.webdriver.common.by import By

from django.test import TestCase


def create_session(username, password):
    if (not pytest.SESSION_ID) and (not pytest.CSRF):
        pytest.session.get(f"http://backend:8000")
        print(pytest.session.cookies.get_dict())
        pytest.CSRF = pytest.session.cookies.get_dict()["csrftoken"]
        headers = {
            'X-CSRFToken': pytest.CSRF,
            'Cookie': f'csrftoken={pytest.CSRF}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        data = {"username": username,
                "password": password}
        pytest.session.post(f"{pytest.path}/api/unicorn/login/", data=data, headers=headers)
        try:
            pytest.SESSION_ID = pytest.session.cookies.get_dict()["sessionid"]
        except:
            raise Exception(f"Login failed! \tlogin: {username} \tpass: {password}")
    return pytest.session


def take_screenshot(driver: webdriver, node_id: str) -> None:
    sleep(1)
    if not os.path.exists('screenshot'):
        os.makedirs('screenshot')
    file_name = os.path.join('screenshot',
                             f'{node_id}_{datetime.today().strftime("%Y-%m-%d_%H:%M")}.png'.replace("/", "_").replace(
                                 "::", "__"))
    driver.get_screenshot_as_file(file_name)


from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.remote.webelement import WebElement



class TestHomepageTests:
    # databases = ["default", "registration_datahub"]


    @pytest.mark.django_db
    def test_bubu(self, live_server):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        # chrome_options.add_argument("--disable-dev-shm-usage")
        self.browser = webdriver.Chrome(options=chrome_options)
        self.browser.implicitly_wait(2)
        def wait_for(locator: str, element_type: str = By.CSS_SELECTOR) -> WebElement:
            return WebDriverWait(self.browser, 10).until(EC.visibility_of_element_located((element_type, locator)))
        # user = UserFactory.create(is_superuser=True, is_staff=True, username="testtest", password="testtest2", email="test@example.com")
        # assert User.objects.filter(email="test@example.com").first()
        # assert user.is_superuser
        # user.save()
        # # call_command("search_index", "--rebuild", "-f")
        #
        # # me = User.objects.get(username='Szymon')
        # # assert me.is_superuser
        #
        # pytest_configure()
        # create_session(user.username, "testtest2")
        # create_session("Szymon", "123412341234a")
        # self.browser.get(pytest.path)
        # take_screenshot(self.browser, "1")
        # self.browser.add_cookie({"name": "csrftoken", "value": pytest.CSRF})
        # self.browser.add_cookie({"name": "sessionid", "value": pytest.SESSION_ID})
        # self.browser.get(pytest.path)
        # take_screenshot(self.browser, "2")
        # assert "HOPE" in browser.title
        # take_screenshot(browser, "2")
        # browser.get(f"{pytest.path}/api/unicorn")
        # take_screenshot(browser, "3")
        self.live_server_url = "http://backend:8000"
        self.browser.get(f"{self.live_server_url}/api/unicorn/")
        take_screenshot(self.browser, f"przed_logowaniem_{self.live_server_url}")
        self.browser.find_element(By.ID, "id_username").send_keys("cypress-username")
        self.browser.find_element(By.ID, "id_password").send_keys("cypress-password")
        self.browser.find_element(By.XPATH, '//*[@id="login-form"]/div[3]/input').click()
        take_screenshot(self.browser, f"po_logowaniu_{self.live_server_url}")
        self.browser.get(f"{self.live_server_url}")
        take_screenshot(self.browser, f"front_{self.live_server_url}")
