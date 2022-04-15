import datetime as dt

from dateutil.relativedelta import relativedelta
from django.db.models import Count, Q


def has_children_filter_in_criteria(targeting_criteria_dict):
    for rule in targeting_criteria_dict.get("rules", []):
        for filter_dict in rule.get("filters", []):
            if filter_dict["field_name"] == "number_of_children":
                return True
    return False


def get_annotate_for_children_count(household_queryset):
    date_18_years_ago = (dt.datetime.now() - relativedelta(years=+18)).date()
    return household_queryset.annotate(
        number_of_children=Count("individuals", filter=Q(individuals__birth_date__gte=date_18_years_ago))
    )
