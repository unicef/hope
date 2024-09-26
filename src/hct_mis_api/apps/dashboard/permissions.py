from rest_framework.permissions import BasePermission


class ReportingPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm("hct_mis_api.reporting_export")

    def has_object_permission(self, request, view, obj):
        return (
            request.user.has_perm("hct_mis_api.reporting_export") and obj.business_area in request.user.business_areas
        )
