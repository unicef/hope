from django.db.models import Case, Q, QuerySet, When

from hct_mis_api.apps.grievance.models import GrievanceTicket
from hct_mis_api.apps.targeting.models import TargetPopulation


def apply_targeting_criteria_flags(target_population: TargetPopulation, households: QuerySet) -> QuerySet:
    if target_population.targeting_criteria.flag_exclude_if_active_adjudication_ticket:
        households = apply_flag_exclude_if_active_adjudication_ticket(households)
    if target_population.targeting_criteria.flag_exclude_if_on_sanction_list:
        households = apply_flag_exclude_if_on_sanction_list(households)
    return households


def apply_flag_exclude_if_active_adjudication_ticket(households: QuerySet) -> QuerySet:
    households_to_be_excluded = households.annotate(
        has_active_adjudication_tickets=Case(
            When(
                (
                    Q(individuals__ticket_duplicates__isnull=False)
                    & ~Q(individuals__ticket_duplicates__ticket__status=GrievanceTicket.STATUS_CLOSED)
                )
                | (
                    Q(individuals__ticket_golden_records__isnull=False)
                    & ~Q(individuals__ticket_golden_records__ticket__status=GrievanceTicket.STATUS_CLOSED)
                )
                | (
                    Q(representatives__ticket_duplicates__isnull=False)
                    & ~Q(representatives__ticket_duplicates__ticket__status=GrievanceTicket.STATUS_CLOSED)
                )
                | (
                    Q(representatives__ticket_golden_records__isnull=False)
                    & ~Q(representatives__ticket_golden_records__ticket__status=GrievanceTicket.STATUS_CLOSED)
                ),
                then=True,
            ),
            default=False,
        )
    ).filter(has_active_adjudication_tickets=True)

    return households.exclude(id__in=households_to_be_excluded)


def apply_flag_exclude_if_on_sanction_list(households: QuerySet) -> QuerySet:
    households_to_be_excluded = households.annotate(
        is_on_saction_list=Case(
            When(
                Q(individuals__sanction_list_confirmed_match=True)
                | Q(representatives__sanction_list_confirmed_match=True),
                then=True,
            ),
            default=False,
        )
    ).filter(is_on_saction_list=True)
    return households.exclude(id__in=households_to_be_excluded)
