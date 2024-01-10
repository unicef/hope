from helper import Common
from selenium.webdriver.common.by import By

class BaseComponents(Common):

    navProgrammeManagement = 'a[data-cy="nav-Programme Management"]'

    def getNavProgrammeManagement(self):
        return self.wait_for(self.navProgrammeManagement)