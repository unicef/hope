from django_filters import ChoiceFilter, FilterSet

from models.steficon import Rule


class SteficonRuleFilter(FilterSet):
    type = ChoiceFilter(choices=Rule.TYPE_CHOICES, required=True, field_name="type")

    class Meta:
        fields = ("enabled", "deprecated", "type")
        model = Rule
