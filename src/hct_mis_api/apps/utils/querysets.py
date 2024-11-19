from django.db.models import QuerySet


def evaluate_qs(qs: QuerySet) -> QuerySet:
    """
    Purpose of this util it to make more visible that qs is getting evaluated,
    random list(qs) call could be easily lost and get removed from the code.
    Main use case is to lock table rows for querysets with applied select_for_update().

    Good to read:
    https://docs.djangoproject.com/en/4.1/ref/models/querysets/#when-querysets-are-evaluated
    https://docs.djangoproject.com/en/4.1/ref/models/querysets/#select-for-update
    https://stackoverflow.com/questions/17159471/how-to-use-select-for-update-to-get-an-object-in-django
    """

    qs._fetch_all()
    return qs
