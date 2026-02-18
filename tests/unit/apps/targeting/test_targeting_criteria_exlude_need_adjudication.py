import pytest

from extras.test_utils.factories import (
    BusinessAreaFactory,
    HouseholdFactory,
    IndividualFactory,
    PaymentFactory,
    PaymentPlanFactory,
    TicketNeedsAdjudicationDetailsFactory,
)
from hope.apps.grievance.models import GrievanceTicket
from hope.apps.targeting.services.targeting_service import TargetingCriteriaQueryingBase
from hope.models import Household

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area():
    return BusinessAreaFactory(slug="afghanistan")


@pytest.fixture
def targeting_flag_data(business_area):
    household1 = HouseholdFactory(business_area=business_area)
    IndividualFactory.create_batch(2, household=household1)

    representative1 = IndividualFactory(household=None)
    household1.representatives.set([representative1])

    household2 = HouseholdFactory(business_area=business_area)
    individuals2 = IndividualFactory.create_batch(2, household=household2)

    representative2 = IndividualFactory(household=None)
    household2.representatives.set([representative2])

    payment_plan = PaymentPlanFactory(
        business_area=business_area,
        flag_exclude_if_active_adjudication_ticket=True,
        flag_exclude_if_on_sanction_list=True,
    )

    PaymentFactory(parent=payment_plan, household=household1)
    PaymentFactory(parent=payment_plan, household=household2)

    golden_record = IndividualFactory(household=None)

    ticket_member = TicketNeedsAdjudicationDetailsFactory(
        golden_records_individual=golden_record, ticket__issue_type=23
    )
    ticket_rep = TicketNeedsAdjudicationDetailsFactory(golden_records_individual=golden_record, ticket__issue_type=23)

    return {
        "household1": household1,
        "household2": household2,
        "individuals2": individuals2,
        "representative2": representative2,
        "ticket_member": ticket_member,
        "ticket_rep": ticket_rep,
    }


@pytest.mark.parametrize(
    ("member_dup", "rep_dup", "ticket_status", "household_count"),
    [
        (True, False, GrievanceTicket.STATUS_IN_PROGRESS, 1),
        (True, False, GrievanceTicket.STATUS_CLOSED, 2),
        (False, True, GrievanceTicket.STATUS_IN_PROGRESS, 1),
        (False, True, GrievanceTicket.STATUS_CLOSED, 2),
        (True, True, GrievanceTicket.STATUS_IN_PROGRESS, 1),
        (True, True, GrievanceTicket.STATUS_CLOSED, 2),
    ],
)
def test_flag_exclude_if_active_adjudication_ticket_duplicate(
    targeting_flag_data,
    member_dup,
    rep_dup,
    ticket_status,
    household_count,
):
    if member_dup:
        t = targeting_flag_data["ticket_member"]
        t.ticket.status = ticket_status
        t.ticket.save()
        t.possible_duplicates.set([targeting_flag_data["individuals2"][0]])

    if rep_dup:
        t = targeting_flag_data["ticket_rep"]
        t.ticket.status = ticket_status
        t.ticket.save()
        t.possible_duplicates.set([targeting_flag_data["representative2"]])

    assert Household.objects.count() == 2

    criteria = TargetingCriteriaQueryingBase()
    criteria.flag_exclude_if_active_adjudication_ticket = True

    qs = Household.objects.filter(criteria.apply_flag_exclude_if_active_adjudication_ticket())
    assert qs.count() == household_count


@pytest.mark.parametrize(
    ("member_gr", "rep_gr", "ticket_status", "household_count"),
    [
        (True, False, GrievanceTicket.STATUS_IN_PROGRESS, 1),
        (True, False, GrievanceTicket.STATUS_CLOSED, 2),
        (False, True, GrievanceTicket.STATUS_IN_PROGRESS, 1),
        (False, True, GrievanceTicket.STATUS_CLOSED, 2),
        (True, True, GrievanceTicket.STATUS_IN_PROGRESS, 1),
        (True, True, GrievanceTicket.STATUS_CLOSED, 2),
    ],
)
def test_flag_exclude_if_active_adjudication_ticket_golden_record(
    targeting_flag_data,
    member_gr,
    rep_gr,
    ticket_status,
    household_count,
):
    if member_gr:
        t = targeting_flag_data["ticket_member"]
        t.ticket.status = ticket_status
        t.ticket.save()
        t.golden_records_individual = targeting_flag_data["individuals2"][0]
        t.save()

    if rep_gr:
        t = targeting_flag_data["ticket_rep"]
        t.ticket.status = ticket_status
        t.ticket.save()
        t.golden_records_individual = targeting_flag_data["representative2"]
        t.save()

    criteria = TargetingCriteriaQueryingBase()
    criteria.flag_exclude_if_active_adjudication_ticket = True

    qs = Household.objects.filter(criteria.apply_flag_exclude_if_active_adjudication_ticket())
    assert qs.count() == household_count


def test_flag_exclude_if_active_adjudication_ticket_no_ticket():
    criteria = TargetingCriteriaQueryingBase()
    criteria.flag_exclude_if_active_adjudication_ticket = True

    qs = Household.objects.filter(criteria.apply_flag_exclude_if_active_adjudication_ticket())
    assert qs.count() == Household.objects.count()


@pytest.mark.parametrize(
    ("member_sanctioned", "rep_sanctioned", "household_count"),
    [
        (True, False, 1),
        (False, True, 1),
        (True, True, 1),
        (False, False, 2),
    ],
)
def test_flag_exclude_if_on_sanction_list(
    targeting_flag_data,
    member_sanctioned,
    rep_sanctioned,
    household_count,
):
    if member_sanctioned:
        ind = targeting_flag_data["individuals2"][0]
        ind.sanction_list_confirmed_match = True
        ind.save()

    if rep_sanctioned:
        rep = targeting_flag_data["representative2"]
        rep.sanction_list_confirmed_match = True
        rep.save()

    criteria = TargetingCriteriaQueryingBase()
    criteria.flag_exclude_if_on_sanction_list = True

    qs = Household.objects.filter(criteria.apply_flag_exclude_if_on_sanction_list())
    assert qs.count() == household_count
