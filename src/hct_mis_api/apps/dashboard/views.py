import logging
from typing import Any, Dict, Type

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from hct_mis_api.apps.account.permissions import Permissions, check_permissions
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.dashboard.celery_tasks import generate_dash_report_task
from hct_mis_api.apps.dashboard.services import (DashboardCacheBase,
                                                 DashboardDataCache,
                                                 DashboardGlobalDataCache)
from hct_mis_api.apps.utils.sentry import sentry_tags

log = logging.getLogger(__name__)

CACHE_TIMEOUT = 60 * 60 * 24  # 24 hours


class DashboardDataView(APIView):
    """
    API View to retrieve a DashReport for a specific business area.
    Only authenticated users with the appropriate permissions can access this view.
    """

    permission_classes = [IsAuthenticated]

    @sentry_tags
    def get(self, request: Any, business_area_slug: str) -> Response:
        """
        Retrieve dashboard data for a given business area from Redis cache.
        If data is not cached or needs updating, refresh it.
        """
        is_global = business_area_slug.lower() == "global"
        business_area = get_object_or_404(BusinessArea, slug=business_area_slug)
        data_cache: Type[DashboardCacheBase] = DashboardGlobalDataCache if is_global else DashboardDataCache

        if not check_permissions(request.user, [Permissions.DASHBOARD_VIEW_COUNTRY], business_area=business_area):
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

        data = data_cache.get_data(business_area_slug)
        if not data:
            data = data_cache.refresh_data(business_area_slug if not is_global else "global")

        return Response(data, status=status.HTTP_200_OK)


class CreateOrUpdateDashReportView(APIView):
    """
    API to trigger the creation or update of a DashReport for a given business area.
    Restricted to superusers and users with the required permissions.
    """

    permission_classes = [IsAuthenticated]

    @sentry_tags
    def post(self, request: Any, business_area_slug: str) -> Response:
        if not request.user.is_superuser and not check_permissions(
            request.user,
            [Permissions.DASHBOARD_VIEW_COUNTRY],
            business_area=BusinessArea.objects.get(slug=business_area_slug),
        ):
            raise PermissionDenied(
                "Only superusers or users with the correct permissions can create or update DashReports."
            )

        try:
            business_area = BusinessArea.objects.get(slug=business_area_slug)
            generate_dash_report_task.delay(business_area.slug)
            cache_key = f"dashboard_report_{business_area_slug}"
            cache.delete(cache_key)

            return Response(
                {"detail": _("DashReport generation task has been triggered.")}, status=status.HTTP_202_ACCEPTED
            )

        except BusinessArea.DoesNotExist:
            return Response({"detail": "Business area not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DashboardReportView(LoginRequiredMixin, TemplateView):
    """
    View to render the dashboard template for a specific business area.
    """

    template_name = "dashboard/dashboard.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        business_area_slug = kwargs.get("business_area_slug")
        business_area = get_object_or_404(BusinessArea, slug=business_area_slug)

        if not check_permissions(self.request.user, [Permissions.DASHBOARD_VIEW_COUNTRY], business_area=business_area):
            context["error_message"] = _("You do not have permission to view this dashboard.")
            context["has_permission"] = False
        else:
            context["business_area_slug"] = business_area_slug
            context["household_data_url"] = reverse("api:household-data", args=[business_area_slug])
            context["has_permission"] = True
        # Dynamically switch template for "Global" dashboard
        if business_area_slug.lower() == "global":
            self.template_name = "dashboard/global_dashboard.html"
        return context
