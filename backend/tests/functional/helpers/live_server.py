from django.contrib.staticfiles.testing import LiveServerTestCase

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class HopeLiveServer(LiveServerTestCase):
    def setUp(self) -> None:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        self.browser = webdriver.Chrome(options=chrome_options)
        self.browser.implicitly_wait(2)

    def tearDown(self) -> None:
        self.browser.quit()
