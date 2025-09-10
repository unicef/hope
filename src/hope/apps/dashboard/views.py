import logging
from typing import Any

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.db import OperationalError
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from hope.apps.account.models import RoleAssignment
from hope.apps.account.permissions import Permissions, check_permissions
from hope.apps.core.models import BusinessArea
from hope.apps.dashboard.celery_tasks import generate_dash_report_task
from hope.apps.dashboard.services import (
    GLOBAL_SLUG,
    DashboardCacheBase,
    DashboardDataCache,
    DashboardGlobalDataCache,
)
from hope.apps.utils.sentry import sentry_tags

log = logging.getLogger(__name__)


class DashboardDataView(APIView):
    """API View to retrieve a DashReport for a specific business area.

    Only authenticated users with the appropriate permissions can access this view.
    """

    permission_classes = [IsAuthenticated]

    @sentry_tags
    def get(self, request: Any, business_area_slug: str) -> Response:
        """Retrieve dashboard data for a given business area from Redis cache.

        If data is not cached or needs updating, refresh it.
        """
        is_global = business_area_slug.lower() == "global"
        data_cache: type[DashboardCacheBase] = DashboardGlobalDataCache if is_global else DashboardDataCache

        has_permission = False

        if is_global:
            if request.user.is_superuser or request.user.has_perm(Permissions.DASHBOARD_VIEW_COUNTRY.value):
                has_permission = True
        else:
            business_area_obj = get_object_or_404(BusinessArea, slug=business_area_slug)
            if check_permissions(
                request.user,
                [Permissions.DASHBOARD_VIEW_COUNTRY],
                business_area=business_area_obj,
            ):
                has_permission = True

        if not has_permission:
            return Response(
                {
                    "detail": _(
                        "You do not have permission to view the global dashboard."
                        if is_global
                        else "You do not have permission to view this dashboard."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        cache_identifier = GLOBAL_SLUG if is_global else business_area_slug
        data = data_cache.get_data(cache_identifier)
        if data is None:
            generate_dash_report_task.delay(cache_identifier)
            data = []
        return Response(data, status=status.HTTP_200_OK)


class CreateOrUpdateDashReportView(APIView):
    """API to trigger the creation or update of a DashReport for a given business area.

    Restricted to superusers and users with the required permissions.
    """

    permission_classes = [IsAuthenticated]

    @sentry_tags
    def post(self, request: Any, business_area_slug: str) -> Response:
        is_global = business_area_slug.lower() == GLOBAL_SLUG
        has_permission = False
        business_area_obj = None

        if is_global:
            if (
                request.user.is_superuser
                or RoleAssignment.objects.filter(
                    user=request.user,
                    role__permissions__contains=[Permissions.DASHBOARD_VIEW_COUNTRY.value],
                    business_area__active=True,
                ).exists()
            ):
                has_permission = True
        else:
            business_area_obj = get_object_or_404(BusinessArea, slug=business_area_slug)
            if request.user.is_superuser or check_permissions(
                request.user,
                [Permissions.DASHBOARD_VIEW_COUNTRY],
                business_area=business_area_obj,
            ):
                has_permission = True

        if not has_permission:
            raise PermissionDenied(_("You do not have permission to trigger DashReport generation for this scope."))

        try:
            task_identifier = GLOBAL_SLUG if is_global else business_area_slug

            data_cache_class: type[DashboardCacheBase] = DashboardGlobalDataCache if is_global else DashboardDataCache
            data_cache_key_to_clear = data_cache_class.get_cache_key(task_identifier)
            cache.delete(data_cache_key_to_clear)

            generate_dash_report_task.delay(task_identifier)

            return Response(
                {"detail": _("DashReport generation task has been triggered.")},
                status=status.HTTP_202_ACCEPTED,
            )
        except OperationalError as e:
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DashboardReportView(LoginRequiredMixin, TemplateView):
    """View to render the dashboard template for a specific business area."""

    template_name = "dashboard/dashboard.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        business_area_slug = kwargs.get("business_area_slug")
        is_global = business_area_slug.lower() == "global"

        has_permission = False

        if is_global:
            if self.request.user.is_superuser or self.request.user.has_perm(Permissions.DASHBOARD_VIEW_COUNTRY.value):
                has_permission = True
        else:
            business_area_obj = get_object_or_404(BusinessArea, slug=business_area_slug)
            if check_permissions(
                self.request.user,
                [Permissions.DASHBOARD_VIEW_COUNTRY],
                business_area=business_area_obj,
            ):
                has_permission = True

        if not has_permission:
            context["error_message"] = _(
                "You do not have permission to view the global dashboard."
                if is_global
                else "You do not have permission to view this dashboard."
            )
            context["has_permission"] = False
        else:
            context["business_area_slug"] = business_area_slug
            context["household_data_url"] = reverse("api:household-data", args=[business_area_slug])
            context["has_permission"] = True

        if is_global:
            self.template_name = "dashboard/global_dashboard.html"
        return context
