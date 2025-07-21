import sys
from io import StringIO
from typing import Any

from django.conf import settings
from django.test import TestCase

import pytest

from tests.extras.test_utils.factories.core import create_afghanistan
from tests.extras.test_utils.factories.household import create_household_and_individuals
from tests.extras.test_utils.factories.payment import generate_delivery_mechanisms
from hct_mis_api.apps.payment.models import Account, AccountType
from tests.extras.test_utils.factories.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.utils.elasticsearch_utils import rebuild_search_index
from hct_mis_api.one_time_scripts.drc_update_script import drc_update_script


class Capturing(list):
    def __enter__(self) -> "Capturing":
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self

    def __exit__(self, *args: Any) -> None:
        self.extend(self._stringio.getvalue().splitlines())
        del self._stringio  # free up some memory
        sys.stdout = self._stdout


@pytest.mark.elasticsearch
class TestSouthSudanUpdateScript(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        generate_delivery_mechanisms()
        cls.account_type_mobile = AccountType.objects.get(key="mobile")
        business_area = create_afghanistan()
        program = ProgramFactory(name="Test Program for Household", status=Program.ACTIVE, business_area=business_area)
        cls.program = program

        business_area = create_afghanistan()
        cls.business_area = business_area

        household, individuals = create_household_and_individuals(
            household_data={
                "business_area": business_area,
                "program_id": program.id,
            },
            individuals_data=[
                {
                    "business_area": business_area,
                    "program_id": program.id,
                },
            ],
        )
        individual = individuals[0]
        individual.unicef_id = "IND-0"
        individual.save()
        individual.refresh_from_db()
        cls.individual = individual

        household2, individuals2 = create_household_and_individuals(
            household_data={
                "business_area": business_area,
                "program_id": program.id,
            },
            individuals_data=[
                {
                    "business_area": business_area,
                    "program_id": program.id,
                    "phone_no": "+48602102373",
                    "payment_delivery_phone_no": "+48602102373",
                },
            ],
        )

        individual2 = individuals2[0]
        individual2.unicef_id = "IND-1"
        individual2.save()
        individual2.refresh_from_db()
        cls.individual2 = individual2
        cls.deliver_mechanism_data2 = Account.objects.create(
            data={
                "service_provider_code": "OLD_CODE",
                "provider": "OLD_PROVIDER",
                "delivery_phone_number": "+48602102373",
            },
            individual=individual2,
            rdi_merge_status=Account.MERGED,
            account_type=cls.account_type_mobile,
        )

        household3, individuals3 = create_household_and_individuals(
            household_data={
                "business_area": business_area,
                "program_id": program.id,
            },
            individuals_data=[
                {
                    "business_area": business_area,
                    "program_id": program.id,
                    "phone_no": "+48602102373",
                    "payment_delivery_phone_no": "+48602102373",
                },
            ],
        )

        individual3 = individuals3[0]
        individual3.unicef_id = "IND-2"
        individual3.save()
        individual3.refresh_from_db()
        cls.individual3 = individual3
        cls.deliver_mechanism_data3 = Account.objects.create(
            data={
                "service_provider_code": "OLD_CODE",
                "provider": "OLD_PROVIDER",
                "delivery_phone_number": "+48602102373",
            },
            individual=individual3,
            rdi_merge_status=Account.MERGED,
            account_type=cls.account_type_mobile,
        )

        household4, individuals4 = create_household_and_individuals(
            household_data={
                "business_area": business_area,
                "program_id": program.id,
            },
            individuals_data=[
                {
                    "business_area": business_area,
                    "program_id": program.id,
                    "phone_no": "+48602102373",
                    "payment_delivery_phone_no": "+48602102373",
                },
            ],
        )

        individual4 = individuals4[0]
        individual4.unicef_id = "IND-3"
        individual4.save()
        individual4.refresh_from_db()
        cls.individual4 = individual4

        rebuild_search_index()

    def test_drc_script(self) -> None:
        with Capturing() as output:
            drc_update_script(f"{settings.TESTS_ROOT}/one_time_scripts/files/updates_DRC_test.xlsx", self.program.id, 1)
        expected_output = [
            "Validating row 0 to 1 Indivduals",
            "Validating row 1 to 2 Indivduals",
            "Validating row 2 to 3 Indivduals",
            "Validating row 3 to 4 Indivduals",
            "Validation successful",
            "Updating row 0 to 1 Individuals",
            "Updating row 1 to 2 Individuals",
            "Updating row 2 to 3 Individuals",
            "Updating row 3 to 4 Individuals",
            "Deduplicating individuals Elasticsearch",
            "Deduplicating documents",
            "Update successful",
        ]
        self.assertEqual(output, expected_output)
        self.individual.refresh_from_db()
        self.individual2.refresh_from_db()
        self.individual3.refresh_from_db()
        self.individual4.refresh_from_db()
        individual = self.individual
        individual2 = self.individual2
        individual3 = self.individual3
        individual4 = self.individual4
        deliver_mechanism_data2 = self.deliver_mechanism_data2
        deliver_mechanism_data3 = self.deliver_mechanism_data3
        self.assertEqual(str(individual.phone_no), "+243837611111")
        self.assertEqual(str(individual.payment_delivery_phone_no), "+243837611111")
        self.assertEqual(individual.accounts.count(), 1)
        deliver_mechanism_data = individual.accounts.first()
        self.assertEqual(
            deliver_mechanism_data.data,
            {
                "service_provider_code": "CD-VODACASH",
                "provider": "Vodacash",
            },
        )
        self.assertEqual(str(individual2.phone_no), "+243836122222")
        self.assertEqual(str(individual2.payment_delivery_phone_no), "+243836122222")
        self.assertEqual(individual2.accounts.count(), 1)
        deliver_mechanism_data2.refresh_from_db()
        self.assertEqual(
            deliver_mechanism_data2.data,
            {
                "service_provider_code": "CD-VODACASH",
                "provider": "Vodacash",
                "delivery_phone_number": "+48602102373",
            },
        )
        self.assertEqual(str(individual3.phone_no), "+243831733333")
        self.assertEqual(individual3.accounts.count(), 1)
        deliver_mechanism_data3.refresh_from_db()
        self.assertEqual(
            deliver_mechanism_data3.data,
            {
                "service_provider_code": "OLD_CODE",
                "provider": "OLD_PROVIDER",
                "delivery_phone_number": "+48602102373",
            },
        )

        self.assertEqual(str(individual4.phone_no), "+243831733333")
        self.assertEqual(individual4.accounts.count(), 0)
