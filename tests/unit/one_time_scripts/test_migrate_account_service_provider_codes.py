from django.test import TestCase

from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.geo import models as geo_models
from hct_mis_api.apps.payment.models import (
    AccountType,
    DeliveryMechanism,
    FinancialInstitution,
    FinancialInstitutionMapping,
    FinancialServiceProvider,
)
from hct_mis_api.one_time_scripts.migrate_account_service_provider_codes import (
    migrate_account_service_provider_codes,
)
from tests.extras.test_utils.factories.household import IndividualFactory
from tests.extras.test_utils.factories.payment import (
    AccountFactory,
    generate_delivery_mechanisms,
)
from tests.extras.test_utils.factories.registration_data import (
    RegistrationDataImportFactory,
)


class TestMigrateAccountServiceProviderCodes(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.ng = geo_models.Country.objects.create(name="Nigeria", iso_code2="NG")
        cls.ba_ng, _ = BusinessArea.objects.get_or_create(
            code="0060",
            defaults={
                "code": "0060",
                "name": "Nigeria",
                "long_name": "Nigeria",
                "region_code": "64",
                "region_name": "SAR",
                "slug": "nigeria",
                "has_data_sharing_agreement": True,
                "kobo_token": "XXX",
            },
        )
        generate_delivery_mechanisms()
        cls.uba_fsp, _ = FinancialServiceProvider.objects.get_or_create(
            name="United Bank for Africa - Nigeria",
            defaults=dict(
                vision_vendor_number=12345, communication_channel=FinancialServiceProvider.COMMUNICATION_CHANNEL_API
            ),
        )
        cls.moneygram_fsp, _ = FinancialServiceProvider.objects.get_or_create(
            name="Moneygram",
            defaults=dict(
                vision_vendor_number=123456, communication_channel=FinancialServiceProvider.COMMUNICATION_CHANNEL_API
            ),
        )
        cls.ecobank_fsp, _ = FinancialServiceProvider.objects.get_or_create(
            name="Nigeria - Eco Bank",
            defaults=dict(
                vision_vendor_number=1234567, communication_channel=FinancialServiceProvider.COMMUNICATION_CHANNEL_API
            ),
        )
        cls.dm_transfer_to_account = DeliveryMechanism.objects.get(code="transfer_to_account")
        cls.nigeria_uba_rdi = RegistrationDataImportFactory(business_area=cls.ba_ng, data_source="Flex Registration")

        for mapping in [
            {
                "uba_institution_name": "9 PAYMENT SERVICE BANK",
                "uba_code": "120001",
                "moneygram_code": "100003",
                "ecobank_code": None,
            },
            {
                "uba_institution_name": "Access Bank",
                "uba_code": "000014",
                "moneygram_code": "000014",
                "ecobank_code": "044",
            },
        ]:
            collector = IndividualFactory(household=None, registration_data_import=cls.nigeria_uba_rdi)
            AccountFactory(
                individual=collector,
                account_type=AccountType.objects.get(key="bank"),
                data={
                    "bank_account_number__transfer_to_account": "123",
                    "bank_name__transfer_to_account": mapping["uba_institution_name"],  # type: ignore
                    "bank_code__transfer_to_account": mapping["uba_code"],  # type: ignore
                    "account_holder_name__transfer_to_account": "Marek",
                },
            )

        cls.nigeria_eco_rdi = RegistrationDataImportFactory(business_area=cls.ba_ng, data_source="Excel")
        for mapping in [
            {
                "uba_institution_name": "Access Bank",
                "uba_code": "000014",
                "moneygram_code": "000014",
                "ecobank_code": "044",
            },
            {
                "uba_institution_name": "Citi Bank",
                "uba_code": "000009",
                "moneygram_code": "000009",
                "ecobank_code": "023",
            },
        ]:
            collector = IndividualFactory(household=None, registration_data_import=cls.nigeria_uba_rdi)
            AccountFactory(
                individual=collector,
                account_type=AccountType.objects.get(key="bank"),
                data={
                    "bank_account_number__transfer_to_account": "123",
                    "bank_name__transfer_to_account": mapping["uba_institution_name"],
                    "bank_code__transfer_to_account": mapping["uba_code"],
                    "account_holder_name__transfer_to_account": "Marek",
                },
            )

    def test_migrate_account_service_provider_codes(self) -> None:
        migrate_account_service_provider_codes()

        """
        Used 3 HOPE mappings: [{'uba_institution_name': 'Citi Bank', 'uba_code': '000009', 'moneygram_code': '000009', 'ecobank_code': '023'}, {'uba_institution_name': '9 PAYMENT SERVICE BANK', 'uba_code': '120001', 'moneygram_code': '100003', 'ecobank_code': None}, {'uba_institution_name': 'Access Bank', 'uba_code': '000014', 'moneygram_code': '000014', 'ecobank_code': '044'}]

        Created 3 UBA FSP mappings: ['000009', '120001', '000014']
        Created 2 ECO FSP mappings: ['023', '044']
        Created 3 MONEYGRAM FSP mappings: ['000009', '100003', '000014']
        """

        self.assertEqual(FinancialInstitution.objects.count(), 3)
        fi1 = FinancialInstitution.objects.get(name="9 PAYMENT SERVICE BANK", country__iso_code2="NG", type="bank")
        fi2 = FinancialInstitution.objects.get(name="Access Bank", country__iso_code2="NG", type="bank")
        fi3 = FinancialInstitution.objects.get(name="Citi Bank", country__iso_code2="NG", type="bank")

        self.assertEqual(FinancialInstitutionMapping.objects.count(), 8)
        FinancialInstitutionMapping.objects.get(
            financial_service_provider=self.uba_fsp, financial_institution=fi1, code="120001"
        )
        FinancialInstitutionMapping.objects.get(
            financial_service_provider=self.uba_fsp, financial_institution=fi2, code="000014"
        )
        FinancialInstitutionMapping.objects.get(
            financial_service_provider=self.uba_fsp, financial_institution=fi3, code="000009"
        )
        FinancialInstitutionMapping.objects.get(
            financial_service_provider=self.ecobank_fsp, financial_institution=fi3, code="023"
        )
        FinancialInstitutionMapping.objects.get(
            financial_service_provider=self.ecobank_fsp, financial_institution=fi2, code="044"
        )
        FinancialInstitutionMapping.objects.get(
            financial_service_provider=self.moneygram_fsp, financial_institution=fi1, code="100003"
        )
        FinancialInstitutionMapping.objects.get(
            financial_service_provider=self.moneygram_fsp, financial_institution=fi2, code="000014"
        )
        FinancialInstitutionMapping.objects.get(
            financial_service_provider=self.moneygram_fsp, financial_institution=fi3, code="000009"
        )
