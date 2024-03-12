import os
from time import sleep

from page_object.base_components import BaseComponents
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement


class ProgrammeManagement(BaseComponents):
    headerTitle = 'h5[data-cy="page-header-title"]'
    buttonNewProgram = 'a[data-cy="button-new-program"]'
    inputProgrammeName = 'input[data-cy="input-name"]'
    labelProgrammeName = 'div[data-cy="input-programme-name"]'
    inputStartDate = 'input[name="startDate"]'
    labelStartDate = 'div[data-cy="input-start-date"]'
    inputEndDate = 'input[name="endDate"]'
    labelEndDate = 'div[data-cy="input-end-date"]'
    selectSelector = 'div[data-cy="select-sector"]'
    labelSelector = 'div[data-cy="input-sector"]'
    inputDataCollectingType = 'div[data-cy="input-data-collecting-type"]'
    labelDataCollectingType = 'div[data-cy="input-data-collecting-type"]'
    inputCashPlus = 'span[data-cy="input-cashPlus"]'
    inputDescription = 'textarea[data-cy="input-description"]'
    inputBudget = 'input[data-cy="input-budget"]'
    inputAdministrativeAreasOfImplementation = 'input[data-cy="input-administrativeAreasOfImplementation"]'
    inputPopulation = 'input[data-cy="input-populationGoal"]'
    inputFreqOfPaymentOneOff = '//*[@data-cy="input-frequency-of-payment"]/div[1]/div/span'
    inputFreqOfPaymentRegular = '//*[@data-cy="input-frequency-of-payment"]/div[2]/div/span'
    buttonNext = 'button[data-cy="button-next"]'
    buttonBack = 'button[data-cy="button-back"]'
    buttonCancel = 'a[data-cy="button-cancel"]'
    buttonSave = 'button[data-cy="button-save"]'
    buttonAddPartner = 'button[data-cy="button-add-partner"]'
    inputPartner = 'div[data-cy="select-partners[0].id"]'
    buttonDelete = 'button[data-cy="button-delete"]'
    labelAdminArea = '//*[@id="radioGroup-partners[0].areaAccess"]/div[2]/div/span/span[1]'
    calendarIcon = 'button[data-cy="calendar-icon"]'
    calendar = 'div[data-cy="date-picker-container"]'
    calendarMonthYear = (
        '//*[@class="MuiPickersSlideTransition-transitionContainer ' 'MuiPickersCalendarHeader-transitionContainer"]'
    )
    calendarChangeMonth = '//*[@class="MuiButtonBase-root MuiIconButton-root MuiPickersCalendarHeader-iconButton"]'
    calendarDays = (
        '//*[@class="MuiButtonBase-root MuiIconButton-root MuiPickersDay-day" '
        'or @class="MuiButtonBase-root MuiIconButton-root MuiPickersDay-day MuiPickersDay-current '
        'MuiPickersDay-daySelected" '
        'or @class="MuiButtonBase-root MuiIconButton-root MuiPickersDay-day '
        'MuiPickersDay-dayDisabled"]'
    )
    filtersSearch = '//*[@data-cy="filters-search"]/div/input'
    buttonApply = 'button[data-cy="button-filters-clear"]'

    def getCalendarIcon(self) -> WebElement:
        return self.wait_for(self.calendarIcon)

    def getCalendar(self) -> WebElement:
        return self.wait_for(self.calendar)

    def chooseAreaAdmin1ByName(self, name: str) -> WebElement:
        return self.wait_for(f"//*[contains(text(), '{name}')]/span", By.XPATH)

    def getLabelAdminArea(self) -> WebElement:
        return self.wait_for(self.labelAdminArea, By.XPATH)

    def getRowByProgramName(self, programName: str) -> WebElement:
        locator = f'tr[data-cy="table-row-{programName}"]'
        self.wait_for(locator)
        return self.get_elements(locator)[0].text.split("\n")

    def getButtonAddPartner(self) -> WebElement:
        return self.wait_for(self.buttonAddPartner)

    def getButtonDelete(self) -> WebElement:
        return self.wait_for(self.buttonDelete)

    def getButtonDeletePopup(self) -> WebElement:
        return self.wait_for("/html/body/div[2]/div[3]/div/div[3]/div/button[2]", By.XPATH)

    def choosePartnerOption(self, optionName: str) -> None:
        # Todo: Change undefined to name of Partner
        selectOption = f'li[data-cy="select-option-{optionName}"]'
        self.wait_for(self.inputPartner).click()
        self.wait_for(selectOption).click()
        self.wait_for_disappear(selectOption)

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

    def getInputStartDate(self, test_data: dict) -> None:
        self.driver.get_screenshot_as_file(os.path.join('screenshot', 'aprzed.png'))
        print(self.driver.capabilities['browserVersion'])
        import selenium
        print(selenium.__version__)
        # x = self.wait_for("MuiFormControl-root MuiTextField-root css-197rvjk-MuiFormControl-root-MuiTextField-root", By.CLASS_NAME).location
        # x.screenshot(os.path.join('screenshot', f'div.png'))
        self.wait_for(self.inputStartDate).send_keys(test_data["startDate"].numerically_formatted_date)
        print(self.wait_for(self.inputStartDate).get_attribute("value"))
        element = self.wait_for(self.inputStartDate)
        self.driver.execute_script("arguments[0].value='" + test_data["startDate"].numerically_formatted_date + "';", element)
        sleep(1)
        print(self.wait_for(self.inputStartDate).get_attribute("value"))
        self.driver.get_screenshot_as_file(os.path.join('screenshot', 'foo2.png'))
        # self.driver.execute_script("arguments[0].click();", self.wait_for(self.inputStartDate))
        el = self.wait_for(self.inputStartDate)
        str = el.tag_name
        parent = el.find_element("xpath", "..")
        children = parent.find_elements("xpath", "*")
        print(parent.tag_name, parent.get_attribute("class"))
        for child in children:
            print(f'- {child.tag_name}, {child.get_attribute("class")}')
            children2 = child.find_elements("xpath", "*")
            for child2 in children2:
                print(f'-- {child2.tag_name}, {child.get_attribute("class")}')

        # self.driver.get_screenshot_as_file(os.path.join('screenshot', 'foo0.png'))
        # print(self.wait_for(self.inputStartDate).get_attribute('value'))
        # # from time import sleep
        # # sleep(2)
        # self.wait_for(self.inputStartDate).send_keys(test_data["startDate"].numerically_formatted_date)
        # print(self.wait_for(self.inputStartDate).get_attribute('value'))
        # self.wait_for(self.inputStartDate).send_keys("2")
        # print(self.wait_for(self.inputStartDate).get_attribute('value'))
        # nowyno = self.wait_for(self.inputStartDate)
        # for i in range(7):
        #     nowyno = nowyno.find_element(By.XPATH, '..')
        #     nowyno.screenshot(os.path.join('screenshot', f'parent{i}.png'))

        # calendar_icon = self.get_elements('//button/*[name()="svg"]', By.XPATH)
        # calendar_icon[0].screenshot(os.path.join('screenshot', f'svg1.png'))
        # calendar_icon = self.get_elements('svg[data-testid="CalendarIcon"]')
        # calendar_icon[0].screenshot(os.path.join('screenshot', f'svg2.png'))
        # calendar_icon[0].click()
        # elem = self.wait_for(self.inputStartDate)
        # ac = ActionChains(self.driver)
        # ac.move_to_element(elem).move_by_offset(xy["x"], xy["y"]).click().perform()
        # ac = ActionChains(self.driver)
        # print(xy)
        # ac.move_by_offset(xy["x"]+10, xy["y"]).click().perform()
        # sleep(1)
        # self.driver.get_screenshot_as_file(os.path.join('screenshot', 'foo1.png'))
        # print(self.wait_for(self.inputStartDate).get_attribute('value'))
        # self.wait_for(self.inputStartDate).send_keys("0")

        # return self.wait_for(self.inputStartDate, By.XPATH)
        # text_input = self.driver.find_element(By.CSS_SELECTOR, self.inputStartDate)
        # ActionChains(self.driver).send_keys_to_element(text_input, "2003").perform()

    def chooseInputStartDateViaCalendar(self, day: int) -> None:
        self.find_in_element(self.getLabelStartDate(), self.calendarIcon)[0].click()
        self.getCalendar()
        # ToDo: Create additional waiting mechanism
        from time import sleep

        sleep(1)
        self.get_elements(self.calendarDays, By.XPATH)[day - 1].click()
        self.wait_for_disappear(self.calendar)

    def chooseInputEndDateViaCalendar(self, day: int) -> None:
        self.find_in_element(self.getLabelEndDate(), self.calendarIcon)[0].click()
        self.getCalendar()
        month = self.get(self.calendarMonthYear, By.XPATH).text
        self.get_elements(self.calendarChangeMonth, By.XPATH)[0].click()
        for _ in range(5):
            next_month = self.get(self.calendarMonthYear, By.XPATH).text
            sleep(1)
            if month != next_month:
                break
        self.get_elements(self.calendarDays, By.XPATH)[day - 1].click()
        self.wait_for_disappear(self.calendar)

    def getLabelStartDate(self) -> WebElement:
        return self.wait_for(self.labelStartDate)

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
        selectOption = f'li[data-cy="select-option-{optionName}"]'
        self.wait_for(self.selectSelector).click()
        self.wait_for(selectOption).click()
        self.wait_for_disappear(selectOption)

    def getLabelSelector(self) -> WebElement:
        return self.wait_for(self.labelSelector)

    def chooseOptionDataCollectingType(self, optionName: str) -> None:
        selectOption = f'li[data-cy="select-option-{optionName}"]'
        self.wait_for(self.inputDataCollectingType).click()
        self.wait_for(selectOption).click()
        self.wait_for_disappear(selectOption)

    def getLabelDataCollectingType(self) -> WebElement:
        return self.wait_for(self.labelDataCollectingType)

    def getHeaderTitle(self) -> WebElement:
        return self.wait_for(self.headerTitle)

    def getButtonNewProgram(self) -> WebElement:
        # Workaround because elements overlapped even though Selenium saw that they were available:
        self.driver.execute_script(
            """
            container = document.querySelector("div[data-cy='main-content']")
            container.scrollBy(0,600)
            """
        )
        return self.wait_for(self.buttonNewProgram)

    def fillFiltersSearch(self, filterText: str) -> None:
        self.wait_for(self.filtersSearch, By.XPATH).send_keys(filterText)
        # ToDo: Delete sleep
        sleep(1)
        self.wait_for(self.filtersSearch, By.XPATH).send_keys(Keys.ENTER)

    def getButtonApply(self) -> WebElement:
        return self.wait_for(self.buttonApply)

    def getInputDescription(self) -> WebElement:
        return self.wait_for(self.inputDescription)

    def getInputBudget(self) -> WebElement:
        return self.wait_for(self.inputBudget)

    def getInputAdministrativeAreasOfImplementation(self) -> WebElement:
        return self.wait_for(self.inputAdministrativeAreasOfImplementation)

    def getInputPopulation(self) -> WebElement:
        return self.wait_for(self.inputPopulation)
