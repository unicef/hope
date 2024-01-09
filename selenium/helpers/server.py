import unittest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

class CustomServer(unittest.TestCase):
    def setUp(self):
        self.browser = webdriver.Firefox()
        self.browser.get("http://localhost:8082/api/unicorn/")
        assert "Log in" in self.browser.title
        self.browser.find_element(By.ID, "id_username").send_keys('cypress-username')
        self.browser.find_element(By.ID, "id_password").send_keys('cypress-password')
        self.browser.find_element(By.XPATH, '//*[@id="login-form"]/div[3]/input').click()
        self.browser.get("http://localhost:8082/")
        assert "HOPE" in self.browser.title

    def tearDown(self):
        self.browser.close()
