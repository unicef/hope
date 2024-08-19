import pytest
from page_object.country_dashboard.country_dashboard import CountryDashboard

pytestmark = pytest.mark.django_db(transaction=True)


@pytest.mark.usefixtures("login")
class TestSmokeCountryDashboard:

    def test_smoke_country_dashboard(self, pageCountryDashboard: CountryDashboard) -> None:
        pageCountryDashboard.getNavCountryDashboard().click()
        assert "Dashboard" in pageCountryDashboard.getPageHeaderTitle().text
        assert "EXPORT" in pageCountryDashboard.getButtonEdPlan().text
        assert "Programme" in pageCountryDashboard.getFiltersProgram().text
        assert "Programme" in pageCountryDashboard.getProgrammeInput().text
        assert "Admin Level 2" in pageCountryDashboard.getFilterAdministrativeArea().text
        assert "Admin Level 2" in pageCountryDashboard.getAdminLevel2Input().text
        assert "CLEAR" in pageCountryDashboard.getButtonFiltersClear().text
        assert "APPLY" in pageCountryDashboard.getButtonFiltersApply().text
        assert "Administrative Area 2" in pageCountryDashboard.getTableLabel()[0].text
        assert "Total Transferred sorted descending" in pageCountryDashboard.getTableLabel()[1].text.replace("\n", " ")
        assert "Households Reached" in pageCountryDashboard.getTableLabel()[2].text
        assert "Administrative Area 2" in pageCountryDashboard.getTableLabel()[3].text
        assert "Total Transferred sorted descending" in pageCountryDashboard.getTableLabel()[4].text.replace("\n", " ")
        assert "People Reached" in pageCountryDashboard.getTableLabel()[5].text
        assert "0" in pageCountryDashboard.getTotalNumberOfHouseholdsReached().text
        assert "0" in pageCountryDashboard.getTotalNumberOfIndividualsReached().text
        assert "0" in pageCountryDashboard.getTotalNumberOfPeopleReached().text
        assert "0" in pageCountryDashboard.getTotalNumberOfChildrenReached().text
        assert "0" in pageCountryDashboard.getTotalNumberOfGrievances().text
        assert "0" in pageCountryDashboard.getTotalNumberOfFeedback().text
        assert "USD 0.00" in pageCountryDashboard.getTotalAmountTransferred().text
