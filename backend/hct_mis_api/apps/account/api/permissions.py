from typing import Any

from rest_framework.permissions import BasePermission

from hct_mis_api.apps.account.permissions import Permissions, check_permissions


class BaseRestPermission(BasePermission):
    PERMISSIONS = []

    def has_permission(self, request: Any, view: Any) -> bool:
        user = request.user
        permissions = self.PERMISSIONS
        kwargs = {
            "business_area": request.parser_context.get("kwargs", {}).get("business_area"),
            "Program": request.parser_context.get("kwargs", {}).get("program_id"),
        }

        return check_permissions(user, permissions, **kwargs)


class PMViewListPermission(BaseRestPermission):
    PERMISSIONS = [Permissions.PM_VIEW_LIST]


class PaymentVerificationViewDetailsPermission(BaseRestPermission):
    PERMISSIONS = [Permissions.PAYMENT_VERIFICATION_VIEW_DETAILS]


class ProgrammeViewListAndDetailsPermission(BaseRestPermission):
    PERMISSIONS = [Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS]


class PaymentViewListManagerialPermission(BaseRestPermission):
    PERMISSIONS = [Permissions.PAYMENT_VIEW_LIST_MANAGERIAL]
