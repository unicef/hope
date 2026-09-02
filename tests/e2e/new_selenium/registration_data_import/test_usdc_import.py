import json

from django.utils import timezone
import pytest

from e2e.new_selenium.conftest import grant_permission
from extras.test_utils.factories.aurora import (
    OrganizationFactory,
    ProjectFactory,
    RecordFactory,
    RegistrationFactory,
)
from extras.test_utils.factories.core import FlexibleAttributeFactory
from extras.test_utils.factories.geo import CountryFactory
from extras.test_utils.factories.household import DocumentTypeFactory
from extras.test_utils.factories.payment import (
    AccountTypeFactory,
    DeliveryMechanismFactory,
    FinancialInstitutionFactory,
)
from extras.test_utils.factories.program import ProgramFactory
from extras.test_utils.selenium import HopeTestBrowser
from hope.apps.account.permissions import Permissions
from hope.apps.core.utils import IDENTIFICATION_TYPE_TO_KEY_MAPPING
from hope.apps.household.const import IDENTIFICATION_TYPE_TAX_ID
from hope.contrib.aurora.services.ukraine_flex_registration_service import UkraineUSDCRegistrationService
from hope.models import (
    BeneficiaryGroup,
    BusinessArea,
    DataCollectingType,
    DeliveryMechanism,
    FinancialInstitution,
    FlexibleAttribute,
    PendingHousehold,
    PendingIndividual,
    Program,
    RegistrationDataImport,
    User,
)

pytestmark = pytest.mark.django_db()


@pytest.fixture
def usdc_import(business_area: BusinessArea, create_super_user: User) -> RegistrationDataImport:
    business_area.postpone_deduplication = True
    business_area.save(update_fields=["postpone_deduplication"])
    CountryFactory(name="Ukraine", short_name="Ukraine", iso_code2="UA", iso_code3="UKR", iso_num="0804")
    DocumentTypeFactory(
        key=IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_TAX_ID],
        label=IDENTIFICATION_TYPE_TAX_ID,
    )
    DeliveryMechanismFactory(
        code="transfer_to_digital_wallet",
        name="Transfer to Digital Wallet",
        transfer_type=DeliveryMechanism.TransferType.DIGITAL,
        account_type=AccountTypeFactory(key="crypto", label="Crypto"),
    )
    FinancialInstitutionFactory(
        name="Generic Crypto",
        type=FinancialInstitution.FinancialInstitutionType.OTHER,
        country=None,
    )
    FlexibleAttributeFactory(name="wallet_num_image_i_f", type=FlexibleAttribute.IMAGE)
    FlexibleAttributeFactory(name="id_wallet_image_i_f", type=FlexibleAttribute.IMAGE)

    program = ProgramFactory(
        name="USDC Program",
        code="USDC",
        status=Program.ACTIVE,
        business_area=business_area,
        data_collecting_type=DataCollectingType.objects.get(code="full"),
        beneficiary_group=BeneficiaryGroup.objects.filter(name="Main Menu").first(),
    )
    organization = OrganizationFactory(business_area=business_area, slug=business_area.slug)
    project = ProjectFactory(organization=organization, programme=program)
    registration = RegistrationFactory(project=project)
    registration.rdi_parser = UkraineUSDCRegistrationService
    registration.save()

    record = RecordFactory(
        registration=registration.source_id,
        timestamp=timezone.now(),
        source_id=1,
        fields={
            "consent": [{"consent_h_c": ["1"]}],
            "individual_details": [
                {
                    "given_name_i_c": "Testina",
                    "middle_name_i_c": "Fakeivna",
                    "family_name_i_c": "Sampleenko",
                    "birth_date": "1991-03-07",
                    "gender_i_c": "female",
                    "phone_no_i_c": "0501234567",
                    "tax_id_no_i_c": "1112223334",
                    "wallet_address_i_c": "0xFAKE0000DEADBEEF",
                    "wallet_name_i_c": "TestWallet",
                    "wallet_num_image_i_f": "d2FsbGV0X251bV9pbWFnZQ==",
                    "id_wallet_image_i_f": "aWRfd2FsbGV0X2ltYWdl",
                }
            ],
        },
        files=json.dumps({}).encode(),
    )

    service = UkraineUSDCRegistrationService(registration)
    rdi = service.create_rdi(create_super_user, "usdc rdi")
    service.process_records(rdi.id, [record.id])
    rdi.status = RegistrationDataImport.IN_REVIEW
    rdi.save(update_fields=["status"])

    return rdi


def test_usdc_import_detail_pages_render_and_rdi_merges(
    browser: HopeTestBrowser,
    user_with_no_permissions: User,
    business_area: BusinessArea,
    usdc_import: RegistrationDataImport,
) -> None:
    rdi = usdc_import
    program = rdi.program
    individual = PendingIndividual.objects.get(registration_data_import=rdi)
    household = PendingHousehold.objects.get(registration_data_import=rdi)

    with grant_permission(
        user_with_no_permissions,
        business_area,
        Permissions.RDI_VIEW_LIST,
        Permissions.RDI_VIEW_DETAILS,
        Permissions.RDI_MERGE_IMPORT,
        Permissions.POPULATION_VIEW_INDIVIDUALS_DETAILS,
        Permissions.POPULATION_VIEW_INDIVIDUALS_LIST,
        Permissions.POPULATION_VIEW_HOUSEHOLDS_DETAILS,
        Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS,
        Permissions.GRIEVANCES_VIEW_LIST_EXCLUDING_SENSITIVE,
        Permissions.GRIEVANCES_VIEW_LIST_SENSITIVE,
    ):
        browser.login(username="noperm_user", password="testtest2")

        browser.open(f"/{business_area.slug}/programs/{program.code}/population/individuals/{individual.id}")
        browser.wait_for_element_visible('h5[data-cy="page-header-title"]')
        browser.assert_text(individual.full_name, 'div[data-cy="label-Full Name"]')
        browser.assert_text(individual.full_name_latin, 'div[data-cy="label-Full Name"]')

        browser.open(f"/{business_area.slug}/programs/{program.code}/population/household/{household.id}")
        browser.wait_for_element_visible('h5[data-cy="page-header-title"]')

        browser.open(f"/{business_area.slug}/programs/{program.code}/registration-data-import/{rdi.id}")
        browser.wait_for_element_clickable('button[data-cy="button-merge-rdi"]').click()
        browser.wait_for_element_clickable('button[data-cy="button-merge"]').click()
        browser.assert_text("MERGED", 'div[data-cy="label-status"]')
