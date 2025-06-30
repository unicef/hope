from typing import Any

from django.conf import settings
from django.test import TestCase

import pytest
from constance.test import override_config
from strategy_field.utils import fqn

from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.utils import IDENTIFICATION_TYPE_TO_KEY_MAPPING
from hct_mis_api.apps.geo import models as geo_models
from hct_mis_api.apps.grievance.models import GrievanceTicket
from hct_mis_api.apps.household.fixtures import (
    DocumentFactory,
    DocumentTypeFactory,
    create_household_and_individuals,
)
from hct_mis_api.apps.household.models import (
    IDENTIFICATION_TYPE_NATIONAL_ID,
    Individual,
)
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.registration_data.fixtures import RegistrationDataImportFactory
from hct_mis_api.apps.sanction_list.models import SanctionList
from hct_mis_api.apps.sanction_list.strategies.un import UNSanctionList
from hct_mis_api.apps.sanction_list.tasks.check_against_sanction_list_pre_merge import (
    check_against_sanction_list_pre_merge,
)
from hct_mis_api.apps.sanction_list.tasks.load_xml import LoadSanctionListXMLTask
from hct_mis_api.apps.utils.elasticsearch_utils import rebuild_search_index

pytestmark = pytest.mark.usefixtures("django_elasticsearch_setup")


@pytest.fixture()
def sanction_list(db: Any) -> "SanctionList":
    from test_utils.factories.sanction_list import SanctionListFactory

    return SanctionListFactory(strategy=fqn(UNSanctionList))


@override_config(SANCTION_LIST_MATCH_SCORE=3.5)
@pytest.mark.elasticsearch
class TestSanctionListPreMerge(TestCase):
    databases = "__all__"
    fixtures = (f"{settings.PROJECT_ROOT}/apps/geo/fixtures/data.json",)

    TEST_FILES_PATH = f"{settings.TESTS_ROOT}/apps/sanction_list/test_files"

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        from test_utils.factories.sanction_list import SanctionListFactory

        full_sanction_list_path = f"{cls.TEST_FILES_PATH}/full_sanction_list.xml"
        sanction_list = SanctionListFactory()
        sanction_list.save()
        task = LoadSanctionListXMLTask(sanction_list)
        task.load_from_file(full_sanction_list_path)

        cls.business_area = BusinessArea.objects.create(
            code="0060",
            name="Afghanistan",
            long_name="THE ISLAMIC REPUBLIC OF AFGHANISTAN",
            region_code="64",
            region_name="SAR",
            has_data_sharing_agreement=True,
        )
        cls.program = ProgramFactory(business_area=cls.business_area)
        cls.program.sanction_lists.add(sanction_list)
        cls.registration_data_import = RegistrationDataImportFactory(
            business_area=cls.business_area, program=cls.program
        )
        cls.household, cls.individuals = create_household_and_individuals(
            household_data={
                "registration_data_import": cls.registration_data_import,
                "program": cls.program,
            },
            individuals_data=[
                {
                    # DUPLICATE
                    "given_name": "Ri",
                    "full_name": "Ri Won Ho",
                    "middle_name": "",
                    "family_name": "Won Ho",
                    "birth_date": "1964-07-17",
                },
                {
                    "given_name": "Choo",
                    "full_name": "Choo Ryoong",
                    "middle_name": "",
                    "family_name": "Ryong",
                    "birth_date": "1960-04-04",
                },
                {
                    "given_name": "Tescik",
                    "full_name": "Tescik Testowski",
                    "middle_name": "",
                    "family_name": "Testowski",
                    "birth_date": "1996-12-12",
                },
                {
                    # DUPLICATE
                    "given_name": "Tessta",
                    "full_name": "Tessta Testowski",
                    "middle_name": "",
                    "family_name": "Testowski",
                    "birth_date": "1997-07-07",
                },
                {
                    # DUPLICATE
                    "given_name": "Test",
                    "full_name": "Test Testowski",
                    "middle_name": "",
                    "family_name": "Testowski",
                    "birth_date": "1955-09-04",
                },
                {
                    "given_name": "Test",
                    "full_name": "Test Example",
                    "middle_name": "",
                    "family_name": "Example",
                    "birth_date": "1997-08-08",
                },
                {
                    # DUPLICATE
                    "given_name": "Tessta",
                    "full_name": "Tessta Testowski",
                    "middle_name": "",
                    "family_name": "Testowski",
                    "birth_date": "1997-07-07",
                },
                {
                    "given_name": "Abdul",
                    "full_name": "Abdul Afghanistan",
                    "middle_name": "",
                    "family_name": "Afghanistan",
                    "birth_date": "1997-07-07",
                },
            ],
        )

        ind = Individual.objects.get(full_name="Abdul Afghanistan")
        country = geo_models.Country.objects.get(iso_code3="AFG")
        doc_type = DocumentTypeFactory(
            label="National ID",
            key=IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_NATIONAL_ID],
        )
        DocumentFactory(
            document_number="55130",
            individual=ind,
            type=doc_type,
            country=country,
            program=ind.program,
        )
        rebuild_search_index()

    def test_execute(self) -> None:
        check_against_sanction_list_pre_merge(program_id=self.program.id)

        expected = [
            {"full_name": "Abdul Afghanistan", "sanction_list_possible_match": False},
            {"full_name": "Choo Ryoong", "sanction_list_possible_match": False},
            {"full_name": "Ri Won Ho", "sanction_list_possible_match": False},
            {"full_name": "Tescik Testowski", "sanction_list_possible_match": False},
            {"full_name": "Tessta Testowski", "sanction_list_possible_match": False},
            {"full_name": "Tessta Testowski", "sanction_list_possible_match": False},
            {"full_name": "Test Example", "sanction_list_possible_match": False},
            {"full_name": "Test Testowski", "sanction_list_possible_match": False},
        ]

        result = list(Individual.objects.order_by("full_name").values("full_name", "sanction_list_possible_match"))

        self.assertEqual(result, expected)

    def test_create_system_flag_tickets(self) -> None:
        check_against_sanction_list_pre_merge(program_id=self.program.id)
        self.assertEqual(
            GrievanceTicket.objects.filter(category=GrievanceTicket.CATEGORY_SYSTEM_FLAGGING).count(),
            0,
        )
        for grievance_ticket in GrievanceTicket.objects.filter(category=GrievanceTicket.CATEGORY_SYSTEM_FLAGGING):
            self.assertEqual(grievance_ticket.programs.count(), 0)
            self.assertEqual(grievance_ticket.programs.first(), self.program)

        self.household.refresh_from_db()
        for grievance_ticket in GrievanceTicket.objects.filter(category=GrievanceTicket.CATEGORY_SYSTEM_FLAGGING):
            self.assertEqual(grievance_ticket.household_unicef_id, self.household.unicef_id)
