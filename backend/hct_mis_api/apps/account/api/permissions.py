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


class PDUViewListAndDetailsPermission(BaseRestPermission):
    PERMISSIONS = [Permissions.PDU_VIEW_LIST_AND_DETAILS]


class PDUTemplateCreatePermission(BaseRestPermission):
    PERMISSIONS = [Permissions.PDU_TEMPLATE_CREATE]


class PDUTemplateDownloadPermission(BaseRestPermission):
    PERMISSIONS = [Permissions.PDU_TEMPLATE_DOWNLOAD]


class PDUUploadPermission(BaseRestPermission):
    PERMISSIONS = [Permissions.PDU_UPLOAD]


class RDIViewListPermission(BaseRestPermission):
    PERMISSIONS = [Permissions.RDI_VIEW_LIST]


class TargetingViewListPermission(BaseRestPermission):
    PERMISSIONS = [Permissions.TARGETING_VIEW_LIST]


class GeoViewListPermission(BaseRestPermission):
    PERMISSIONS = [Permissions.GEO_VIEW_LIST]


class ProgramCycleViewListPermission(BaseRestPermission):
    PERMISSIONS = [Permissions.PM_PROGRAMME_CYCLE_VIEW_LIST]


class ProgramCycleViewDetailsPermission(BaseRestPermission):
    PERMISSIONS = [Permissions.PM_PROGRAMME_CYCLE_VIEW_DETAILS]


class ProgramCycleCreatePermission(BaseRestPermission):
    PERMISSIONS = [Permissions.PM_PROGRAMME_CYCLE_CREATE]


class ProgramCycleUpdatePermission(BaseRestPermission):
    PERMISSIONS = [Permissions.PM_PROGRAMME_CYCLE_UPDATE]


class ProgramCycleDeletePermission(BaseRestPermission):
    PERMISSIONS = [Permissions.PM_PROGRAMME_CYCLE_DELETE]
