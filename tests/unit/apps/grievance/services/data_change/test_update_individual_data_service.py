from datetime import date
from typing import Any
import uuid

from django.core.exceptions import ValidationError
import pytest
from rest_framework.exceptions import ValidationError as DRFValidationError

from extras.test_utils.factories import (
    AccountFactory,
    AccountTypeFactory,
    AreaFactory,
    AreaTypeFactory,
    BusinessAreaFactory,
    CountryFactory,
    DocumentFactory,
    DocumentTypeFactory,
    FinancialInstitutionFactory,
    GrievanceTicketFactory,
    HouseholdFactory,
    IndividualFactory,
    ProgramFactory,
    TicketIndividualDataUpdateDetailsFactory,
    UserFactory,
)
from hope.apps.grievance.models import GrievanceTicket
from hope.apps.grievance.services.data_change.individual_data_update_service import IndividualDataUpdateService
from hope.models import Country, Document

pytestmark = [
    pytest.mark.usefixtures("mock_elasticsearch"),
    pytest.mark.django_db,
]


@pytest.fixture
def update_context() -> dict[str, Any]:
    business_area = BusinessAreaFactory()
    program = ProgramFactory(business_area=business_area)
    country_afg = CountryFactory(iso_code3="AFG")
    user = UserFactory()

    household = HouseholdFactory(program=program, business_area=business_area, create_role=False)
    individual = IndividualFactory(
        household=household,
        business_area=business_area,
        program=program,
        registration_data_import=household.registration_data_import,
    )

    document_type_unique_for_individual = DocumentTypeFactory(unique_for_individual=True, key="unique", label="Unique")
    document_type_not_unique_for_individual = DocumentTypeFactory(
        unique_for_individual=False, key="not_unique", label="Not unique"
    )

    ticket_details = TicketIndividualDataUpdateDetailsFactory(
        individual=individual,
        ticket__business_area=business_area,
        ticket__category=GrievanceTicket.CATEGORY_DATA_CHANGE,
        ticket__issue_type=GrievanceTicket.ISSUE_TYPE_INDIVIDUAL_DATA_CHANGE_DATA_UPDATE,
        individual_data={"documents": []},
    )
    ticket = ticket_details.ticket

    account_type_bank = AccountTypeFactory(key="bank", label="Bank")
    account_type_mobile = AccountTypeFactory(key="mobile", label="Mobile")

    return {
        "business_area": business_area,
        "program": program,
        "country_afg": country_afg,
        "user": user,
        "household": household,
        "individual": individual,
        "document_type_unique": document_type_unique_for_individual,
        "document_type_not_unique": document_type_not_unique_for_individual,
        "ticket": ticket,
        "account_type_bank": account_type_bank,
        "account_type_mobile": account_type_mobile,
    }


def test_add_document_of_same_type_not_unique_per_individual_valid(update_context: dict[str, Any]) -> None:
    DocumentFactory(
        individual=update_context["individual"],
        type=update_context["document_type_not_unique"],
        status=Document.STATUS_VALID,
        program=update_context["program"],
        document_number="123456",
        country=update_context["country_afg"],
    )

    update_context["ticket"].individual_data_update_ticket_details.individual_data["documents"] = [
        {
            "value": {
                "key": update_context["document_type_not_unique"].key,
                "country": "AFG",
                "number": "111111",
            },
            "approve_status": True,
        }
    ]
    update_context["ticket"].individual_data_update_ticket_details.save()

    service = IndividualDataUpdateService(
        update_context["ticket"], update_context["ticket"].individual_data_update_ticket_details
    )
    try:
        service.close(update_context["user"])
    except ValidationError:
        pytest.fail("ValidationError should not be raised")

    assert Document.objects.filter(document_number="111111").count() == 1


def test_add_document_of_same_type_not_unique_per_individual_pending(update_context: dict[str, Any]) -> None:
    DocumentFactory(
        individual=update_context["individual"],
        type=update_context["document_type_not_unique"],
        status=Document.STATUS_PENDING,
        program=update_context["program"],
        document_number="123456",
        country=update_context["country_afg"],
    )

    update_context["ticket"].individual_data_update_ticket_details.individual_data["documents"] = [
        {
            "value": {
                "key": update_context["document_type_not_unique"].key,
                "country": "AFG",
                "number": "111111",
            },
            "approve_status": True,
        }
    ]
    update_context["ticket"].individual_data_update_ticket_details.save()

    service = IndividualDataUpdateService(
        update_context["ticket"], update_context["ticket"].individual_data_update_ticket_details
    )
    try:
        service.close(update_context["user"])
    except ValidationError:
        pytest.fail("ValidationError should not be raised")

    assert Document.objects.filter(document_number="111111").count() == 1


