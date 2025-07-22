from selenium.page_object.base_components import BaseComponents
from selenium.webdriver.remote.webelement import WebElement


class GrievanceDashboard(BaseComponents):
    # Locators
    pageHeaderTitle = 'h5[data-cy="page-header-title"]'
    totalNumberOfTicketsTopNumber = 'div[data-cy="total-number-of-tickets-top-number"]'
    labelizedFieldContainerTotalNumberOfTicketsSystemGenerated = (
        'div[data-cy="labelized-field-container-total-number-of-tickets-system-generated"]'
    )
    labelSystemGenerated = 'div[data-cy="label-SYSTEM-GENERATED"]'
    labelizedFieldContainerTotalNumberOfTicketsUserGenerated = (
        'div[data-cy="labelized-field-container-total-number-of-tickets-user-generated"]'
    )
    labelUserGenerated = 'div[data-cy="label-USER-GENERATED"]'
    totalNumberOfClosedTicketsTopNumber = 'div[data-cy="total-number-of-closed-tickets-top-number"]'
    labelizedFieldContainerTotalNumberOfClosedTicketsSystemGenerated = (
        'div[data-cy="labelized-field-container-total-number-of-closed-tickets-system-generated"]'
    )
    labelizedFieldContainerTotalNumberOfClosedTicketsUserGenerated = (
        'div[data-cy="labelized-field-container-total-number-of-closed-tickets-user-generated"]'
    )
    ticketsAverageResolutionTopNumber = 'div[data-cy="tickets-average-resolution-top-number"]'
    labelizedFieldContainerTicketsAverageResolutionSystemGenerated = (
        'div[data-cy="labelized-field-container-tickets-average-resolution-system-generated"]'
    )
    labelizedFieldContainerTicketsAverageResolutionUserGenerated = (
        'div[data-cy="labelized-field-container-tickets-average-resolution-user-generated"]'
    )

    # Texts
    textTitle = "Grievance Dashboard"

    # Elements

    def getPageHeaderContainer(self) -> WebElement:
        return self.wait_for(self.pageHeaderContainer)

    def getPageHeaderTitle(self) -> WebElement:
        return self.wait_for(self.pageHeaderTitle)

    def getTotalNumberOfTicketsTopNumber(self) -> WebElement:
        return self.wait_for(self.totalNumberOfTicketsTopNumber)

    def getLabelizedFieldContainerTotalNumberOfTicketsSystemGenerated(self) -> WebElement:
        return self.wait_for(self.labelizedFieldContainerTotalNumberOfTicketsSystemGenerated)

    def getLabelSystemGenerated(self) -> WebElement:
        return self.wait_for(self.labelSystemGenerated)

    def getLabelizedFieldContainerTotalNumberOfTicketsUserGenerated(self) -> WebElement:
        return self.wait_for(self.labelizedFieldContainerTotalNumberOfTicketsUserGenerated)

    def getLabelUserGenerated(self) -> WebElement:
        return self.wait_for(self.labelUserGenerated)

    def getTotalNumberOfClosedTicketsTopNumber(self) -> WebElement:
        return self.wait_for(self.totalNumberOfClosedTicketsTopNumber)

    def getLabelizedFieldContainerTotalNumberOfClosedTicketsSystemGenerated(self) -> WebElement:
        return self.wait_for(self.labelizedFieldContainerTotalNumberOfClosedTicketsSystemGenerated)

    def getLabelizedFieldContainerTotalNumberOfClosedTicketsUserGenerated(self) -> WebElement:
        return self.wait_for(self.labelizedFieldContainerTotalNumberOfClosedTicketsUserGenerated)

    def getTicketsAverageResolutionTopNumber(self) -> WebElement:
        return self.wait_for(self.ticketsAverageResolutionTopNumber)

    def getLabelizedFieldContainerTicketsAverageResolutionSystemGenerated(self) -> WebElement:
        return self.wait_for(self.labelizedFieldContainerTicketsAverageResolutionSystemGenerated)

    def getLabelizedFieldContainerTicketsAverageResolutionUserGenerated(self) -> WebElement:
        return self.wait_for(self.labelizedFieldContainerTicketsAverageResolutionUserGenerated)
