from time import sleep

from e2e.page_object.base_components import BaseComponents
from e2e.webdriver.common.by import By
from e2e.webdriver.common.keys import Keys
from e2e.webdriver.remote.webelement import WebElement
from selenium.common import NoSuchElementException


class ProgrammeManagement(BaseComponents):
    headerTitle = 'h5[data-cy="page-header-title"]'
    buttonNewProgram = 'a[data-cy="button-new-program"]'
    inputProgrammeName = 'input[data-cy="input-name"]'
    labelProgrammeName = 'div[data-cy="input-programme-name"]'
    inputStartDate = 'input[name="startDate"]'
    labelStartDate = 'div[data-cy="date-picker-filter"]'
    inputEndDate = 'input[name="endDate"]'
    labelEndDate = 'input[data-cy="date-input-endDate"]'
    selectSelector = 'div[data-cy="select-sector"]'
    labelSelector = 'div[data-cy="input-sector"]'
    inputDataCollectingType = 'div[data-cy="input-data-collecting-type"]'
    labelDataCollectingType = 'div[data-cy="input-data-collecting-type"]'
    inputCashPlus = 'span[data-cy="input-cashPlus"]'
    inputDescription = 'textarea[data-cy="input-description"]'
    inputBudget = 'input[data-cy="input-budget"]'
    inputAdministrativeAreasOfImplementation = 'input[data-cy="input-administrativeAreasOfImplementation"]'
    inputPopulation = 'input[data-cy="input-populationGoal"]'
    inputBeneficiaryGroup = 'div[data-cy="input-beneficiary-group"]'
    inputFreqOfPaymentOneOff = '//*[@data-cy="input-frequency-of-payment"]/div[1]/div/span'
    inputFreqOfPaymentRegular = '//*[@data-cy="input-frequency-of-payment"]/div[2]/div/span'
    buttonNext = 'button[data-cy="button-next"]'
    buttonBack = 'button[data-cy="button-back"]'
    buttonCancel = 'a[data-cy="button-cancel"]'
    buttonSave = 'button[data-cy="button-save"]'
    selectPartnerAccess = 'div[data-cy="select-partnerAccess"]'
    buttonAddPartner = 'button[data-cy="button-add-partner"]'
    inputPartner = 'div[data-cy="select-partners[0].id"]'
    buttonDelete = 'button[data-cy="button-delete"]'
    labelAdminArea = '//*[@id="radioGroup-partners[0].areaAccess"]/div[2]/div/span'
    calendarIcon = 'button[data-cy="calendar-icon"]'
    calendar = "//*[@data-popper-placement]"
    calendarMonthYear = 'div[role="presentation"]'
    calendarChangeMonth = 'button[title="Next month"]'
    calendarDays = "//*[@data-timestamp]"
    filtersSearch = '//*[@data-cy="filters-search"]/div/input'
    buttonApply = 'button[data-cy="button-filters-clear"]'
    buttonEditProgram = 'button[data-cy="button-edit-program"]'
    selectEditProgramDetails = 'li[data-cy="menu-item-edit-details"]'
    selectEditProgramPartners = 'li[data-cy="menu-item-edit-partners"]'
    selectOptionsContainer = 'ul[data-cy="select-options-container"]'
    inputProgrammeCode = 'input[data-cy="input-programmeCode"]'
    tableRow = 'tr[data-cy="table-row-{}"]'
    stepButtonDetails = 'button[data-cy="step-button-details"]'
    stepButtonTimeSeriesFields = 'button[data-cy="step-button-time-series-fields"]'
    stepButtonPartners = 'button[data-cy="step-button-partners"]'
    title = 'h6[data-cy="title"]'
    description = 'div[data-cy="description"]'
    inputPduFieldsObjectLabel = 'input[data-cy="input-pduFields.{}.label"]'
    selectPduFieldsObjectPduDataSubtype = 'div[data-cy="select-pduFields.{}.pduData.subtype"]'
    selectPduFieldsObjectPduDataNumberOfRounds = 'div[data-cy="select-pduFields.{}.pduData.numberOfRounds"]'
    inputPduFieldsRoundsNames = 'input[data-cy="input-pduFields.{}.pduData.roundsNames.{}"]'
    buttonAddTimeSeriesField = 'button[data-cy="button-add-time-series-field"]'

    def getStepButtonDetails(self) -> WebElement:
        return self.wait_for(self.stepButtonDetails)

    def getStepButtonTimeSeriesFields(self) -> WebElement:
        return self.wait_for(self.stepButtonTimeSeriesFields)

    def getStepButtonPartners(self) -> WebElement:
        return self.wait_for(self.stepButtonPartners)

    def getTitle(self) -> WebElement:
        return self.wait_for(self.title)

    def getDescription(self) -> WebElement:
        return self.wait_for(self.description)

    def getInputPduFieldsObjectLabel(self, index: int) -> WebElement:
        locator = self.inputPduFieldsObjectLabel.format(index)
        return self.wait_for(locator)

    def getSelectPduFieldsObjectPduDataSubtype(self, index: int) -> WebElement:
        locator = self.selectPduFieldsObjectPduDataSubtype.format(index)
        return self.wait_for(locator)

    def getSelectPduFieldsObjectPduDataNumberOfRounds(self, index: int) -> WebElement:
        locator = self.selectPduFieldsObjectPduDataNumberOfRounds.format(index)
        return self.wait_for(locator)

    def getInputPduFieldsRoundsNames(self, pduFieldIndex: int, roundNameIndex: int) -> WebElement:
        locator = self.inputPduFieldsRoundsNames.format(pduFieldIndex, roundNameIndex)
        return self.wait_for(locator)

    def getButtonAddTimeSeriesField(self) -> WebElement:
        return self.wait_for(self.buttonAddTimeSeriesField)

    def getCalendarIcon(self) -> WebElement:
        return self.wait_for(self.calendarIcon)

    def getCalendar(self) -> WebElement:
        return self.wait_for(self.calendar, By.XPATH)

    def chooseAreaAdmin1ByName(self, name: str) -> WebElement:
        return self.wait_for(f"//*[contains(text(), '{name}')]/span", By.XPATH)

    def getLabelAdminArea(self) -> WebElement:
        return self.wait_for(self.labelAdminArea, By.XPATH)

    def getRowByProgramName(self, programName: str) -> WebElement:
        locator = f'tr[data-cy="table-row-{programName}"]'
        self.wait_for(locator)
        return self.get_elements(locator)[0].text.split("\n")

    def getAccessToProgram(self) -> WebElement:
        return self.wait_for(self.selectPartnerAccess)

    def selectWhoAccessToProgram(self, name: str) -> None:
        self.select_option_by_name(name)

    def getSelectOptionsContainer(self) -> WebElement:
        return self.wait_for(self.selectOptionsContainer)

    def getButtonAddPartner(self) -> WebElement:
        return self.wait_for(self.buttonAddPartner)

    def getButtonDelete(self) -> WebElement:
        return self.wait_for(self.buttonDelete)

    def getButtonDeletePopup(self) -> WebElement:
        return self.wait_for("/html/body/div[2]/div[3]/div/div[3]/div/button[2]", By.XPATH)

    def getInputPartner(self) -> WebElement:
        return self.wait_for(self.inputPartner)

    def choosePartnerOption(self, optionName: str) -> None:
        # Todo: Change undefined to name of Partner
        self.getInputPartner().click()
        self.select_option_by_name(optionName)

    def getInputProgrammeName(self) -> WebElement:
        return self.wait_for(self.inputProgrammeName)

    def getLabelProgrammeName(self) -> WebElement:
        return self.wait_for(self.labelProgrammeName)

    def getInputCashPlus(self) -> WebElement:
        return self.wait_for(self.inputCashPlus)

    def getInputFreqOfPaymentOneOff(self) -> WebElement:
        return self.wait_for(self.inputFreqOfPaymentOneOff, By.XPATH)

    def getInputFreqOfPaymentRegular(self) -> WebElement:
        return self.wait_for(self.inputFreqOfPaymentRegular, By.XPATH)

    def getInputStartDate(self) -> WebElement:
        return self.wait_for(self.inputStartDate)

    def chooseInputStartDateViaCalendar(self, day: int) -> None:
        self.get(self.labelStartDate).find_element(By.TAG_NAME, "button").click()
        self.getCalendar()
        # ToDo: Create additional waiting mechanism
        sleep(1)
        self.get_elements(self.calendarDays, By.XPATH)[day - 1].click()
        self.wait_for_disappear(self.calendar, By.XPATH)

    def chooseInputEndDateViaCalendar(self, day: int) -> None:
        self.getLabelEndDate().find_element(By.XPATH, "./..").find_element(By.TAG_NAME, "button").click()
        self.getCalendar()
        month = self.wait_for(self.calendarMonthYear).text
        self.wait_for(self.calendarChangeMonth).click()
        for _ in range(50):
            next_month = self.wait_for(self.calendarMonthYear).text
            sleep(0.1)
            if month != next_month:
                break
        self.get_elements(self.calendarDays, By.XPATH)[day - 1].click()
        self.wait_for_disappear(self.calendar, By.XPATH, timeout=120)

    def getLabelStartDate(self) -> WebElement:
        return self.get_elements(self.labelStartDate)[0]

    def getInputEndDate(self) -> WebElement:
        return self.wait_for(self.inputEndDate)

    def getLabelEndDate(self) -> WebElement:
        return self.wait_for(self.labelEndDate)

    def getButtonNext(self) -> WebElement:
        return self.wait_for(self.buttonNext)

    def getButtonBack(self) -> WebElement:
        return self.wait_for(self.buttonBack)

    def getButtonCancel(self) -> WebElement:
        return self.wait_for(self.buttonCancel)

    def getButtonSave(self) -> WebElement:
        return self.wait_for(self.buttonSave)

    def chooseOptionSelector(self, optionName: str) -> None:
        self.wait_for(self.selectSelector).click()
        self.select_option_by_name(optionName)

    def getLabelSelector(self) -> WebElement:
        return self.wait_for(self.labelSelector)

    def chooseOptionDataCollectingType(self, optionName: str) -> None:
        self.wait_for(self.inputDataCollectingType).click()
        self.select_option_by_name(optionName)

    def getLabelDataCollectingType(self) -> WebElement:
        return self.wait_for(self.labelDataCollectingType)

    def getHeaderTitle(self) -> WebElement:
        return self.wait_for(self.headerTitle)

    def getButtonNewProgram(self) -> WebElement:
        # Workaround because elements overlapped even though Selenium saw that they were available:
        self.driver.execute_script(
            """
            container = document.querySelector("div[data-cy='main-content']")
            container.scrollBy(0,-600)
            """
        )
        sleep(2)
        return self.wait_for(self.buttonNewProgram)

    def fillFiltersSearch(self, filterText: str) -> None:
        self.wait_for(self.filtersSearch, By.XPATH).send_keys(filterText)
        # ToDo: Delete sleep
        sleep(1)
        self.wait_for(self.filtersSearch, By.XPATH).send_keys(Keys.ENTER)

    def getButtonApply(self) -> WebElement:
        return self.wait_for(self.buttonApply)

    def getButtonEditProgram(self) -> WebElement:
        # Workaround because elements overlapped even though Selenium saw that they were available:
        self.driver.execute_script(
            """
            container = document.querySelector("div[data-cy='main-content']")
            container.scrollBy(0,-600)
            """
        )
        sleep(2)
        return self.wait_for(self.buttonEditProgram)

    def getSelectEditProgramDetails(self) -> WebElement:
        return self.wait_for(self.selectEditProgramDetails)

    def getSelectEditProgramPartners(self) -> WebElement:
        return self.wait_for(self.selectEditProgramPartners)

    def getInputProgrammeCode(self) -> WebElement:
        return self.wait_for(self.inputProgrammeCode)

    def getInputDescription(self) -> WebElement:
        return self.wait_for(self.inputDescription)

    def getInputBudget(self) -> WebElement:
        return self.wait_for(self.inputBudget)

    def getInputAdministrativeAreasOfImplementation(self) -> WebElement:
        return self.wait_for(self.inputAdministrativeAreasOfImplementation)

    def getInputPopulation(self) -> WebElement:
        return self.wait_for(self.inputPopulation)

    def getInputBeneficiaryGroup(self) -> WebElement:
        return self.wait_for(self.inputBeneficiaryGroup)

    def getTableRowByProgramName(self, program_name: str) -> WebElement:
        return self.wait_for(self.tableRow.format(program_name))

    def clickNavProgrammeManagement(self) -> None:
        for _ in range(150):
            try:
                self.wait_for(self.navProgrammeManagement).click()
                self.wait_for(self.headerTitle)
                self.wait_for_text("Programme Management", self.headerTitle)
                break
            except BaseException:
                sleep(0.1)
        else:
            raise NoSuchElementException(
                "Could not locate page with title 'Programme Management' after multiple attempts."
            )
