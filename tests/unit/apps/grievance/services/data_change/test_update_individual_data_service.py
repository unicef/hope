from datetime import date
from typing import Any
import uuid

from django.core.exceptions import ValidationError
from django.test import TestCase
import pytest
from rest_framework.exceptions import ValidationError as DRFValidationError

from extras.test_utils.factories import (
    AccountFactory,
    AccountTypeFactory,
    AreaFactory,
    AreaTypeFactory,
    BusinessAreaFactory,
    CountryFactory,
    CurrencyFactory,
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
from hope.apps.household.api.caches import get_household_list_program_key, get_individual_list_program_key
from hope.models import Document

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


@pytest.fixture
def hh_field_reference_data(update_context):
    initial_currency = CurrencyFactory(code="USD", name="US Dollar")
    CurrencyFactory(code="PLN", name="Polish Zloty")
    initial_country = CountryFactory(name="Initial Country", iso_code3="ICO", iso_code2="IC", iso_num="999")
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

    hh = update_context["household"]
    hh.country = initial_country
    hh.country_origin = initial_country
    hh.currency = initial_currency
    hh.save(update_fields=["country", "country_origin", "currency"])


def _build_ind_data(hh, fields, new_values, extract):
    return {
        field: {
            "value": new_values[field],
            "approve_status": True,
            "previous_value": extract(getattr(hh, field)),
        }
        for field in fields
    }


def _close_ticket_and_refresh(update_context, ind_data, hh):
    update_context["ticket"].individual_data_update_ticket_details.individual_data = ind_data
    update_context["ticket"].individual_data_update_ticket_details.save()
    service = IndividualDataUpdateService(
        update_context["ticket"], update_context["ticket"].individual_data_update_ticket_details
    )
    service.close(update_context["user"])
    hh.refresh_from_db()


def _assert_fields_updated(hh, fields, new_values, extract):
    for field in fields:
        assert extract(getattr(hh, field)) == new_values[field]


def test_update_people_individual_hh_plain_fields(
    update_context: dict[str, Any], hh_field_reference_data: None, django_assert_num_queries
) -> None:
    fields = [
        "consent",
        "residence_status",
        "address",
        "village",
        "unhcr_id",
        "name_enumerator",
        "org_enumerator",
        "org_name_enumerator",
        "registration_method",
    ]
    new_values = {
        "consent": None,
        "residence_status": "HOST",
        "address": "Test Address ABC",
        "village": "El Paso",
        "unhcr_id": "random_unhcr_id_123",
        "name_enumerator": "test_name",
        "org_enumerator": "test_org",
        "org_name_enumerator": "test_org_name",
        "registration_method": "COMMUNITY",
    }
    hh = update_context["household"]
    ind_data = _build_ind_data(hh, fields, new_values, extract=lambda v: v)
    with django_assert_num_queries(27):
        _close_ticket_and_refresh(update_context, ind_data, hh)
    _assert_fields_updated(hh, fields, new_values, extract=lambda v: v)


def test_update_people_individual_hh_country_fields(
    update_context: dict[str, Any], hh_field_reference_data: None, django_assert_num_queries
) -> None:
    with django_assert_num_queries(31):
        fields = ["country_origin", "country"]
        new_values = {"country_origin": "POL", "country": "OTH"}
        hh = update_context["household"]
        ind_data = _build_ind_data(hh, fields, new_values, extract=lambda v: v.iso_code3)
        _close_ticket_and_refresh(update_context, ind_data, hh)
        _assert_fields_updated(hh, fields, new_values, extract=lambda v: v.iso_code3)


def test_update_people_individual_hh_currency_field(
    update_context: dict[str, Any], hh_field_reference_data: None, django_assert_num_queries
) -> None:
    with django_assert_num_queries(29):
        fields = ["currency"]
        new_values = {"currency": "PLN"}
        hh = update_context["household"]
        ind_data = _build_ind_data(hh, fields, new_values, extract=lambda v: v.code)
        _close_ticket_and_refresh(update_context, ind_data, hh)
        _assert_fields_updated(hh, fields, new_values, extract=lambda v: v.code)


def test_update_people_individual_hh_admin_area(
    update_context: dict[str, Any], hh_field_reference_data: None, django_assert_num_queries
) -> None:
    hh = update_context["household"]
    ind_data = {
        "admin_area_title": {
            "value": "PL22M33",
            "approve_status": True,
            "previous_value": None,
        },
    }
    with django_assert_num_queries(32):
        _close_ticket_and_refresh(update_context, ind_data, hh)
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


def test_close_individual_update_invalidates_both_caches(update_context: dict[str, Any]) -> None:
    update_context["ticket"].individual_data_update_ticket_details.individual_data = {
        "phone_no": {"approve_status": True, "previous_value": "+48111", "value": "+48222"},
    }
    update_context["ticket"].individual_data_update_ticket_details.save()

    program_id = update_context["individual"].program_id
    hh_cache_before = get_household_list_program_key(program_id)
    ind_cache_before = get_individual_list_program_key(program_id)

    service = IndividualDataUpdateService(
        update_context["ticket"], update_context["ticket"].individual_data_update_ticket_details
    )
    with TestCase.captureOnCommitCallbacks(execute=True):
        service.close(update_context["user"])

    assert get_household_list_program_key(program_id) > hh_cache_before
    assert get_individual_list_program_key(program_id) > ind_cache_before


def test_close_individual_update_with_hh_fields_invalidates_household_cache(update_context: dict[str, Any]) -> None:
    update_context["ticket"].individual_data_update_ticket_details.individual_data = {
        "village": {"approve_status": True, "previous_value": "", "value": "New Village"},
    }
    update_context["ticket"].individual_data_update_ticket_details.save()

    program_id = update_context["individual"].program_id
    hh_cache_before = get_household_list_program_key(program_id)

    service = IndividualDataUpdateService(
        update_context["ticket"], update_context["ticket"].individual_data_update_ticket_details
    )
    with TestCase.captureOnCommitCallbacks(execute=True):
        service.close(update_context["user"])

    assert get_household_list_program_key(program_id) > hh_cache_before
