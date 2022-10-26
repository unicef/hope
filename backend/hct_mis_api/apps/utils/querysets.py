from django.db.models import QuerySet


def evaluate_qs(qs: QuerySet) -> QuerySet:
    """
    Purpose of this util it to make more visible that qs is getting evaluated,
    random list(qs) call could be easily lost and get removed from the code.
    Main use case is to lock table rows for querysets with applied select_for_update().
    """
    list(qs)
    return qs
