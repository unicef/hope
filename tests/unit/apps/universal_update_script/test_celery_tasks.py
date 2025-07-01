import pytest

from apps.payment.models import AccountType
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import FlexibleAttribute
from hct_mis_api.apps.geo.models import Area, AreaType, Country
from hct_mis_api.apps.household.fixtures import create_household_and_individuals
from hct_mis_api.apps.household.models import MALE, Document, DocumentType, Individual
from hct_mis_api.apps.payment.models import Account, DeliveryMechanism
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.universal_update_script.celery_tasks import (
    generate_universal_individual_update_template,
    run_universal_individual_update,
)
from hct_mis_api.apps.universal_update_script.models import UniversalUpdate

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
def delivery_mechanism() -> DeliveryMechanism:
    return DeliveryMechanism.objects.create(name="Mobile Money", code="mobile_money")


@pytest.fixture
def flexible_attribute_individual() -> FlexibleAttribute:
    return FlexibleAttribute.objects.create(
        name="muac",
        type=FlexibleAttribute.INTEGER,
        associated_with=FlexibleAttribute.ASSOCIATED_WITH_INDIVIDUAL,
        label={"English(EN)": "Muac"},
    )


@pytest.fixture
def flexible_attribute_household() -> FlexibleAttribute:
    return FlexibleAttribute.objects.create(
        name="eggs",
        type=FlexibleAttribute.STRING,
        associated_with=FlexibleAttribute.ASSOCIATED_WITH_HOUSEHOLD,
        label={"English(EN)": "Eggs"},
    )


@pytest.fixture
def individual(
    program: Program,
    admin1: Area,
    admin2: Area,
    flexible_attribute_individual: FlexibleAttribute,
    flexible_attribute_household: FlexibleAttribute,
    delivery_mechanism: DeliveryMechanism,
) -> Individual:
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


@pytest.fixture()
def wallet(individual: Individual, delivery_mechanism: DeliveryMechanism) -> Account:
    return Account.objects.create(
        individual=individual,
        data={"phone_number": "1234567890"},
        rdi_merge_status=Account.MERGED,
        account_type=AccountType.objects.create(key="mobile"),
    )


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


@pytest.mark.elasticsearch
class TestUniversalIndividualUpdateCeleryTasks:
    def test_run_universal_individual_update(
        self,
        individual: Individual,
        program: Program,
        admin1: Area,
        admin2: Area,
        document_national_id: Document,
        delivery_mechanism: DeliveryMechanism,
        wallet: Account,
    ) -> None:
        universal_update = UniversalUpdate(program=program)
        universal_update.unicef_ids = individual.unicef_id
        universal_update.individual_fields = ["given_name"]
        universal_update.save()
        generate_universal_individual_update_template(str(universal_update.id))
        assert universal_update.template_file is not None
        universal_update.refresh_from_db()
        universal_update.update_file = universal_update.template_file
        universal_update.save()
        run_universal_individual_update(str(universal_update.id))
