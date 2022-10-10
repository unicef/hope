from django_filters import CharFilter, ChoiceFilter, FilterSet

from hct_mis_api.apps.steficon.models import Rule


class SteficonRuleFilter(FilterSet):
    type = ChoiceFilter(choices=Rule.TYPE_CHOICES, required=True, field_name="type")

    class Meta:
        fields = ("enabled", "deprecated", "type")
        model = Rule
