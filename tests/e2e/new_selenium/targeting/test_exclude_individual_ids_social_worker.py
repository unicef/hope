"""E2E regression test for PR #5869 (AB#308529).

https://github.com/unicef/hope/pull/5869
"fix: exclusion by individual IDs not working in social worker programs"
"""

import pytest

from e2e.new_selenium.conftest import grant_permission
from extras.test_utils.factories import (
    DataCollectingTypeFactory,
    HouseholdFactory,
    PaymentPlanGroupFactory,
    PaymentPlanPurposeFactory,
    TargetingCriteriaRuleFactory,
)
from extras.test_utils.factories.payment import PaymentPlanFactory
from extras.test_utils.factories.program import ProgramCycleFactory, ProgramFactory
from extras.test_utils.selenium import HopeTestBrowser
from hope.apps.account.permissions import Permissions
from hope.apps.payment.services.payment_plan_services import PaymentPlanService
from hope.models import (
    BeneficiaryGroup,
    BusinessArea,
    DataCollectingType,
    PaymentPlan,
    PaymentPlanPurpose,
    Program,
    User,
)

pytestmark = pytest.mark.django_db()


@pytest.fixture
def social_purpose() -> PaymentPlanPurpose:
    return PaymentPlanPurposeFactory(name="Social Worker Purpose")


@pytest.fixture
def social_program(business_area: BusinessArea, social_purpose: PaymentPlanPurpose) -> Program:
    # "People" beneficiary group (master_detail=False) is pre-seeded by create_super_user.
    dct = DataCollectingTypeFactory(type=DataCollectingType.Type.SOCIAL, individual_filters_available=True)
    beneficiary_group = BeneficiaryGroup.objects.get(name="People")
    program = ProgramFactory(
        business_area=business_area,
        status=Program.DRAFT,
        cycle=False,
        data_collecting_type=dct,
        beneficiary_group=beneficiary_group,
    )
    # Program.clean() requires at least one purpose before status=ACTIVE save
    program.payment_plan_purposes.add(social_purpose)
    program.status = Program.ACTIVE
    program.save()
    return program


@pytest.fixture
def social_people(social_program: Program, business_area: BusinessArea) -> dict:
    # unicef_id is normally assigned by a DB trigger that isn't active in this suite, so set it
    # explicitly (the exclusion maps an "IND" id to its "HH" household unicef_id).
    hh1 = HouseholdFactory(unicef_id="HH-99-0001.0001", business_area=business_area, program=social_program)
    hh2 = HouseholdFactory(unicef_id="HH-99-0002.0001", business_area=business_area, program=social_program)
    ind1 = hh1.head_of_household
    ind1.unicef_id = "IND-99-0001.0001"
    ind1.save(update_fields=["unicef_id"])
    ind2 = hh2.head_of_household
    ind2.unicef_id = "IND-99-0002.0001"
    ind2.save(update_fields=["unicef_id"])
    return {"hh1": hh1, "ind1": ind1, "hh2": hh2, "ind2": ind2}


@pytest.fixture
def social_tp(
    social_program: Program,
    social_purpose: PaymentPlanPurpose,
    social_people: dict,
) -> PaymentPlan:
    cycle = ProgramCycleFactory(program=social_program, title="Social Worker Cycle")
    group = PaymentPlanGroupFactory(cycle=cycle, name="Social Worker Group")
    ind1 = social_people["ind1"]
    ind2 = social_people["ind2"]

    tp = PaymentPlanFactory(
        name="Exclusion Regression TP",
        program_cycle=cycle,
        payment_plan_group=group,
        status=PaymentPlan.Status.TP_OPEN,
        business_area=social_program.business_area,
    )
    tp.payment_plan_purposes.add(social_purpose)
    # Include both people by individual ID. TargetingCriteriaRule.get_query() splits on ", ".
    TargetingCriteriaRuleFactory(payment_plan=tp, individual_ids=f"{ind1.unicef_id}, {ind2.unicef_id}")

    # Build the population so the People list starts with both people.
    PaymentPlanService(tp).full_rebuild()
    tp.build_status = PaymentPlan.BuildStatus.BUILD_STATUS_OK
    tp.save(update_fields=["build_status"])
    tp.refresh_from_db()
    return tp


def test_exclude_individual_id_removes_person_in_social_program(
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    social_tp: PaymentPlan,
    social_people: dict,
) -> None:
    program = social_tp.program_cycle.program
    ind1 = social_people["ind1"]
    ind2 = social_people["ind2"]
    with grant_permission(
        user_with_no_permissions,
        business_area,
        Permissions.TARGETING_VIEW_DETAILS,
        Permissions.TARGETING_UPDATE,
        Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS,
        Permissions.PM_PROGRAMME_CYCLE_VIEW_LIST,
        Permissions.PM_PAYMENT_PLAN_GROUP_VIEW_LIST,
    ):
        browser.login(username="noperm_user", password="testtest2")

        # Baseline: both people appear in the target population
        browser.open(f"/{business_area.slug}/programs/{program.code}/target-population/{social_tp.id}")
        browser.wait_for_element_visible('[data-cy="target-population-people-row"]')
        baseline_rows = browser.find_elements('[data-cy="target-population-people-row"]')
        assert len(baseline_rows) == 2
        browser.assert_text(ind1.unicef_id)
        browser.assert_text(ind2.unicef_id)

        # Exclude one person by individual unicef_id via the edit form
        browser.open(f"/{business_area.slug}/programs/{program.code}/target-population/edit-tp/{social_tp.id}")
        browser.wait_for_element_clickable('[data-cy="button-show-hide-exclusions"]').click()
        browser.wait_for_element_visible('[data-cy="input-excluded-ids"] input')
        browser.type('[data-cy="input-excluded-ids"] input', ind1.unicef_id)
        browser.type('[data-cy="input-exclusion-reason"] textarea', "Regression check for PR #5869")
        browser.wait_for_element_clickable('[data-cy="button-save"]').click()

        # Save redirects to the detail page once the rebuild (celery eager) has run
        browser.wait_for_element_absent('[data-cy="edit-target-population-form"]', timeout=20)
        browser.wait_for_element_visible('[data-cy="title-excluded-entries"]', timeout=20)

        # The excluded person is dropped from the People list; only the other remains
        browser.wait_for_text(ind2.unicef_id, '[data-cy="target-population-people-row"]', timeout=20)
        remaining_rows = browser.find_elements('[data-cy="target-population-people-row"]')
        assert len(remaining_rows) == 1
        assert ind2.unicef_id in remaining_rows[0].text
        assert ind1.unicef_id not in remaining_rows[0].text
