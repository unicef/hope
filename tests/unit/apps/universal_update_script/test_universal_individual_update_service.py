from django.core.files.base import ContentFile

import pytest

from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.geo.models import Area, AreaType, Country
from hct_mis_api.apps.household.fixtures import create_household_and_individuals
from hct_mis_api.apps.household.models import (
    FEMALE,
    MALE,
    Document,
    DocumentType,
    Individual,
)
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.universal_update_script.models import UniversalUpdate
from hct_mis_api.apps.universal_update_script.universal_individual_update_service.universal_individual_update_service import (
    UniversalIndividualUpdateService,
)

pytestmark = pytest.mark.django_db(transaction=True)


@pytest.fixture()
def poland() -> Country:
    return Country.objects.create(name="Poland", iso_code2="PL", iso_code3="POL", iso_num="616")


@pytest.fixture()
def germany() -> Country:
    return Country.objects.create(name="Germany", iso_code2="DE", iso_code3="DEU", iso_num="276")


@pytest.fixture()
def state(poland: Country) -> AreaType:
    return AreaType.objects.create(name="State", country=poland)


@pytest.fixture()
def district(poland: Country, state: AreaType) -> AreaType:
    return AreaType.objects.create(name="District", parent=state, country=poland)


@pytest.fixture()
def admin1(state: AreaType) -> Area:
    return Area.objects.create(name="Kabul", area_type=state, p_code="AF11")


@pytest.fixture()
def admin2(district: AreaType) -> Area:
    return Area.objects.create(name="Kabul1", area_type=district, p_code="AF1115")


@pytest.fixture()
def program(poland: Country, germany: Country) -> Program:
    business_area = create_afghanistan()
    business_area.countries.add(poland, germany)

    program = ProgramFactory(name="Test Program for Household", status=Program.ACTIVE, business_area=business_area)
    return program


@pytest.fixture
def individual(program: Program, admin1: Area, admin2: Area) -> Individual:
    _, individuals = create_household_and_individuals(
        household_data={
            "unicef_id": "HH-20-0000.0002",
            "rdi_merge_status": "MERGED",
            "business_area": program.business_area,
            "program": program,
            "admin1": admin1,
        },
        individuals_data=[
            {
                "unicef_id": "IND-00-0000.0011",
                "rdi_merge_status": "MERGED",
                "business_area": program.business_area,
                "sex": MALE,
            },
        ],
    )
    ind = individuals[0]
    return ind


@pytest.fixture
def document_national_id(individual: Individual, program: Program, poland: Country) -> Document:
    document_type = DocumentType.objects.create(key="national_id", label="National ID")
    return Document.objects.create(
        individual=individual,
        program=program,
        type=document_type,
        document_number="Test 123",
        rdi_merge_status=Document.MERGED,
        country=poland,
    )


class TestUniversalIndividualUpdateService:
    def test_update_individual(
        self, individual: Individual, program: Program, admin1: Area, admin2: Area, document_national_id: Document
    ) -> None:
        """
        This test generates file for individual update
        Then Changes manually individual household document data
        Then runs the update script based on the file generated and checks if data is updated to original

        In this way I'm checking if file is generated correctly and also if service can use the same file to update back
        :param individual:
        :param program:
        :return:
        """
        # save old values
        given_name_old = individual.given_name
        sex_old = individual.sex
        birth_date_old = individual.birth_date
        address_old = individual.household.address
        admin1_old = individual.household.admin1
        document_number_old = document_national_id.document_number
        universal_update = UniversalUpdate(program=program)
        universal_update.unicef_ids = individual.unicef_id
        universal_update.individual_fields = ["given_name", "sex", "birth_date"]
        universal_update.household_fields = ["address", "admin1"]
        universal_update.save()
        universal_update.document_types.add(DocumentType.objects.first())
        service = UniversalIndividualUpdateService(universal_update)
        template_file = service.generate_xlsx_template()
        universal_update.refresh_from_db()
        content = template_file.getvalue()
        universal_update.update_file.save("template.xlsx", ContentFile(content))
        universal_update.save()
        universal_update.refresh_from_db()
        expected_generate_log = "Generating row 0 to 1\nGenerating Finished\n"
        assert universal_update.saved_logs == expected_generate_log
        # Change the data manually
        individual.given_name = "Test Name"
        individual.sex = FEMALE
        individual.birth_date = "1996-06-21"
        individual.save()
        household = individual.household
        household.address = "Wrocław"
        household.admin1 = None
        household.save()
        document_national_id.document_number = "111"
        document_national_id.save()
        service = UniversalIndividualUpdateService(universal_update)
        universal_update.clear_logs()
        service.execute()
        universal_update.refresh_from_db()
        individual.refresh_from_db()
        document_national_id.refresh_from_db()
        expected_update_log = """Validating row 0 to 1 Indivduals
Validation successful
Updating row 0 to 1 Individuals
Deduplicating individuals Elasticsearch
Deduplicating documents
Update successful
"""
        assert universal_update.saved_logs == expected_update_log
        assert individual.given_name == given_name_old
        assert individual.sex == sex_old
        assert individual.birth_date == birth_date_old
        assert individual.household.address == address_old
        assert individual.household.admin1 == admin1_old
        assert document_national_id.document_number == document_number_old
