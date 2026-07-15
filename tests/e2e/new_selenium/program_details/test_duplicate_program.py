from dateutil.relativedelta import relativedelta
from django.utils import timezone
import pytest

from extras.test_utils.factories import DataCollectingTypeFactory, ProgramFactory
from extras.test_utils.selenium import HopeTestBrowser
from hope.models import BeneficiaryGroup, BusinessArea, DataCollectingType, Program

pytestmark = pytest.mark.django_db()


@pytest.fixture
def program_to_duplicate(business_area: BusinessArea) -> Program:
    dct = DataCollectingTypeFactory(type=DataCollectingType.Type.STANDARD)
    beneficiary_group = BeneficiaryGroup.objects.filter(name="Main Menu").first()
    return ProgramFactory(
        name="Programme To Duplicate",
        code="dsrc",
        status=Program.DRAFT,
        business_area=business_area,
        data_collecting_type=dct,
        beneficiary_group=beneficiary_group,
        start_date=timezone.now() - relativedelta(months=1),
        end_date=timezone.now() + relativedelta(months=1),
        budget=200,
        description="Programme to be duplicated",
        administrative_areas_of_implementation="Test Admin Area",
        # NONE access keeps the copied Partners step valid so we can save without
        # having to configure per-partner area access in the wizard.
        partner_access=Program.NONE_PARTNERS_ACCESS,
        cycle=False,
    )


def test_duplicate_programme(login: HopeTestBrowser, program_to_duplicate: Program) -> None:
    """Duplicating a programme copies its fields but uses a new code and stays DRAFT."""
    new_code = "dnew"
    ba_slug = program_to_duplicate.business_area.slug
    code = program_to_duplicate.code

    # Open the source programme details page directly.
    login.open(f"/{ba_slug}/programs/{code}/details/{code}")
    login.wait_for_text(program_to_duplicate.name, 'h5[data-cy="page-header-title"]')

    # Start duplication from the copy button in the details header.
    login.wait_for_element_clickable('[data-cy="button-copy-program"]').click()

    # 1st step (Details) - the name is pre-filled with the "Copy of Programme"
    # prefix and the code must be provided by the user. The data-cy lands on the
    # field wrapper, so the input itself is targeted by its form name.
    login.wait_for_element_visible('input[name="name"]')
    assert "Copy of Programme" in login.get_value('input[name="name"]')
    login.type('input[name="code"]', new_code)
    login.click('button[data-cy="button-next"]')

    # 2nd step (Time Series Fields) - not copied from the source programme.
    login.wait_for_element_visible('button[data-cy="button-add-time-series-field"]')
    login.click('button[data-cy="button-next"]')

    # 3rd step (Partners) - copied partner access, save the duplicate.
    login.wait_for_element_visible('button[data-cy="button-save"]').click()

    # We land on the freshly created programme's details page in DRAFT status.
    login.wait_for_text("Copy of Programme", 'h5[data-cy="page-header-title"]')
    login.assert_text("DRAFT", 'div[data-cy="status-container"]')

    # The duplicate is a brand new programme that copied the source's fields
    # (sector, budget, data collecting type) but uses the new code we entered.
    new_program = Program.objects.exclude(pk=program_to_duplicate.pk).get(name__startswith="Copy of Programme")
    assert new_program.code == new_code
    assert new_program.status == Program.DRAFT
    assert new_program.sector == program_to_duplicate.sector
    assert new_program.budget == program_to_duplicate.budget
    assert new_program.data_collecting_type == program_to_duplicate.data_collecting_type
    assert new_program.description == program_to_duplicate.description
