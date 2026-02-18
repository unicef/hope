import datetime

import pytest
from rest_framework.test import APIClient

from extras.test_utils.factories import (
    BusinessAreaFactory,
    DocumentTypeFactory,
    HouseholdFactory,
    IndividualFactory,
    PaymentFactory,
    PaymentPlanFactory,
    PendingDocumentFactory,
    PendingHouseholdFactory,
    PendingIndividualFactory,
    ProgramCycleFactory,
    ProgramFactory,
    RegistrationDataImportFactory,
    UserFactory,
)
from hope.apps.core.utils import IDENTIFICATION_TYPE_TO_KEY_MAPPING
from hope.apps.household.const import HEAD, IDENTIFICATION_TYPE_TAX_ID
from hope.models import Payment, PaymentPlan

pytestmark = pytest.mark.django_db


@pytest.fixture
def user():
    return UserFactory()


@pytest.fixture
def api_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def business_area():
    return BusinessAreaFactory(
        code="0060",
        name="Afghanistan",
        long_name="THE ISLAMIC REPUBLIC OF AFGHANISTAN",
        region_code="64",
        region_name="SAR",
        has_data_sharing_agreement=True,
    )


@pytest.fixture
def program(business_area):
    return ProgramFactory(business_area=business_area)


@pytest.fixture
def payment_plan(business_area, program, user):
    return PaymentPlanFactory(
        business_area=business_area,
        program_cycle=ProgramCycleFactory(program=program),
        created_by=user,
    )


@pytest.fixture
def tax_document_type():
    return DocumentTypeFactory(key=IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_TAX_ID])


@pytest.fixture
def merged_household_context(business_area, program):
    household = HouseholdFactory(business_area=business_area, program=program, size=1)
    individual = IndividualFactory(household=household, program=program, business_area=business_area, relationship=HEAD)
    household.head_of_household = individual
    household.save(update_fields=["head_of_household"])
    return {"household": household, "individual": individual}


@pytest.fixture
def pending_household_context(business_area, program):
    rdi = RegistrationDataImportFactory(business_area=business_area, program=program)
    pending_household = PendingHouseholdFactory(
        registration_data_import=rdi, business_area=business_area, program=program
    )
    pending_individual = PendingIndividualFactory(
        household=pending_household, relationship=HEAD, business_area=business_area, program=program
    )
    pending_household.head_of_household = pending_individual
    pending_household.save(update_fields=["head_of_household"])
    return {"household": pending_household, "individual": pending_individual}


def test_filtering_business_area_code_with_tax_id(
    api_client, business_area, merged_household_context, tax_document_type
) -> None:
    individual = merged_household_context["individual"]
    document = PendingDocumentFactory(individual=individual, type=tax_document_type)
    tax_id = document.document_number

    response_ok = api_client.get(f"/api/hh-status?tax_id={tax_id}&business_area_code={business_area.code}")
    assert response_ok.status_code == 200

    response_nok = api_client.get(f"/api/hh-status?tax_id={tax_id}&business_area_code=non-existent")
    assert response_nok.status_code == 404


def test_filtering_business_area_code_with_detail_id(api_client, business_area, pending_household_context) -> None:
    pending_household = pending_household_context["household"]
    pending_household.detail_id = "HOPE-2022530111222"
    pending_household.save(update_fields=["detail_id"])

    detail_id = pending_household.detail_id

    response_ok = api_client.get(f"/api/hh-status?detail_id={detail_id}&business_area_code={business_area.code}")
    assert response_ok.status_code == 200

    response_nok = api_client.get(f"/api/hh-status?detail_id={detail_id}&business_area_code=non-existent")
    assert response_nok.status_code == 404


def test_getting_non_existent_individual(api_client) -> None:
    response = api_client.get("/api/hh-status?tax_id=non-existent")
    assert response.status_code == 404
    assert response.json()["detail"] == "Document with given tax_id: non-existent not found"


def test_getting_individual_with_status_imported(api_client, pending_household_context, tax_document_type) -> None:
    pending_household = pending_household_context["household"]
    pending_individual = pending_household_context["individual"]

    pending_document = PendingDocumentFactory(individual=pending_individual, type=tax_document_type)
    tax_id = pending_document.document_number

    response = api_client.get(f"/api/hh-status?tax_id={tax_id}")
    assert response.status_code == 200
    data = response.json()
    info = data["info"]
    assert info["status"] == "imported"
    assert info["date"] == pending_household.updated_at.isoformat().replace("+00:00", "Z")

    individual = info["individual"]
    assert individual is not None
    assert individual["relationship"] == HEAD
    assert individual["role"] is None
    assert individual["tax_id"] == tax_id


def test_getting_individual_with_status_merged_to_population(
    api_client,
    merged_household_context,
    tax_document_type,
) -> None:
    household = merged_household_context["household"]
    individual = merged_household_context["individual"]
    document = PendingDocumentFactory(individual=individual, type=tax_document_type)
    tax_id = document.document_number

    response = api_client.get(f"/api/hh-status?tax_id={tax_id}")
    assert response.status_code == 200
    data = response.json()
    info = data["info"]
    assert info["status"] == "merged to population"
    assert info["date"] == household.created_at.isoformat().replace("+00:00", "Z")


