from django.test import TestCase

from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.household import HouseholdFactory, IndividualFactory
from extras.test_utils.factories.payment import (
    AccountFactory,
    generate_delivery_mechanisms,
)

from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.geo import models as geo_models
from hct_mis_api.apps.payment.models import (
    AccountType,
    FinancialInstitution,
    FinancialInstitutionMapping,
    FinancialServiceProvider,
)
from hct_mis_api.one_time_scripts.create_financial_institutions import (
    create_financial_institutions,
)


class TestCreateFinancialInstitutions(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.ba_afg = create_afghanistan()
        cls.ba_ng, _ = BusinessArea.objects.get_or_create(
            code="0061",
            defaults={
                "code": "0061",
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
        account_type_mobile = AccountType.objects.get(key="mobile")
        account_type_bank = AccountType.objects.get(key="bank")
        cls.uba_fsp, _ = FinancialServiceProvider.objects.get_or_create(
            name="United Bank for Africa - Nigeria",
            defaults=dict(
                vision_vendor_number=12345, communication_channel=FinancialServiceProvider.COMMUNICATION_CHANNEL_API
            ),
        )
        cls.nigeria = geo_models.Country.objects.create(name="Nigeria", iso_code2="NG", iso_code3="NG", iso_num="NG")
        cls.afg = geo_models.Country.objects.create(name="Afghanistan", iso_code2="AF", iso_code3="AF", iso_num="0004")

        # ng account
        collector1 = IndividualFactory(household=None, business_area=cls.ba_ng)
        hh1 = HouseholdFactory(head_of_household=collector1, country=cls.nigeria)
        collector1.household = hh1
        collector1.save()
        cls.acc1 = AccountFactory(
            individual=collector1,
            account_type=account_type_bank,
            number="123",
            data={
                "number": "123",
                "name": "bank1",
                "code": "456",
            },
        )
        fi_ng = FinancialInstitution.objects.create(
            name="bank1",
            type=FinancialInstitution.FinancialInstitutionType.BANK,
        )
        cls.mapping_ng = FinancialInstitutionMapping.objects.create(
            financial_service_provider=cls.uba_fsp, financial_institution=fi_ng, code="456"
        )

        # afg accounts:

        # same financial institution for bank type
        collector2 = IndividualFactory(household=None, business_area=cls.ba_afg)
        hh2 = HouseholdFactory(head_of_household=collector2, country=cls.afg)
        collector2.household = hh2
        collector2.save()
        cls.acc2 = AccountFactory(
            individual=collector2,
            account_type=account_type_bank,
            number="111",
            data={
                "number": "111",
                "name": "bank2",
                "code": "666",
            },
        )
        collector3 = IndividualFactory(household=None, business_area=cls.ba_afg)
        hh3 = HouseholdFactory(head_of_household=collector3, country=cls.afg)
        collector3.household = hh3
        collector3.save()
        cls.acc3 = AccountFactory(
            individual=collector3,
            account_type=account_type_bank,
            number="222",
            data={
                "number": "222",
                "name": "bank2b",
                "code": "666",
            },
        )

        # another financial institution for bank type
        collector4 = IndividualFactory(household=None, business_area=cls.ba_afg)
        hh4 = HouseholdFactory(head_of_household=collector4, country=cls.afg)
        collector4.household = hh4
        collector4.save()
        cls.acc4 = AccountFactory(
            individual=collector4,
            account_type=account_type_bank,
            number="333",
            data={
                "number": "333",
                "name": "bank3",
                "code": "667",
            },
        )

        # same financial institution for mobile type
        collector5 = IndividualFactory(household=None, business_area=cls.ba_afg)
        hh5 = HouseholdFactory(head_of_household=collector5, country=cls.afg)
        collector5.household = hh5
        collector5.save()
        cls.acc5 = AccountFactory(
            individual=collector5,
            account_type=account_type_mobile,
            number="444",
            data={
                "number": "444",
                "provider": "bank4",
                "service_provider_code": "668",
            },
        )
        collector6 = IndividualFactory(household=None, business_area=cls.ba_afg)
        hh6 = HouseholdFactory(head_of_household=collector6, country=cls.afg)
        collector6.household = hh6
        collector6.save()
        cls.acc6 = AccountFactory(
            individual=collector6,
            account_type=account_type_mobile,
            number="555",
            data={
                "number": "555",
                "provider": "bank4b",
                "service_provider_code": "668",
            },
        )

        # another financial institution for mobile type
        collector7 = IndividualFactory(household=None, business_area=cls.ba_afg)
        hh7 = HouseholdFactory(head_of_household=collector7, country=cls.afg)
        collector7.household = hh7
        collector7.save()
        cls.acc7 = AccountFactory(
            individual=collector7,
            account_type=account_type_mobile,
            number="666",
            data={
                "number": "666",
                "provider": "bank5",
                "service_provider_code": "669",
            },
        )

    def test_migrate_account_service_provider_codes(self) -> None:
        create_financial_institutions()

        self.assertEqual(FinancialInstitution.objects.count(), 5)
        fi_ng = FinancialInstitution.objects.get(name="bank1", type="bank")
        self.acc1.refresh_from_db()
        self.assertEqual(self.acc1.financial_institution, fi_ng)

        fi_afg_1 = FinancialInstitution.objects.get(name="bank2", swift_code="666", type="bank")
        self.acc2.refresh_from_db()
        self.acc3.refresh_from_db()
        self.assertEqual(self.acc2.financial_institution, fi_afg_1)
        self.assertEqual(self.acc2.financial_institution.country, self.afg)
        self.assertEqual(self.acc3.financial_institution, fi_afg_1)

        fi_afg_2 = FinancialInstitution.objects.get(name="bank3", swift_code="667", type="bank")
        self.acc4.refresh_from_db()
        self.assertEqual(self.acc4.financial_institution, fi_afg_2)
        self.assertEqual(self.acc4.financial_institution.country, self.afg)

        fi_afg_3 = FinancialInstitution.objects.get(name="bank4", swift_code="668", type="bank")
        self.acc5.refresh_from_db()
        self.acc6.refresh_from_db()
        self.assertEqual(self.acc5.financial_institution, fi_afg_3)
        self.assertEqual(self.acc5.financial_institution.country, self.afg)
        self.assertEqual(self.acc6.financial_institution, fi_afg_3)

        fi_afg_4 = FinancialInstitution.objects.get(name="bank5", swift_code="669", type="bank")
        self.acc7.refresh_from_db()
        self.assertEqual(self.acc7.financial_institution, fi_afg_4)
        self.assertEqual(self.acc7.financial_institution.country, self.afg)
