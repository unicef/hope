import base64
import contextlib
from pathlib import Path
from typing import Iterator

import pytest
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from extras.test_utils.factories import RoleFactory, UserFactory
from extras.test_utils.factories.api import APITokenFactory
from extras.test_utils.factories.core import BeneficiaryGroupFactory, BusinessAreaFactory, DataCollectingTypeFactory
from extras.test_utils.factories.geo import CountryFactory
from extras.test_utils.factories.household import DocumentTypeFactory
from extras.test_utils.factories.payment import FinancialInstitutionFactory
from extras.test_utils.factories.program import ProgramFactory
from extras.test_utils.factories.registration_data import RegistrationDataImportFactory
from hope.apps.core.utils import IDENTIFICATION_TYPE_TO_KEY_MAPPING
from hope.apps.household.const import IDENTIFICATION_TYPE_BIRTH_CERTIFICATE
from hope.models import (
    APIToken,
    BusinessArea,
    Country,
    DocumentType,
    FinancialInstitution,
    Program,
    RegistrationDataImport,
    User,
)
from hope.models.utils import Grant


@contextlib.contextmanager
def token_grant_permission(token: APIToken, grant: Grant) -> Iterator:
    old = token.grants
    token.grants += [grant.name]
    token.save()
    yield
    token.grants = old
    token.save()


@pytest.fixture
def imported_by_user(db) -> User:
    return UserFactory()


@pytest.fixture
def business_area(db) -> BusinessArea:
    return BusinessAreaFactory(name="Afghanistan")


@pytest.fixture
def api_user(db) -> User:
    return UserFactory()


@pytest.fixture
def api_token(api_user: User, business_area: BusinessArea) -> APIToken:
    grants = [Grant.API_RDI_CREATE.name, Grant.API_RDI_UPLOAD.name]
    role = RoleFactory(name="api-role", permissions=grants)
    api_user.role_assignments.create(role=role, business_area=business_area)
    token = APITokenFactory(user=api_user, grants=grants)
    token.valid_for.set([business_area])
    return token


@pytest.fixture
def token_api_client(api_token: APIToken) -> APIClient:
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION="Token " + api_token.key)
    return client


@pytest.fixture
def afghanistan_country(db) -> Country:
    return CountryFactory(name="Afghanistan", short_name="Afghanistan", iso_code2="AF", iso_code3="AFG", iso_num="0004")


@pytest.fixture
def base64_image() -> str:
    image = Path(__file__).parent / "logo.png"
    return base64.b64encode(image.read_bytes()).decode("utf-8")


@pytest.fixture
def birth_certificate_doc_type(db) -> DocumentType:
    return DocumentTypeFactory(
        key=IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_BIRTH_CERTIFICATE],
        label="--",
    )


@pytest.fixture
def program(business_area: BusinessArea) -> Program:
    return ProgramFactory(
        status=Program.DRAFT,
        business_area=business_area,
        biometric_deduplication_enabled=True,
    )


@pytest.fixture
def upload_url(business_area: BusinessArea) -> str:
    return reverse("api:rdi-upload", args=[business_area.slug])


@pytest.fixture
def program_create_payload(db) -> dict:
    dct = DataCollectingTypeFactory()
    bg = BeneficiaryGroupFactory()
    return {
        "name": "Program #1",
        "start_date": "2022-09-27",
        "end_date": "2022-09-27",
        "budget": "10000",
        "frequency_of_payments": "ONE_OFF",
        "sector": "CHILD_PROTECTION",
        "cash_plus": True,
        "population_goal": 101,
        "data_collecting_type": dct.id,
        "beneficiary_group": str(bg.id),
    }


@pytest.fixture
def program_create_url(business_area: BusinessArea) -> str:
    return reverse("api:program-create", args=[business_area.slug])


@pytest.fixture
def program_list_url(business_area: BusinessArea) -> str:
    return reverse("api:program-list", args=[business_area.slug])


@pytest.fixture
def program_global_list_url() -> str:
    return reverse("api:program-global-list")


@pytest.fixture
def ba_scoped_programs(business_area: BusinessArea) -> tuple[Program, Program]:
    program1 = ProgramFactory(
        budget=10000,
        start_date="2022-01-12",
        end_date="2022-09-12",
        business_area=business_area,
        population_goal=200,
        status=Program.ACTIVE,
    )
    program2 = ProgramFactory(
        budget=200,
        start_date="2022-01-10",
        end_date="2022-09-10",
        business_area=business_area,
        population_goal=200,
        status=Program.DRAFT,
    )
    # program from another BA — should NOT appear
    ProgramFactory(business_area=BusinessAreaFactory(name="Ukraine"), status=Program.ACTIVE)
    program1.refresh_from_db()
    program2.refresh_from_db()
    return program1, program2


@pytest.fixture
def three_programs(business_area: BusinessArea) -> tuple[Program, Program, Program]:
    ba2 = BusinessAreaFactory(name="Ukraine")
    program_active = ProgramFactory(
        budget=10000,
        start_date="2022-01-12",
        end_date="2022-09-12",
        business_area=business_area,
        population_goal=200,
        status=Program.ACTIVE,
    )
    program_draft = ProgramFactory(
        budget=200,
        start_date="2022-01-10",
        end_date="2022-09-10",
        business_area=business_area,
        population_goal=200,
        status=Program.DRAFT,
    )
    program_other_ba = ProgramFactory(
        budget=200,
        start_date="2022-01-10",
        end_date="2022-09-10",
        business_area=ba2,
        population_goal=400,
        status=Program.ACTIVE,
    )
    program_active.refresh_from_db()
    program_draft.refresh_from_db()
    program_other_ba.refresh_from_db()
    return program_active, program_draft, program_other_ba


@pytest.fixture
def rdi_loading(business_area: BusinessArea, program: Program) -> RegistrationDataImport:
    return RegistrationDataImportFactory(
        business_area=business_area,
        program=program,
        status=RegistrationDataImport.LOADING,
        number_of_individuals=0,
        number_of_households=0,
    )


@pytest.fixture
def financial_institution(db) -> FinancialInstitution:
    return FinancialInstitutionFactory(name="mbank", type=FinancialInstitution.FinancialInstitutionType.BANK)


@pytest.fixture
def bank_account_type(db) -> None:
    from hope.models import AccountType

    AccountType.objects.get_or_create(key="bank", defaults={"label": "Bank", "unique_fields": ["number"]})


@pytest.fixture
def user_business_area(api_token: APIToken) -> BusinessArea:
    return api_token.valid_for.first()


@pytest.fixture
def generic_bank(db) -> FinancialInstitution:
    fi, _ = FinancialInstitution.objects.get_or_create(
        name="Generic Bank", defaults={"type": FinancialInstitution.FinancialInstitutionType.BANK}
    )
    return fi
