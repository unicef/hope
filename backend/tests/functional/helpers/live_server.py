from django.contrib.staticfiles.testing import LiveServerTestCase, StaticLiveServerTestCase
from django.conf import settings

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class HopeLiveServer(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        cls.port = 8080
        super(HopeLiveServer, cls).setUpClass()

    def setUp(self) -> None:
        chrome_options = Options()
        # chrome_options.add_argument("--headless")
        # chrome_options.add_argument("--no-sandbox")
        # chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--headless")

        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--allow-insecure-localhost")
        chrome_options.add_argument("--disable-translate")
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--lang=en-GB")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-browser-side-navigation")
        chrome_options.add_argument("--ignore-certificate-errors")
        chrome_options.add_argument("--proxy-server='direct://'")
        chrome_options.add_argument("--proxy-bypass-list=*")

        prefs = {"profile.default_content_setting_values.notifications": 1}  # explicitly allow notifications
        chrome_options.add_experimental_option("prefs", prefs)
        self.browser = webdriver.Chrome(options=chrome_options)
        self.browser.implicitly_wait(2)

    def tearDown(self) -> None:
        self.browser.quit()
