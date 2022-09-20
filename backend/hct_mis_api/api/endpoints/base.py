from django.utils.functional import cached_property

from hct_mis_api.apps.core.models import BusinessArea


class SelectedBusinessAreaMixin:
    @cached_property
    def selected_business_area(self):
        return BusinessArea.objects.get(slug=self.kwargs["business_area"])
