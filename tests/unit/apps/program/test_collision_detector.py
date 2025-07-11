import pytest

from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.geo.models import Country
from hct_mis_api.apps.household.fixtures import create_household_and_individuals
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program

pytestmark = pytest.mark.django_db(transaction=True)
@pytest.fixture()
def poland() -> Country:
    return Country.objects.create(name="Poland", iso_code2="PL", iso_code3="POL", iso_num="616")


@pytest.fixture()
def germany() -> Country:
    return Country.objects.create(name="Germany", iso_code2="DE", iso_code3="DEU", iso_num="276")

@pytest.fixture()
def program(poland: Country, germany: Country) -> Program:
    business_area = create_afghanistan()
    business_area.countries.add(poland, germany)

    program = ProgramFactory(name="Test Program for Household", status=Program.ACTIVE, business_area=business_area)
    return program

@pytest.fixture
def original_household():
    household, individuals = create_household_and_individuals(
        household_data={
            "unicef_id": "HH-20-0000.0002",
            "rdi_merge_status": "MERGED",
            "business_area": program.business_area,
            "program": program,
            "admin1": admin1,
            "size": 954,
            "returnee": True,
        },
        individuals_data=[
            {
                "unicef_id": "IND-00-0000.0011",
                "rdi_merge_status": "MERGED",
                "business_area": program.business_area,
                "sex": MALE,
                "phone_no": "+48555444333",
            },
        ],
    )

    ind = individuals[0]

    ind.flex_fields = {"muac": 0}
    ind.save()
    household.flex_fields = {"eggs": "OLD"}
    household.save()
    return ind