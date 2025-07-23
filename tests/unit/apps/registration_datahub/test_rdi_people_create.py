from datetime import date
from io import BytesIO
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management import call_command
from django.forms import model_to_dict
from django.test import TestCase

import pytest
from django_countries.fields import Country
from extras.test_utils.factories.account import PartnerFactory
from extras.test_utils.factories.core import (
    create_afghanistan,
    create_pdu_flexible_attribute,
)
from extras.test_utils.factories.payment import generate_delivery_mechanisms
from extras.test_utils.factories.program import ProgramFactory
from extras.test_utils.factories.registration_data import RegistrationDataImportFactory

from hct_mis_api.apps.core.models import DataCollectingType, PeriodicFieldData
from hct_mis_api.apps.geo.fixtures import AreaFactory
from hct_mis_api.apps.geo.models import Country as GeoCountry
from hct_mis_api.apps.household.models import (
    ROLE_ALTERNATE,
    ROLE_PRIMARY,
    PendingHousehold,
    PendingIndividual,
)
from hct_mis_api.apps.payment.models import PendingAccount
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.registration_data.models import ImportData
from hct_mis_api.apps.utils.elasticsearch_utils import rebuild_search_index
from hct_mis_api.apps.utils.models import MergeStatusModel

pytestmark = pytest.mark.usefixtures("django_elasticsearch_setup")


@pytest.mark.elasticsearch
class TestRdiXlsxPeople(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        call_command("init-geo-fixtures")
        PartnerFactory(name="UNHCR")
        content = Path(f"{settings.TESTS_ROOT}/apps/registration_datahub/test_file/rdi_people_test.xlsx").read_bytes()
        file = File(BytesIO(content), name="rdi_people_test.xlsx")
        cls.business_area = create_afghanistan()
        parent = AreaFactory(p_code="AF11", name="Name")
        AreaFactory(p_code="AF1115", name="Name2", parent=parent)

        from hct_mis_api.apps.registration_datahub.tasks.rdi_xlsx_people_create import (
            RdiXlsxPeopleCreateTask,
        )

        cls.RdiXlsxPeopleCreateTask = RdiXlsxPeopleCreateTask
        cls.import_data = ImportData.objects.create(
            file=file,
            number_of_households=0,
            number_of_individuals=4,
        )
        cls.program = ProgramFactory(status=Program.ACTIVE, data_collecting_type__type=DataCollectingType.Type.SOCIAL)
        cls.registration_data_import = RegistrationDataImportFactory(
            business_area=cls.business_area, program=cls.program, import_data=cls.import_data
        )
        cls.string_attribute = create_pdu_flexible_attribute(
            label="PDU String Attribute",
            subtype=PeriodicFieldData.STRING,
            number_of_rounds=1,
            rounds_names=["May"],
            program=cls.program,
        )
        generate_delivery_mechanisms()

        rebuild_search_index()

    def test_execute(self) -> None:
        self.RdiXlsxPeopleCreateTask().execute(
            self.registration_data_import.id, self.import_data.id, self.business_area.id, self.program.id
        )
        households_count = PendingHousehold.objects.count()
        individuals_count = PendingIndividual.objects.count()

        self.assertEqual(4, households_count)
        self.assertEqual(4, individuals_count)

        individual_data = {
            "full_name": "Derek Index4",
            "given_name": "Derek",
            "middle_name": "",
            "family_name": "Index4",
            "sex": "MALE",
            "relationship": "HEAD",
            "birth_date": date(2000, 8, 22),
            "marital_status": "MARRIED",
        }
        matching_individuals = PendingIndividual.objects.filter(**individual_data)

        self.assertEqual(matching_individuals.count(), 1)
        individual = matching_individuals.first()
        self.assertEqual(
            individual.flex_fields,
            {"pdu_string_attribute": {"1": {"value": "Test PDU Value", "collection_date": "2020-01-08"}}},
        )
        household_data = {
            "residence_status": "REFUGEE",
            "country": GeoCountry.objects.get(iso_code2=Country("IM").code).id,
            "zip_code": "002",
            "flex_fields": {},
        }
        household = matching_individuals.first().pending_household
        household_obj_data = model_to_dict(household, ("residence_status", "country", "zip_code", "flex_fields"))
        self.assertEqual(household_obj_data, household_data)

        roles = household.individuals_and_roles(manager="pending_objects").all()
        self.assertEqual(roles.count(), 2)
        primary_role = roles.filter(role=ROLE_PRIMARY).first()
        self.assertEqual(primary_role.role, "PRIMARY")
        self.assertEqual(primary_role.individual.full_name, "Derek Index4")
        alternate_role = roles.filter(role=ROLE_ALTERNATE).first()
        self.assertEqual(alternate_role.role, "ALTERNATE")
        self.assertEqual(alternate_role.individual.full_name, "Collector ForJanIndex_3")

        worker_individuals = PendingIndividual.objects.filter(relationship="NON_BENEFICIARY")
        self.assertEqual(worker_individuals.count(), 2)

        self.assertEqual(PendingAccount.objects.count(), 3)
        dmd1 = PendingAccount.objects.get(individual__full_name="Collector ForJanIndex_3")
        dmd2 = PendingAccount.objects.get(individual__full_name="WorkerCollector ForDerekIndex_4")
        dmd3 = PendingAccount.objects.get(individual__full_name="Jan    Index3")
        self.assertEqual(dmd1.rdi_merge_status, MergeStatusModel.PENDING)
        self.assertEqual(dmd2.rdi_merge_status, MergeStatusModel.PENDING)
        self.assertEqual(dmd3.rdi_merge_status, MergeStatusModel.PENDING)
        self.assertEqual(
            dmd1.data,
            {"card_number": "164260858", "card_expiry_date": "1995-06-03T00:00:00"},
        )
        self.assertEqual(
            dmd2.data,
            {
                "card_number": "1975549730",
                "card_expiry_date": "2022-02-17T00:00:00",
                "name_of_cardholder": "Name1",
            },
        )
        self.assertEqual(
            dmd3.data,
            {
                "card_number": "870567340",
                "card_expiry_date": "2016-06-27T00:00:00",
                "name_of_cardholder": "Name2",
            },
        )
