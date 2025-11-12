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

from hope.apps.account.permissions import Permissions, check_permissions
from hope.apps.dashboard.celery_tasks import generate_dash_report_task
from hope.apps.dashboard.services import (
    GLOBAL_SLUG,
    DashboardCacheBase,
    DashboardDataCache,
    DashboardGlobalDataCache,
)
from hope.apps.utils.sentry import sentry_tags
from hope.models import BusinessArea

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
        slug = business_area_slug.lower()
        is_global = slug == GLOBAL_SLUG
        business_area_obj = get_object_or_404(BusinessArea, slug=slug)
        if not check_permissions(request.user, [Permissions.DASHBOARD_VIEW_COUNTRY], business_area=business_area_obj):
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

        data_cache: type[DashboardCacheBase] = DashboardGlobalDataCache if is_global else DashboardDataCache
        data = data_cache.get_data(slug)
        if data is None:
            generate_dash_report_task.delay(slug)
            data = []
        return Response(data, status=status.HTTP_200_OK)


class CreateOrUpdateDashReportView(APIView):
    """API to trigger the creation or update of a DashReport for a given business area.

    Restricted to superusers and users with the required permissions.
    """

    permission_classes = [IsAuthenticated]

    @sentry_tags
    def post(self, request: Any, business_area_slug: str) -> Response:
        slug = business_area_slug.lower()
        is_global = slug == GLOBAL_SLUG
        business_area_obj = get_object_or_404(BusinessArea, slug=slug)
        if not (
            request.user.is_superuser
            or check_permissions(
                request.user,
                [Permissions.DASHBOARD_VIEW_COUNTRY],
                business_area=business_area_obj,
            )
        ):
            raise PermissionDenied(_("You do not have permission to trigger DashReport generation for this scope."))

        try:
            data_cache_class: type[DashboardCacheBase] = DashboardGlobalDataCache if is_global else DashboardDataCache
            data_cache_key_to_clear = data_cache_class.get_cache_key(slug)
            cache.delete(data_cache_key_to_clear)

            generate_dash_report_task.delay(slug)

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
        slug = business_area_slug.lower()
        is_global = slug == GLOBAL_SLUG

        business_area_obj = get_object_or_404(BusinessArea, slug=slug)
        has_permission = check_permissions(
            self.request.user,
            [Permissions.DASHBOARD_VIEW_COUNTRY],
            business_area=business_area_obj,
        )

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