def test_getting_individual_with_status_targeted(
    api_client,
    merged_household_context,
    tax_document_type,
    payment_plan,
) -> None:
    household = merged_household_context["household"]
    individual = merged_household_context["individual"]
    document = PendingDocumentFactory(individual=individual, type=tax_document_type)
    tax_id = document.document_number
    PaymentFactory(
        parent=payment_plan,
        household=household,
        delivered_quantity=None,
    )

    response = api_client.get(f"/api/hh-status?tax_id={tax_id}")
    assert response.status_code == 200
    data = response.json()
    info = data["info"]
    assert info["status"] == "merged to population"
    assert info["date"] == household.created_at.isoformat().replace("+00:00", "Z")


def test_getting_individual_with_status_sent_to_cash_assist(
    api_client,
    merged_household_context,
    tax_document_type,
    business_area,
    program,
    user,
) -> None:
    household = merged_household_context["household"]
    individual = merged_household_context["individual"]
    document = PendingDocumentFactory(individual=individual, type=tax_document_type)
    tax_id = document.document_number
    payment_plan = PaymentPlanFactory(
        business_area=business_area,
        program_cycle=ProgramCycleFactory(program=program),
        created_by=user,
        status=PaymentPlan.Status.TP_LOCKED,
    )
    PaymentFactory(
        parent=payment_plan,
        household=household,
        status=Payment.STATUS_PENDING,
        delivered_quantity=999,
    )

    response = api_client.get(f"/api/hh-status?tax_id={tax_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["info"] is not None
    info = data["info"]
    assert info["status"] == "paid"


def test_getting_individual_with_status_paid(
    api_client,
    merged_household_context,
    tax_document_type,
) -> None:
    household = merged_household_context["household"]
    individual = merged_household_context["individual"]
    document = PendingDocumentFactory(individual=individual, type=tax_document_type)
    tax_id = document.document_number
    payment = PaymentFactory(
        household=household,
        currency="PLN",
        delivery_date=datetime.date.today(),
        delivered_quantity=1,
    )

    response = api_client.get(f"/api/hh-status?tax_id={tax_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["info"] is not None
    info = data["info"]
    assert info["status"] == "paid"
    assert datetime.datetime.fromisoformat(info["date"].replace("Z", "")).date() == payment.delivery_date


def test_getting_non_existent_household(api_client) -> None:
    response = api_client.get("/api/hh-status?detail_id=non-existent")
    assert response.status_code == 404
    assert response.json()["detail"] == "Household with given detail_id: non-existent not found"


def test_getting_household_with_status_imported(api_client, pending_household_context) -> None:
    pending_household = pending_household_context["household"]
    pending_household.detail_id = "HOPE-2022530111222"
    pending_household.save(update_fields=["detail_id"])

    detail_id = pending_household.detail_id

    response = api_client.get(f"/api/hh-status?detail_id={detail_id}")
    assert response.status_code == 200
    data = response.json()
    info = data["info"]
    assert info["status"] == "imported"
    assert info["date"] == pending_household.updated_at.isoformat().replace("+00:00", "Z")
    assert "individual" not in info


def test_getting_household_with_status_paid(api_client, merged_household_context) -> None:
    detail_id = "HOPE-2022530111222"
    household = merged_household_context["household"]
    household.detail_id = detail_id
    household.save(update_fields=["detail_id"])
    individual = merged_household_context["individual"]
    payment = PaymentFactory(
        household=household,
        delivered_quantity=1000,
        collector=individual,
        delivery_date=datetime.date.today(),
    )
    response = api_client.get(f"/api/hh-status?detail_id={detail_id}")
    assert response.status_code == 200
    data = response.json()
    info = data["info"]
    assert info["status"] == "paid"
    assert datetime.datetime.fromisoformat(info["date"].replace("Z", "")).date() == payment.delivery_date
    assert "individual" not in info


@pytest.mark.parametrize(
    "url",
    [
        "/api/hh-status?detail_id=xxx&tax_id=yyy",
        "/api/hh-status",
    ],
)
def test_query_params_validation(api_client, url) -> None:
    response = api_client.get(url)
    assert response.status_code == 400


def test_pending_households_count_gt_1(api_client, business_area, program) -> None:
    detail_id = "123"
    PendingHouseholdFactory(detail_id=detail_id, business_area=business_area, program=program)
    PendingHouseholdFactory(detail_id=detail_id, business_area=business_area, program=program)

    response = api_client.get(f"/api/hh-status?detail_id={detail_id}")
    assert response.status_code == 400


def test_merged_households_count_gt_1(api_client, business_area, program) -> None:
    detail_id = "123"
    HouseholdFactory(detail_id=detail_id, business_area=business_area, program=program)
    HouseholdFactory(detail_id=detail_id, business_area=business_area, program=program)

    response = api_client.get(f"/api/hh-status?detail_id={detail_id}")
    assert response.status_code == 400


def test_documents_count_gt_1(api_client, merged_household_context, tax_document_type) -> None:
    individual = merged_household_context["individual"]
    PendingDocumentFactory(individual=individual, type=tax_document_type, document_number="123")
    PendingDocumentFactory(individual=individual, type=tax_document_type, document_number="123")

    response = api_client.get("/api/hh-status?tax_id=123")
    assert response.status_code == 400
