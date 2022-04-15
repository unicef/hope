import datetime as dt

from dateutil.relativedelta import relativedelta
from django.db.models import Count, Q


def has_children_filter_in_criteria(targeting_criteria_dict):
    return any(has(rule) for rule in targeting_criteria_dict.get("rules", []))


def has(rule):
    return any(filter_dict["field_name"] == "number_of_children" for filter_dict in rule.get("filters", []))

def get_annotate_for_children_count(household_queryset):
    date_18_years_ago = (dt.datetime.now() - relativedelta(years=+18)).date()
    return household_queryset.annotate(
        number_of_children=Count("individuals", filter=Q(individuals__birth_date__gte=date_18_years_ago))
    )
