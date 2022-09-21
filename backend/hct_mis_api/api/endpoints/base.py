from django.utils.functional import cached_property

from rest_framework.views import APIView

from hct_mis_api.apps.core.models import BusinessArea

from ..auth import HOPEPermission


class SelectedBusinessAreaMixin:
    @cached_property
    def selected_business_area(self):
        return BusinessArea.objects.get(slug=self.kwargs.get("business_area", None))


class HOPEAPIView(SelectedBusinessAreaMixin, APIView):
    permission_classes = [HOPEPermission]
    # authentication_classes = [HOPEAuthentication]
    permission = "any"
