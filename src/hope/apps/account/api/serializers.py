from typing import Any

from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.utils import timezone
from flags.state import flag_state
from rest_framework import serializers
from rest_framework.utils.serializer_helpers import ReturnDict

from hope.apps.account.models import (
    USER_STATUS_CHOICES,
    Partner,
    Role,
    RoleAssignment,
    User,
)
from hope.apps.account.permissions import Permissions
from hope.apps.core.models import BusinessArea
from hope.apps.core.utils import to_choice_object
from hope.apps.geo.api.serializers import AreaLevelSerializer
from hope.apps.program.models import Program


class UserBusinessAreaSerializer(serializers.ModelSerializer):
    permissions = serializers.SerializerMethodField()
    is_accountability_applicable = serializers.SerializerMethodField()

    class Meta:
        model = BusinessArea
        fields = (
            "id",
            "name",
            "slug",
            "permissions",
            "is_accountability_applicable",
        )

    def get_permissions(self, obj: BusinessArea) -> list:
        user = self.context["user_obj"]
        if not user:
            return []

        cached_user_roles = getattr(user, "cached_user_role_assignments", None)
        cached_partner_roles = getattr(user.partner, "cached_partner_role_assignments", None) if user.partner else []

        if cached_user_roles is not None:
            permissions_set = set()

            relevant_assignments = [
                assignment for assignment in cached_user_roles if assignment.business_area.id == obj.id
            ]

            if cached_partner_roles:
                relevant_assignments.extend(
                    [assignment for assignment in cached_partner_roles if assignment.business_area.id == obj.id]
                )

            for assignment in relevant_assignments:
                if assignment.role and assignment.role.permissions:
                    permissions_set.update(assignment.role.permissions)
                if hasattr(assignment, "group") and assignment.group:
                    for perm in getattr(assignment.group, "permissions", []):
                        if hasattr(perm, "content_type") and hasattr(perm, "codename"):
                            permissions_set.add(f"{perm.content_type.app_label}.{perm.codename}")

            return permissions_set

        return user.all_permissions_in_business_areas[str(obj.id)]

    def get_is_accountability_applicable(self, obj: BusinessArea) -> bool:
        return all(
            [
                self.context["allow_accountability_module"],
                obj.is_accountability_applicable,
            ]
        )


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ("name", "subsystem", "is_visible_on_ui", "is_available_for_partner")


class RoleAssignmentSerializer(serializers.ModelSerializer):
    business_area = serializers.CharField(source="business_area.slug")
    program = serializers.CharField(source="program.name", allow_null=True)
    role = RoleSerializer()

    class Meta:
        model = RoleAssignment
        fields = ("role", "business_area", "program")


class PartnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Partner
        fields = ("id", "name")


class ProgramUsersSerializer(serializers.ModelSerializer):
    partner = PartnerSerializer()
    partner_roles = serializers.SerializerMethodField()
    user_roles = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "is_superuser",
            "partner",
            "user_roles",
            "partner_roles",
            "status",
            "last_login",
        )

    @staticmethod
    def get_partner_roles(user: User) -> ReturnDict:
        """Use prefetched data when available to avoid additional queries."""
        cached_partner_roles = getattr(user.partner, "cached_partner_role_assignments", None)

        if cached_partner_roles is not None:
            role_assignments = cached_partner_roles
        else:
            role_assignments = (
                user.partner.role_assignments.order_by("business_area__slug", "role__name")
                .select_related("business_area", "role")
                .exclude(expiry_date__lt=timezone.now())
            )
        return RoleAssignmentSerializer(role_assignments, many=True).data

    @staticmethod
    def get_user_roles(user: User) -> ReturnDict:
        """Use prefetched data when available to avoid additional queries."""
        cached_user_roles = getattr(user, "cached_user_role_assignments", None)

        if cached_user_roles is not None:
            role_assignments = cached_user_roles
        else:
            role_assignments = (
                user.role_assignments.order_by("business_area__slug", "role__name")
                .select_related("business_area", "role")
                .exclude(expiry_date__lt=timezone.now())
            )
        return RoleAssignmentSerializer(role_assignments, many=True).data


