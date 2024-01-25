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
  getPageNoFound(self):
        return self.wait_for(self.pageNotFound).contains(this.text404Error)
  getButtonRefresh(self):
        return self.wait_for(self.buttonRefresh).contains(this.textRefresh)
  getGoToCountryDashboard(self):
        return self.wait_for(self.buttonCountryDashboard).contains(this.textGoTo)
