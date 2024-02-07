import os
from datetime import datetime
from time import sleep

import pytest

from hct_mis_api.apps.core.models import BusinessArea
from helpers.hope import HOPE
from selenium.webdriver.common.by import By
from hct_mis_api.apps.account.models import Partner, Role, User, UserRole
from hct_mis_api.apps.account.fixtures import UserFactory


def take_screenshot(driver, node_id: str) -> None:
    sleep(5)
    if not os.path.exists('screenshot'):
        os.makedirs('screenshot')
    file_name = os.path.join('screenshot',
                             f'{node_id}_{datetime.today().strftime("%Y-%m-%d_%H:%M")}.png'.replace("/", "_").replace(
                                 "::", "__"))
    driver.get_screenshot_as_file(file_name)


class TestAdminPanel(HOPE):

    @pytest.mark.django_db
    def test_login(self):
        Role.objects.create(name="Role")
        BusinessArea.objects.create(
            **{
                "code": "0060",
                "name": "Afghanistan",
                "long_name": "THE ISLAMIC REPUBLIC OF AFGHANISTAN",
                "region_code": "64",
                "region_name": "SAR",
                "slug": "afghanistan",
                "has_data_sharing_agreement": True,
                "is_payment_plan_applicable": False,
                "kobo_token": "XXX",
            }, )
        user = UserFactory.create(is_superuser=True, is_staff=True, username="testtest", password="testtest2",
                                  email="test@example.com")
        UserRole.objects.create(
            user=user,
            role=Role.objects.get(name="Role"),
            business_area=BusinessArea.objects.get(name="Afghanistan"),
        )
        assert User.objects.filter(email="test@example.com").first()
        assert user.is_superuser
        self.browser.get(f"{self.live_server_url}/api/unicorn/")
        # take_screenshot(self.browser, f"przed_logowaniem_{self.live_server_url}")
        self.wait_for(locator="id_username").send_keys("testtest")
        self.get(locator="id_password").send_keys("testtest2")
        self.get(By.XPATH, '//*[@id="login-form"]/div[3]/input').click()
        # take_screenshot(self.browser, f"po_logowaniu_{self.live_server_url}")
        self.browser.get(f"{self.live_server_url}")
        take_screenshot(self.browser, f"front_{self.live_server_url}")
        # self.wait_for(By.CLASS_NAME, "errornote")