class ProfileSerializer(ProgramUsersSerializer):
    business_areas = serializers.SerializerMethodField()
    permissions_in_scope = serializers.SerializerMethodField()
    cross_area_filter_available = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = ProgramUsersSerializer.Meta.fields + (
            "business_areas",
            "permissions_in_scope",
            "cross_area_filter_available",
        )

    @staticmethod
    def get_business_areas(user: User) -> ReturnDict:
        """Use prefetched data when available to avoid additional queries."""
        business_areas = set()

        cached_user_roles = getattr(user, "cached_user_role_assignments", None)
        if cached_user_roles is not None:
            for assignment in cached_user_roles:
                business_areas.add(assignment.business_area)

        if user.partner:
            cached_partner_roles = getattr(user.partner, "cached_partner_role_assignments", None)
            if cached_partner_roles is not None:
                for assignment in cached_partner_roles:
                    business_areas.add(assignment.business_area)

        if cached_user_roles is None:
            business_areas = user.business_areas

        return UserBusinessAreaSerializer(
            list(business_areas),
            context={"user_obj": user, "allow_accountability_module": bool(flag_state("ALLOW_ACCOUNTABILITY_MODULE"))},
            many=True,
        ).data

    def get_permissions_in_scope(self, user: User) -> set:
        request = self.context.get("request", {})
        if user.is_superuser:
            return {e.value for e in Permissions}

        business_area_slug = request.parser_context["kwargs"]["business_area_slug"]
        if program_slug := request.query_params.get("program"):  # scope program
            program = self.context.get("program") or get_object_or_404(
                Program, slug=program_slug, business_area__slug=business_area_slug
            )
            return user.permissions_in_business_area(business_area_slug, program.id)

        return user.permissions_in_business_area(business_area_slug)

    def get_cross_area_filter_available(self, user: User) -> bool:
        """Check if the cross area filter is available for the user.

        Access to the cross-area filter, in addition to the standard permissions check,
        is available only if user does not have ANY area limits in the program (has full-area-access)
        """
        perm = Permissions.GRIEVANCES_CROSS_AREA_FILTER.value

        request = self.context.get("request", {})
        business_area_slug = request.parser_context["kwargs"]["business_area_slug"]

        if program_slug := request.query_params.get("program"):
            program = self.context.get("program") or get_object_or_404(
                Program, slug=program_slug, business_area__slug=business_area_slug
            )
            return user.has_perm(perm, program) and not user.partner.has_area_limits_in_program(program.id)

        business_area = BusinessArea.objects.get(slug=business_area_slug) if business_area_slug != "undefined" else None
        return user.has_perm(perm, business_area)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ("id", "first_name", "last_name", "email", "username")


class PartnerForProgramSerializer(serializers.ModelSerializer):
    """Serializer for Partner model.

    It expects Partner objects to be annotated with partner_program which is the program that is serializing the object
    """

    areas = serializers.SerializerMethodField()
    area_access = serializers.SerializerMethodField()

    class Meta:
        model = Partner
        fields = ("id", "name", "area_access", "areas")

    def get_area_access(self, obj: Partner) -> str:
        if obj.annotate_has_admin_area_limit:
            return "ADMIN_AREA"
        return "BUSINESS_AREA"

    def get_areas(self, obj: Partner) -> ReturnDict:
        if not obj.annotate_has_admin_area_limit:
            return None
        areas_qs = obj.get_areas_for_program(obj.partner_program).order_by("name")
        return AreaLevelSerializer(areas_qs, many=True).data


class UserChoicesSerializer(serializers.Serializer):
    role_choices = serializers.SerializerMethodField()
    status_choices = serializers.SerializerMethodField()
    partner_choices = serializers.SerializerMethodField()
    partner_choices_temp = serializers.SerializerMethodField()

    def get_role_choices(self, *args: Any, **kwargs: Any) -> list[dict[str, Any]]:
        return [
            {"name": role.name, "value": role.id, "subsystem": role.subsystem} for role in Role.objects.order_by("name")
        ]

    def get_status_choices(self, *args: Any, **kwargs: Any) -> list[dict[str, Any]]:
        return to_choice_object(USER_STATUS_CHOICES)

    def get_partner_choices(self, *args: Any, **kwargs: Any) -> list[dict[str, Any]]:
        business_area_slug = self.context["request"].parser_context["kwargs"]["business_area_slug"]
        return to_choice_object(
            list(
                Partner.objects.exclude(name=settings.DEFAULT_EMPTY_PARTNER)
                .filter(allowed_business_areas__slug=business_area_slug)
                .exclude(id__in=Partner.objects.filter(parent__isnull=False).values_list("parent_id", flat=True))
                .values_list("id", "name")
            )
        )

    def get_partner_choices_temp(self, *args: Any, **kwargs: Any) -> list[dict[str, Any]]:
        # TODO: can be removed after proper solution is applied; this is the temp solution to skip the user input in
        #  program mutations and retrieve partners already with a role in BA
        business_area_slug = self.context["request"].parser_context["kwargs"]["business_area_slug"]
        return to_choice_object(
            list(
                Partner.objects.exclude(name=settings.DEFAULT_EMPTY_PARTNER)
                .filter(
                    role_assignments__business_area__slug=business_area_slug,
                    role_assignments__program=None,
                )
                .exclude(id__in=Partner.objects.filter(parent__isnull=False).values_list("parent_id", flat=True))
                .values_list("id", "name")
            )
        )
