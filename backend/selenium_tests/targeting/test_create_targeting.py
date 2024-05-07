import time
from datetime import datetime

import pytest
from dateutil.relativedelta import relativedelta
from selenium.webdriver import Keys, ActionChains

from page_object.programme_details.programme_details import ProgrammeDetails
from page_object.programme_management.programme_management import ProgrammeManagement
from selenium.common import TimeoutException

from hct_mis_api.apps.core.fixtures import DataCollectingTypeFactory
from hct_mis_api.apps.core.models import BusinessArea, DataCollectingType
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program
from page_object.targeting.targeting import Targeting
from page_object.targeting.targeting_create import TargetingCreate

pytestmark = pytest.mark.django_db(transaction=True)


@pytest.fixture
def active_program() -> Program:
    return get_program_with_dct_type_and_name("Active Program", dct_type=DataCollectingType.Type.SOCIAL,
                                              status=Program.ACTIVE)


def get_program_with_dct_type_and_name(
        name: str, dct_type: str = DataCollectingType.Type.STANDARD, status: str = Program.ACTIVE
) -> Program:
    BusinessArea.objects.filter(slug="afghanistan").update(is_payment_plan_applicable=True)
    dct = DataCollectingTypeFactory(type=dct_type)
    program = ProgramFactory(
        name=name,
        start_date=datetime.now() - relativedelta(months=1),
        end_date=datetime.now() + relativedelta(months=1),
        data_collecting_type=dct,
        status=status,
    )
    return program


@pytest.mark.usefixtures("login")
class TestCreateTargeting:
    def test_create_targeting_for_people(
            self,
            active_program: Program,
            pageTargeting: Targeting,
            pageTargetingCreate: TargetingCreate,
    ) -> None:
        pageTargeting.navigate_to_page("afghanistan", active_program.id)
        pageTargeting.getButtonCreateNew().click()
        pageTargeting.getButtonCreateNewByFilters().click()
        assert "New Target Population" in pageTargetingCreate.getTitlePage().text
        pageTargetingCreate.getAddCriteriaButton().click()
        assert pageTargetingCreate.getAddPeopleRuleButton().text.upper() == "ADD PEOPLE RULE"
        pageTargetingCreate.getAddPeopleRuleButton().click()
        pageTargetingCreate.getTargetingCriteriaAutoComplete().click()
        pageTargetingCreate.getTargetingCriteriaAutoComplete().send_keys("Does the Social Worker have disability?")
        pageTargetingCreate.getTargetingCriteriaAutoComplete().send_keys(Keys.ARROW_DOWN)
        pageTargetingCreate.getTargetingCriteriaAutoComplete().send_keys(Keys.ENTER)
        pageTargetingCreate.getTargetingCriteriaValue().click()
        pageTargetingCreate.select_multiple_option_by_name("HEARING", 'SEEING')
        pageTargetingCreate.getTargetingCriteriaAddDialogSaveButton().click()
        pageTargetingCreate.screenshot("xd2")
        # assert 1== 2
        # actions.send_keys(Keys.ENTER).perform()
        # pageTargetingCreate.getTargetingCriteriaValue().send_keys(Keys.ARROW_DOWN)
        # pageTargetingCreate.getTargetingCriteriaValue().send_keys(Keys.ENTER)
