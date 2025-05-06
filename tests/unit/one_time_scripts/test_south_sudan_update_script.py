import datetime
import sys
from io import StringIO
from typing import Any

from django.conf import settings
from django.test import TestCase

from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.geo.models import Area, AreaType, Country
from hct_mis_api.apps.household.fixtures import create_household_and_individuals
from hct_mis_api.apps.household.models import MALE, Document, DocumentType
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.utils.elasticsearch_utils import rebuild_search_index
from hct_mis_api.one_time_scripts.south_sudan_update_script import (
    south_sudan_update_script,
)


class Capturing(list):
    def __enter__(self) -> "Capturing":
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self

    def __exit__(self, *args: Any) -> None:
        self.extend(self._stringio.getvalue().splitlines())
        del self._stringio  # free up some memory
        sys.stdout = self._stdout


class TestSouthSudanUpdateScript(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
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

        household2, individuals2 = create_household_and_individuals(
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

        individual2 = individuals2[0]
        individual2.unicef_id = "IND-1"
        individual2.save()
        individual2.refresh_from_db()
        cls.individual2 = individual2
        rebuild_search_index()

    def test_south_sudan_update_script(self) -> None:
        poland = Country.objects.create(name="Poland", iso_code2="PL", iso_code3="POL", iso_num="616")
        germany = Country.objects.create(name="Germany", iso_code2="DE", iso_code3="DEU", iso_num="276")
        self.business_area.countries.add(poland, germany)
        state = AreaType.objects.create(name="State", country=poland)
        district = AreaType.objects.create(name="District", parent=state, country=poland)
        Area.objects.create(name="Kabul", area_type=state, p_code="AF11")
        Area.objects.create(name="Kabul1", area_type=district, p_code="AF1115")
        DocumentType.objects.create(label="National ID", key="national_id")
        DocumentType.objects.create(label="Birth Certificate", key="birth_certificate")
        Document.objects.create(
            individual=self.individual,
            type=DocumentType.objects.get(key="national_id"),
            document_number="DIFFERENT",
            country=poland,
            rdi_merge_status="MERGED",
        )
        Document.objects.create(
            individual=self.individual,
            type=DocumentType.objects.get(key="birth_certificate"),
            document_number="OLD",
            country=germany,
            rdi_merge_status="MERGED",
        )
        with Capturing() as output:
            south_sudan_update_script(
                f"{settings.TESTS_ROOT}/one_time_scripts/files/update_script_sudan.xlsx", self.program.id, 1
            )
        expected_output = [
            "Validating row 0 to 1 Indivduals",
            "Validating row 1 to 2 Indivduals",
            "Validation successful",
            "Updating row 0 to 1 Individuals",
            "Updating row 1 to 2 Individuals",
            "Deduplicating individuals Elasticsearch",
            "Deduplicating documents",
            "Update successful",
        ]

        assert output == expected_output
        self.individual.refresh_from_db()
        self.individual2.refresh_from_db()
        individual = self.individual
        individual2 = self.individual2
        household = individual.household
        assert household.admin1.p_code == "AF11"
        assert household.admin2.p_code == "AF1115"
        assert individual.given_name == "Jan"
        assert individual.middle_name == "Roman"
        assert individual.family_name == "Romaniak"
        assert individual.full_name == "Jan Romaniak"
        assert individual.birth_date == datetime.date(1991, 11, 18)
        assert individual.sex == MALE
        assert individual.phone_no == "+48603499023"
        assert individual.flex_fields.get("ss_hw_lot_num_i_f") == 32.0
        assert individual.flex_fields.get("ss_health_facility_name_i_f") == "ed"
        assert individual.flex_fields.get("ss_hw_title_i_f") == "foo"
        assert individual.flex_fields.get("ss_hw_work_id_i_f") == "bar"
        assert individual.flex_fields.get("ss_hw_grade_i_f") == "fooooo"
        assert individual.flex_fields.get("ss_hw_qualifications_i_f") == "baaaar"
        assert individual.flex_fields.get("ss_hw_cadre_i_f") == "aaaaa"
        assert individual.documents.get(type__key="national_id").document_number == "TEST123"
        assert individual.documents.get(type__key="national_id").country.iso_code3 == "POL"

        assert individual.documents.get(type__key="birth_certificate").document_number == "OLD"
        assert individual.documents.get(type__key="birth_certificate").country.iso_code3 == "DEU"
        assert individual2.middle_name == "Testowy"
        assert individual2.family_name == "Tesciak"

    def test_south_sudan_update_script_validation_fails(self) -> None:
        with Capturing() as output:
            south_sudan_update_script(
                f"{settings.TESTS_ROOT}/one_time_scripts/files/update_script_sudan.xlsx", self.program.id, 1
            )
        expected_output = [
            "Validating row 0 to 1 Indivduals",
            "Validating row 1 to 2 Indivduals",
            "Validation failed",
            "Row: 2 - Administrative area admin1 with p_code AF11 not found",
            "Row: 2 - Administrative area admin2 with p_code AF1115 not found",
            "Row: 2 - Country not found for field national_id_country_i_c and value Poland",
            "Row: 2 - Document type not found for field national_id_no_i_c",
        ]
        assert output == expected_output
