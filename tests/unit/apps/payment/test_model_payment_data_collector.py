from typing import Any

import pytest

from extras.test_utils.factories.household import HouseholdFactory, IndividualFactory
from extras.test_utils.factories.payment import (
    AccountFactory,
    AccountTypeFactory,
    DeliveryMechanismFactory,
    FinancialServiceProviderFactory,
)
from extras.test_utils.factories.program import ProgramFactory
from extras.test_utils.factories.registration_data import RegistrationDataImportFactory
from hope.models import (
    AccountType,
    DeliveryMechanismConfig,
    FinancialInstitution,
    FspNameMapping,
    MergeStatusModel,
    PaymentDataCollector,
)

pytestmark = pytest.mark.django_db


@pytest.fixture
def account_setup():
    program = ProgramFactory()
    registration_data_import = RegistrationDataImportFactory(program=program)
    ind = IndividualFactory(
        household=None,
        program=program,
        registration_data_import=registration_data_import,
    )
    ind2 = IndividualFactory(
        household=None,
        program=program,
        registration_data_import=registration_data_import,
    )
    household = HouseholdFactory(
        program=program,
        registration_data_import=registration_data_import,
        head_of_household=ind,
        address="address",
    )
    ind.household = household
    ind.save(update_fields=["household"])
    ind2.household = household
    ind2.save(update_fields=["household"])

    fsp = FinancialServiceProviderFactory()
    account_type_bank = AccountTypeFactory(key="bank", label="Bank")
    dm_atm_card = DeliveryMechanismFactory(
        code="atm_card",
        name="ATM Card",
        payment_gateway_id="dm-atm-card",
        account_type=account_type_bank,
    )
    dm_cash = DeliveryMechanismFactory(
        code="cash_over_the_counter",
        name="Cash OTC",
        payment_gateway_id="dm-cash-otc",
        account_type=None,
    )
    dm_config = DeliveryMechanismConfig.objects.create(
        fsp=fsp,
        delivery_mechanism=dm_atm_card,
        required_fields=[],
    )
    financial_institution = FinancialInstitution.objects.create(
        name="ABC", type=FinancialInstitution.FinancialInstitutionType.BANK
    )
    return {
        "program": program,
        "individual": ind,
        "individual_2": ind2,
        "household": household,
        "fsp": fsp,
        "dm_atm_card": dm_atm_card,
        "dm_cash": dm_cash,
        "financial_institution": financial_institution,
        "account_type_bank": account_type_bank,
        "dm_config": dm_config,
    }


def test_get_associated_object(account_setup):
    dmd = AccountFactory(
        data={"test": "test"},
        individual=account_setup["individual"],
        rdi_merge_status=MergeStatusModel.MERGED,
    )
    assert (
        PaymentDataCollector.get_associated_object(
            FspNameMapping.SourceModel.ACCOUNT.value, account_setup["individual"], dmd
        )
        == dmd.account_data
    )
    assert (
        PaymentDataCollector.get_associated_object(
            FspNameMapping.SourceModel.HOUSEHOLD.value, account_setup["individual"]
        )
        == dmd.individual.household
    )
    assert (
        PaymentDataCollector.get_associated_object(
            FspNameMapping.SourceModel.INDIVIDUAL.value, account_setup["individual"]
        )
        == dmd.individual
    )


def test_delivery_data(account_setup):
    dmd = AccountFactory(
        data={
            "name_of_cardholder": "Marek",
        },
        individual=account_setup["individual"],
        account_type=AccountType.objects.get(key="bank"),
        number="test",
        financial_institution=account_setup["financial_institution"],
        rdi_merge_status=MergeStatusModel.MERGED,
    )

    fsp2 = FinancialServiceProviderFactory()
    assert (
        PaymentDataCollector.delivery_data(fsp2, account_setup["dm_atm_card"], account_setup["individual"])
        == dmd.account_data
    )

    dm_config = account_setup["dm_config"]
    dm_config.required_fields.extend(["custom_ind_name", "custom_hh_address", "address", "name_of_cardholder"])
    dm_config.save()

    FspNameMapping.objects.create(
        external_name="custom_ind_name",
        hope_name="my_custom_ind_name",
        source=FspNameMapping.SourceModel.INDIVIDUAL,
        fsp=account_setup["fsp"],
    )
    FspNameMapping.objects.create(
        external_name="custom_hh_address",
        hope_name="my_custom_hh_address",
        source=FspNameMapping.SourceModel.HOUSEHOLD,
        fsp=account_setup["fsp"],
    )
    FspNameMapping.objects.create(
        external_name="address",
        hope_name="address",
        source=FspNameMapping.SourceModel.HOUSEHOLD,
        fsp=account_setup["fsp"],
    )

    def my_custom_ind_name(self: Any) -> str:
        return f"{self.full_name} Custom"

    dmd.individual.__class__.my_custom_ind_name = property(my_custom_ind_name)

    def my_custom_hh_address(self: Any) -> str:
        return f"{self.address} Custom"

    account_setup["household"].__class__.my_custom_hh_address = property(my_custom_hh_address)

    assert PaymentDataCollector.delivery_data(
        account_setup["fsp"], account_setup["dm_atm_card"], account_setup["individual"]
    ) == {
        "number": "test",
        "name_of_cardholder": "Marek",
        "custom_ind_name": f"{dmd.individual.full_name} Custom",
        "custom_hh_address": f"{account_setup['household'].address} Custom",
        "address": account_setup["household"].address,
        "financial_institution_name": str(account_setup["financial_institution"].name),
        "financial_institution_pk": str(account_setup["financial_institution"].id),
    }