def test_add_document_of_same_type_unique_per_individual_valid(update_context: dict[str, Any]) -> None:
    DocumentFactory(
        individual=update_context["individual"],
        type=update_context["document_type_unique"],
        status=Document.STATUS_VALID,
        program=update_context["program"],
        document_number="123456",
        country=update_context["country_afg"],
    )

    update_context["ticket"].individual_data_update_ticket_details.individual_data["documents"] = [
        {
            "value": {
                "key": update_context["document_type_unique"].key,
                "country": "AFG",
                "number": "111111",
            },
            "approve_status": True,
        }
    ]
    update_context["ticket"].individual_data_update_ticket_details.save()

    service = IndividualDataUpdateService(
        update_context["ticket"], update_context["ticket"].individual_data_update_ticket_details
    )
    with pytest.raises(DRFValidationError) as exc:
        service.close(update_context["user"])
    assert f"Document of type {update_context['document_type_unique']} already exists for this individual" in str(
        exc.value
    )


def test_save_sets_previous_value_for_phone_and_date(update_context: dict[str, Any]) -> None:
    ticket = GrievanceTicketFactory(
        category=GrievanceTicket.CATEGORY_DATA_CHANGE,
        issue_type=GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_ADD_INDIVIDUAL,
        business_area=update_context["business_area"],
    )
    individual = update_context["individual"]
    individual.phone_no = "123456"
    individual.birth_date = date(2020, 1, 2)
    individual.save(update_fields=["phone_no", "birth_date"])

    extras = {
        "issue_type": {
            "individual_data_update_issue_type_extras": {
                "individual": individual,
                "individual_data": {
                    "phone_no": "+999",
                    "birth_date": date(2025, 2, 3),
                },
            }
        }
    }
    service = IndividualDataUpdateService(ticket, extras)
    tickets = service.save()

    ticket_details = tickets[0].individual_data_update_ticket_details
    assert ticket_details.individual_data["phone_no"]["previous_value"] == "123456"
    assert ticket_details.individual_data["birth_date"]["previous_value"] == "2020-01-02"


def test_update_sets_previous_value_for_phone_and_date(update_context: dict[str, Any]) -> None:
    ticket_details = TicketIndividualDataUpdateDetailsFactory(
        individual=update_context["individual"],
        ticket__business_area=update_context["business_area"],
        individual_data={},
    )
    ticket = ticket_details.ticket
    individual = update_context["individual"]
    individual.phone_no = "789"
    individual.birth_date = date(2021, 3, 4)
    individual.save(update_fields=["phone_no", "birth_date"])

    extras = {
        "individual_data_update_issue_type_extras": {
            "individual_data": {
                "phone_no": "+123",
                "birth_date": date(2025, 5, 6),
            }
        }
    }
    service = IndividualDataUpdateService(ticket, extras)
    updated_ticket = service.update()

    details = updated_ticket.individual_data_update_ticket_details
    assert details.individual_data["phone_no"]["previous_value"] == "789"
    assert details.individual_data["birth_date"]["previous_value"] == "2021-03-04"
    assert Document.objects.filter(document_number="111111").count() == 0


def test_add_document_of_same_type_unique_per_individual_pending(update_context: dict[str, Any]) -> None:
    DocumentFactory(
        individual=update_context["individual"],
        type=update_context["document_type_unique"],
        status=Document.STATUS_PENDING,
        program=update_context["program"],
        document_number="123456",
        country=update_context["country_afg"],
    )

    update_context["ticket"].individual_data_update_ticket_details.individual_data["documents"] = [
        {
            "value": {
                "key": update_context["document_type_unique"].key,
                "country": "AFG",
                "number": "111111",
            },
            "approve_status": True,
        }
    ]
    update_context["ticket"].individual_data_update_ticket_details.save()

    service = IndividualDataUpdateService(
        update_context["ticket"], update_context["ticket"].individual_data_update_ticket_details
    )
    try:
        service.close(update_context["user"])
    except ValidationError:
        pytest.fail("ValidationError should not be raised")

    assert Document.objects.filter(document_number="111111").count() == 1


def test_edit_document_of_same_type_unique_per_individual(update_context: dict[str, Any]) -> None:
    DocumentFactory(
        individual=update_context["individual"],
        type=update_context["document_type_unique"],
        status=Document.STATUS_VALID,
        program=update_context["program"],
        document_number="123456",
        country=update_context["country_afg"],
    )
    document_to_edit = DocumentFactory(
        individual=update_context["individual"],
        type=update_context["document_type_not_unique"],
        status=Document.STATUS_VALID,
        program=update_context["program"],
        document_number="111111",
        country=update_context["country_afg"],
    )

    update_context["ticket"].individual_data_update_ticket_details.individual_data["documents_to_edit"] = [
        {
            "value": {
                "id": str(document_to_edit.id),
                "key": update_context["document_type_unique"].key,
                "country": "AFG",
                "number": "111111",
            },
            "previous_value": {
                "id": str(document_to_edit.id),
                "key": update_context["document_type_not_unique"].key,
                "country": "AFG",
                "number": "111111",
            },
            "approve_status": True,
        }
    ]
    update_context["ticket"].individual_data_update_ticket_details.save()

    service = IndividualDataUpdateService(
        update_context["ticket"], update_context["ticket"].individual_data_update_ticket_details
    )
    with pytest.raises(DRFValidationError) as exc:
        service.close(update_context["user"])
    assert f"Document of type {update_context['document_type_unique']} already exists for this individual" in str(
        exc.value
    )

    document_to_edit.refresh_from_db()
    assert document_to_edit.type == update_context["document_type_not_unique"]


