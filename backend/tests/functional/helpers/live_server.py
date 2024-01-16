from django.contrib.staticfiles.testing import LiveServerTestCase

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class CustomLiveServer(LiveServerTestCase):
    def setUp(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        #         chrome_options.add_argument("--disable-dev-shm-usage")
        self.browser = webdriver.Chrome(options=chrome_options)
        self.browser.implicitly_wait(2)

    def tearDown(self):
        self.browser.quit()
