from django_filters import CharFilter, ChoiceFilter, FilterSet

from hope.models.rule import Rule


class SteficonRuleFilter(FilterSet):
    type = ChoiceFilter(choices=Rule.TYPE_CHOICES, required=True, field_name="type")
    business_area = CharFilter(field_name="allowed_business_areas__slug", lookup_expr="exact")

    class Meta:
        fields = ("enabled", "deprecated", "type", "business_area")
        model = Rule