def test_edit_document_unique_per_individual(update_context: dict[str, Any]) -> None:
    document_to_edit = DocumentFactory(
        individual=update_context["individual"],
        type=update_context["document_type_unique"],
        status=Document.STATUS_VALID,
        program=update_context["program"],
        document_number="111111",
        country=update_context["country_afg"],
    )

    update_context["ticket"].individual_data_update_ticket_details.individual_data["documents_to_edit"] = [
        {
            "value": {
                "id": str(document_to_edit.id),
                "key": update_context["document_type_unique"].key,
                "country": "AFG",
                "number": "22222",
            },
            "previous_value": {
                "id": str(document_to_edit.id),
                "key": update_context["document_type_unique"].key,
                "country": "AFG",
                "number": "111111",
            },
            "approve_status": True,
        }
    ]
    update_context["ticket"].individual_data_update_ticket_details.save()

    service = IndividualDataUpdateService(
        update_context["ticket"], update_context["ticket"].individual_data_update_ticket_details
    )
    try:
        service.close(update_context["user"])
    except ValidationError:
        pytest.fail("ValidationError should not be raised")

    document_to_edit.refresh_from_db()
    assert document_to_edit.document_number == "22222"


def test_edit_document_with_data_already_existing_in_same_program(update_context: dict[str, Any]) -> None:
    household = HouseholdFactory(
        program=update_context["program"],
        business_area=update_context["business_area"],
        create_role=False,
    )
    individual = IndividualFactory(
        household=household,
        business_area=update_context["business_area"],
        program=update_context["program"],
        registration_data_import=household.registration_data_import,
    )

    existing_document = DocumentFactory(
        individual=individual,
        type=update_context["document_type_unique"],
        status=Document.STATUS_VALID,
        program=update_context["program"],
        document_number="123456",
        country=update_context["country_afg"],
    )
    document_to_edit = DocumentFactory(
        individual=update_context["individual"],
        type=update_context["document_type_not_unique"],
        status=Document.STATUS_VALID,
        program=update_context["program"],
        document_number="111111",
        country=update_context["country_afg"],
    )

    update_context["ticket"].individual_data_update_ticket_details.individual_data["documents_to_edit"] = [
        {
            "value": {
                "id": str(document_to_edit.id),
                "key": update_context["document_type_unique"].key,
                "country": "AFG",
                "number": "123456",
            },
            "previous_value": {
                "id": str(document_to_edit.id),
                "key": update_context["document_type_not_unique"].key,
                "country": "AFG",
                "number": "111111",
            },
            "approve_status": True,
        }
    ]
    update_context["ticket"].individual_data_update_ticket_details.save()
    service = IndividualDataUpdateService(
        update_context["ticket"], update_context["ticket"].individual_data_update_ticket_details
    )
    with pytest.raises(DRFValidationError) as exc:
        service.close(update_context["user"])
    assert (
        f"Document with number {existing_document.document_number} of type "
        f"{update_context['document_type_unique']} already exists" in str(exc.value)
    )

    document_to_edit.refresh_from_db()
    assert document_to_edit.document_number == "111111"


