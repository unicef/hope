"""The admin cursor must list every row when several share the ordering value at a page boundary."""

from datetime import UTC, datetime

from admin_cursor_paginator.cursor import Cursor, encode_cursor
from django.contrib.admin.models import LogEntry
from django.contrib.admin.sites import AdminSite
from django.core.paginator import Paginator
from django.test import RequestFactory
import pytest

from extras.test_utils.factories import (
    AccountFactory,
    BusinessAreaFactory,
    DocumentFactory,
    HouseholdFactory,
    IndividualFactory,
    PaymentFactory,
    ProgramFactory,
    UserFactory,
)
from hope.admin.account import AccountAdmin
from hope.admin.document import DocumentAdmin
from hope.admin.household import HouseholdAdmin
from hope.admin.individual import IndividualAdmin
from hope.admin.payment_plan import PaymentAdmin
from hope.admin.utils import FieldPkCursorPaginator
from hope.models import Account, Document, Household, Individual, Payment

pytestmark = pytest.mark.django_db


# unicef_id is unique only per program: a program copy keeps it, so one id can sit in two programs.
@pytest.fixture
def same_unicef_id_population():
    ba = BusinessAreaFactory(slug="unicef-id-tie-ba")
    program = ProgramFactory(business_area=ba, status="ACTIVE")
    other_program = ProgramFactory(business_area=ba, status="ACTIVE")
    return {
        Individual: [
            IndividualFactory(household=None, business_area=ba, program=program, unicef_id="IND-24-0000.0001").pk,
            IndividualFactory(household=None, business_area=ba, program=other_program, unicef_id="IND-24-0000.0001").pk,
        ],
        Household: [
            HouseholdFactory(
                business_area=ba,
                program=program,
                create_role=False,
                unicef_id="HH-24-0000.0001",
                head_of_household__unicef_id="IND-25-0000.0001",
            ).pk,
            HouseholdFactory(
                business_area=ba,
                program=other_program,
                create_role=False,
                unicef_id="HH-24-0000.0001",
                head_of_household__unicef_id="IND-25-0000.0002",
            ).pk,
        ],
    }


# Rows created in one bulk operation can share created_at; auto_now_add ignores a passed value, hence update().
@pytest.fixture
def same_created_at_population():
    created_at = datetime(2026, 1, 1, 12, 0, 0, 123456, tzinfo=UTC)
    documents = [DocumentFactory().pk, DocumentFactory().pk]
    accounts = [AccountFactory().pk, AccountFactory().pk]
    payments = [PaymentFactory().pk, PaymentFactory().pk]
    Document.all_objects.filter(pk__in=documents).update(created_at=created_at)
    Account.all_objects.filter(pk__in=accounts).update(created_at=created_at)
    Payment.all_objects.filter(pk__in=payments).update(created_at=created_at)
    return {Document: documents, Account: accounts, Payment: payments}


@pytest.fixture
def staff_user():
    return UserFactory(is_staff=True, is_active=True, status="ACTIVE")


def admin_request(user, params=None):
    request = RequestFactory().get("/admin/", params or {})
    request.user = user
    return request


@pytest.mark.parametrize(
    ("model", "model_admin_class", "term"),
    [(Individual, IndividualAdmin, "IND-24"), (Household, HouseholdAdmin, "HH-24"), (Household, HouseholdAdmin, "")],
    ids=["individual-search", "household-search", "household-no-search"],
)
def test_cursor_paging_over_rows_sharing_a_unicef_id_lists_every_row(
    same_unicef_id_population, staff_user, model, model_admin_class, term
):
    model_admin = model_admin_class(model, AdminSite())
    first_request = admin_request(staff_user)
    queryset, _ = model_admin.get_search_results(first_request, model_admin.get_queryset(first_request), term)
    first_page = model_admin.get_paginator(first_request, queryset, 1).page(1)
    second_request = admin_request(staff_user, {"p": encode_cursor(first_page.next_cursor)})

    second_page = model_admin.get_paginator(second_request, queryset, 1).page(2)

    assert [obj.pk for obj in [*first_page, *second_page]] == sorted(same_unicef_id_population[model])


@pytest.mark.parametrize(
    ("model", "model_admin_class"),
    [(Document, DocumentAdmin), (Account, AccountAdmin), (Payment, PaymentAdmin)],
    ids=["document", "account", "payment"],
)
def test_cursor_paging_over_rows_sharing_created_at_lists_every_row(
    same_created_at_population, staff_user, model, model_admin_class
):
    model_admin = model_admin_class(model, AdminSite())
    first_request = admin_request(staff_user)
    queryset = model_admin.get_queryset(first_request)
    first_page = model_admin.get_paginator(first_request, queryset, 1).page(1)
    second_request = admin_request(staff_user, {"p": encode_cursor(first_page.next_cursor)})

    second_page = model_admin.get_paginator(second_request, queryset, 1).page(2)

    assert [obj.pk for obj in [*first_page, *second_page]] == sorted(same_created_at_population[model], reverse=True)


def test_previous_page_cursor_on_a_shared_unicef_id_returns_the_row_before_it(same_unicef_id_population, staff_user):
    first_pk, second_pk = sorted(same_unicef_id_population[Individual])
    model_admin = IndividualAdmin(Individual, AdminSite())
    queryset, _ = model_admin.get_search_results(
        admin_request(staff_user), model_admin.get_queryset(admin_request(staff_user)), "IND-24"
    )
    cursor = Cursor(value=FieldPkCursorPaginator.cursor_value("IND-24-0000.0001", second_pk), is_reverse=1, number=2)

    page = model_admin.get_paginator(admin_request(staff_user, {"p": encode_cursor(cursor)}), queryset, 1).page(2)

    assert [obj.pk for obj in page] == [first_pk]
    assert page.next_cursor.value == FieldPkCursorPaginator.cursor_value("IND-24-0000.0001", first_pk)


# A cursor from a bookmarked link made before the pk was added carries the field value alone.
def test_cursor_without_pk_opens_the_first_page(same_unicef_id_population, staff_user):
    model_admin = IndividualAdmin(Individual, AdminSite())
    queryset, _ = model_admin.get_search_results(
        admin_request(staff_user), model_admin.get_queryset(admin_request(staff_user)), "IND-24"
    )
    cursor = Cursor(value="IND-24-0000.0001", is_reverse=0, number=2)

    page = model_admin.get_paginator(admin_request(staff_user, {"p": encode_cursor(cursor)}), queryset, 1).page(2)

    assert page.number == 1
    assert [obj.pk for obj in page] == [min(same_unicef_id_population[Individual])]


# Django's history_view pages LogEntry rows through the model admin's get_paginator.
def test_history_view_log_entries_keep_the_offset_paginator(staff_user):
    model_admin = IndividualAdmin(Individual, AdminSite())

    paginator = model_admin.get_paginator(admin_request(staff_user), LogEntry.objects.all(), 100)

    assert type(paginator) is Paginator
