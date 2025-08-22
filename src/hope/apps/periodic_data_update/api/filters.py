from django_filters import rest_framework as filters

from hope.apps.core.api.filters import UpdatedAtFilter
from hope.apps.periodic_data_update.models import PDUOnlineEdit


class PDUOnlineEditFilter(UpdatedAtFilter):
    status = filters.MultipleChoiceFilter(choices=PDUOnlineEdit.Status.choices)

    class Meta:
        model = PDUOnlineEdit
        fields = ("status",)
