from django.utils.functional import cached_property

from rest_framework.views import APIView

from hct_mis_api.api.auth import HOPEPermission
from hct_mis_api.apps.core.models import BusinessArea


class SelectedBusinessAreaMixin:
    @cached_property
    def selected_business_area(self):
        return BusinessArea.objects.get(slug=self.kwargs["business_area"])


class HOPEAPIView(SelectedBusinessAreaMixin, APIView):
    permission_classes = [HOPEPermission]
    permission = "any"
