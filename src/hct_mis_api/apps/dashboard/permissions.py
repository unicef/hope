from typing import Any

from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import View


class ReportingPermission(BasePermission):
    def has_permission(self, request: Request, view: View) -> bool:
        """
        Check if the user has the 'reporting_export' permission.
        """
        return request.user.has_perm("hct_mis_api.reporting_export")

    def has_object_permission(self, request: Request, view: View, obj: Any) -> bool:
        """
        Check if the user has the 'reporting_export' permission and if the business area
        of the object is within the user's assigned business areas.
        """
        return (
            request.user.has_perm("hct_mis_api.reporting_export") and obj.business_area in request.user.business_areas
        )
