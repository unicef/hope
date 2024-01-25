from page_object.base_components import BaseComponents


class ErrorPage(BaseComponents):
    # Locators
    pageNotFound = "h1"
    buttonRefresh = "button"
    buttonCountryDashboard = 'button[data-cy="button-go-back"]'

    # Texts
    text404Error = "Access Denied"
    textRefresh = "REFRESH PAGE"
    textGoTo = "GO BACK"

    # Elements

    def getPageNoFound(self):
        return self.wait_for(self.pageNotFound).contains(self.text404Error)

    def getButtonRefresh(self):
        return self.wait_for(self.buttonRefresh).contains(self.textRefresh)

    def getGoToCountryDashboard(self):
        return self.wait_for(self.buttonCountryDashboard).contains(self.textGoTo)