def test_edit_account(update_context: dict[str, Any]) -> None:
    fi1 = FinancialInstitutionFactory()
    fi2 = FinancialInstitutionFactory()
    account = AccountFactory(
        id=uuid.UUID("e0a7605f-62f4-4280-99f6-b7a2c4001680"),
        individual=update_context["individual"],
        number="123",
        data={"field": "value"},
        financial_institution=fi1,
        account_type=update_context["account_type_mobile"],
    )
    update_context["ticket"].individual_data_update_ticket_details.individual_data["accounts"] = [
        {
            "approve_status": True,
            "value": {
                "number": "2222",
                "financial_institution": str(fi1.id),
                "data_fields": [{"key": "new_field", "value": "new_value"}],
                "account_type": "mobile",
            },
        }
    ]
    update_context["ticket"].individual_data_update_ticket_details.individual_data["accounts_to_edit"] = [
        {
            "approve_status": True,
            "financial_institution": str(fi2.id),
            "financial_institution_previous_value": str(fi1.id),
            "number": "123123",
            "number_previous_value": "123",
            "data_fields": [
                {
                    "name": "field",
                    "previous_value": "value",
                    "value": "updated_value",
                },
                {"name": "new_field", "previous_value": None, "value": "new_value"},
            ],
            "id": "e0a7605f-62f4-4280-99f6-b7a2c4001680",
            "name": "mobile",
        }
    ]
    update_context["ticket"].individual_data_update_ticket_details.save()

    service = IndividualDataUpdateService(
        update_context["ticket"], update_context["ticket"].individual_data_update_ticket_details
    )
    try:
        service.close(update_context["user"])
    except ValidationError:
        pytest.fail("ValidationError should not be raised")

    account.refresh_from_db()
    assert account.number == "123123"
    assert account.financial_institution == fi2
    assert account.data == {
        "field": "updated_value",
        "new_field": "new_value",
    }

    new_account = update_context["individual"].accounts.exclude(id=account.id).first()
    assert new_account.number == "2222"
    assert new_account.financial_institution == fi1
    assert new_account.data == {"new_field": "new_value"}


def test_update_people_individual_hh_fields(update_context: dict[str, Any]) -> None:
    pl = CountryFactory(name="Poland", iso_code3="POL", iso_code2="PL", iso_num="620")
    CountryFactory(
        name="Other Country",
        short_name="Oth",
        iso_code2="O",
        iso_code3="OTH",
        iso_num="111",
    )
    area_type_1 = AreaTypeFactory(area_level=1, country=pl)
    area_type_2 = AreaTypeFactory(area_level=2, country=pl, parent=area_type_1)
    area1 = AreaFactory(area_type=area_type_1, p_code="PL22", name="Test Area Parent")
    AreaFactory(area_type=area_type_2, p_code="PL22M33", name="Test Area M", parent=area1)
    hh_fields = [
        "consent",
        "residence_status",
        "country_origin",
        "country",
        "address",
        "village",
        "currency",
        "unhcr_id",
        "name_enumerator",
        "org_enumerator",
        "org_name_enumerator",
        "registration_method",
    ]
    hh = update_context["household"]
    ind_data = {}
    new_data = {
        "address": "Test Address ABC",
        "country_origin": "POL",
        "country": "OTH",
        "residence_status": "HOST",
        "village": "El Paso",
        "consent": None,
        "currency": "PLN",
        "unhcr_id": "random_unhcr_id_123",
        "name_enumerator": "test_name",
        "org_enumerator": "test_org",
        "org_name_enumerator": "test_org_name",
        "registration_method": "COMMUNITY",
    }
    for hh_field in hh_fields:
        ind_data[hh_field] = {
            "value": new_data.get(hh_field),
            "approve_status": True,
            "previous_value": (
                getattr(hh, hh_field).iso_code3 if isinstance(getattr(hh, hh_field), Country) else getattr(hh, hh_field)
            ),
        }
    ind_data["admin_area_title"] = {
        "value": "PL22M33",
        "approve_status": True,
        "previous_value": None,
    }
    update_context["ticket"].individual_data_update_ticket_details.individual_data = ind_data
    update_context["ticket"].individual_data_update_ticket_details.save()

    service = IndividualDataUpdateService(
        update_context["ticket"], update_context["ticket"].individual_data_update_ticket_details
    )
    service.close(update_context["user"])

    hh.refresh_from_db()
    for hh_field in hh_fields:
        hh_value = (
            getattr(hh, hh_field).iso_code3 if isinstance(getattr(hh, hh_field), Country) else getattr(hh, hh_field)
        )
        assert hh_value == new_data.get(hh_field)

    assert hh.admin_area.p_code == "PL22M33"
    assert hh.admin_area.name == "Test Area M"
    assert hh.admin2.p_code == "PL22M33"
    assert hh.admin2.name == "Test Area M"
    assert hh.admin3 is None
    assert hh.admin1 is not None
    assert hh.admin2.parent == hh.admin1


def test_update_phone_no_data(update_context: dict[str, Any]) -> None:
    update_context["ticket"].individual_data_update_ticket_details.individual_data = {
        "phone_no": {"approve_status": True, "previous_value": "+485656565665", "value": "+485544332211"},
        "phone_no_alternative": {
            "approve_status": True,
            "previous_value": "+485656561223",
            "value": "+485544334455",
        },
    }
    update_context["ticket"].individual_data_update_ticket_details.save()
    service = IndividualDataUpdateService(
        update_context["ticket"], update_context["ticket"].individual_data_update_ticket_details
    )
    service.close(update_context["user"])

    update_context["individual"].refresh_from_db()
    assert update_context["individual"].phone_no == "+485544332211"
    assert update_context["individual"].phone_no_alternative == "+485544334455"
