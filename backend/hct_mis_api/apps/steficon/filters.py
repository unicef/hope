from django_filters import FilterSet

from hct_mis_api.apps.steficon.models import Rule


class SteficonRuleFilter(FilterSet):
    class Meta:
        fields = ("enabled", "deprecated", "type")
        model = Rule