def test_delivery_data_setter(account_setup):
    account = AccountFactory(
        data={
            "expiry_date": "12.12.2024",
            "name_of_cardholder": "Marek",
        },
        individual=account_setup["individual"],
        account_type=account_setup["account_type_bank"],
        number="test",
        financial_institution=account_setup["financial_institution"],
        rdi_merge_status=MergeStatusModel.MERGED,
    )
    financial_institution2 = FinancialInstitution.objects.create(
        name="DEF", type=FinancialInstitution.FinancialInstitutionType.BANK
    )

    account.account_data = {
        "number": "456",
        "financial_institution": str(financial_institution2.id),
        "expiry_date": "12.12.2025",
        "new_field": "new_value",
    }
    account.save()

    assert account.account_data == {
        "number": "456",
        "expiry_date": "12.12.2025",
        "financial_institution_pk": str(financial_institution2.id),
        "financial_institution_name": str(financial_institution2.name),
        "new_field": "new_value",
        "name_of_cardholder": "Marek",
    }


def test_validate_account(account_setup):
    fsp = account_setup["fsp"]
    collector = account_setup["individual"]

    # Account type not required (cash delivery mechanism)
    assert PaymentDataCollector.validate_account(fsp, account_setup["dm_cash"], collector) is True

    # No delivery mechanism config -> validation passes
    dm_without_config = DeliveryMechanismFactory(
        code="atm_card_no_config",
        name="ATM Card No Config",
        account_type=account_setup["account_type_bank"],
    )
    assert PaymentDataCollector.validate_account(fsp, dm_without_config, collector) is True

    # Config requires account field but account missing -> validation fails
    dm_config = account_setup["dm_config"]
    dm_config.required_fields = ["expiry_date"]
    dm_config.save()
    assert PaymentDataCollector.validate_account(fsp, account_setup["dm_atm_card"], collector) is False

    # Account has required fields -> validation passes
    AccountFactory(
        number="test",
        data={
            "expiry_date": "12.12.2024",
        },
        individual=collector,
        account_type=account_setup["account_type_bank"],
        rdi_merge_status=MergeStatusModel.MERGED,
    )
    assert PaymentDataCollector.validate_account(fsp, account_setup["dm_atm_card"], collector) is True

    # Missing required account field -> validation fails
    dm_config.required_fields = ["expiry_date", "missing_field"]
    dm_config.save(update_fields=["required_fields"])
    assert PaymentDataCollector.validate_account(fsp, account_setup["dm_atm_card"], collector) is False

    # Required mapped household/individual fields present -> validation passes
    collector.phone_no = "+48111222333"
    collector.save(update_fields=["phone_no"])
    account_setup["household"].address = "Main Street 1"
    account_setup["household"].save(update_fields=["address"])

    FspNameMapping.objects.create(
        external_name="address",
        hope_name="address",
        source=FspNameMapping.SourceModel.HOUSEHOLD,
        fsp=fsp,
    )
    FspNameMapping.objects.create(
        external_name="phone_no",
        hope_name="phone_no",
        source=FspNameMapping.SourceModel.INDIVIDUAL,
        fsp=fsp,
    )

    dm_config.required_fields = ["address", "phone_no"]
    dm_config.save(update_fields=["required_fields"])
    assert PaymentDataCollector.validate_account(fsp, account_setup["dm_atm_card"], collector) is True

    # Missing mapped individual field -> validation fails
    collector.phone_no = ""
    collector.save(update_fields=["phone_no"])
    assert PaymentDataCollector.validate_account(fsp, account_setup["dm_atm_card"], collector) is False
