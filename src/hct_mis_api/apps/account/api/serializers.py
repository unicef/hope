from django.contrib.auth import get_user_model

from flags.state import flag_state
from rest_framework import serializers
from rest_framework.utils.serializer_helpers import ReturnDict

from hct_mis_api.apps.account.models import Role, User
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.program.models import Program


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
        user = self.context["request"].user
        if user:
            return user.permissions_in_business_area(obj.slug)
        return []

    def get_is_accountability_applicable(self, obj: BusinessArea) -> bool:
        return all([bool(flag_state("ALLOW_ACCOUNTABILITY_MODULE")), obj.is_accountability_applicable])


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        exclude = ("id",)


class ProfileSerializer(serializers.ModelSerializer):
    permissions_in_scope = serializers.SerializerMethodField()
    business_areas = UserBusinessAreaSerializer(many=True)
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
            "business_areas",
            "permissions_in_scope",
            "user_roles",
            "partner_roles",
        )

    @staticmethod
    def get_partner_roles(user: User) -> ReturnDict:
        role_ids = user.partner.role_assignments.order_by("business_area__slug").values_list("role_id", flat=True)
        return RoleSerializer(Role.objects.filter(id__in=role_ids), many=True).data

    @staticmethod
    def get_user_roles(user: User) -> ReturnDict:
        role_ids = user.role_assignments.order_by("business_area__slug").values_list("role_id", flat=True)
        return RoleSerializer(Role.objects.filter(id__in=role_ids), many=True).data

    def get_permissions_in_scope(self, user: User) -> set:
        request = self.context.get("request", {})
        business_area_slug = request.query_params.get("business_area_slug")

        if program_slug := request.query_params.get("program_slug"):  # scope program
            if program := Program.objects.filter(slug=program_slug, business_area__slug=business_area_slug).first():
                return user.permissions_in_business_area(business_area_slug, program.id)
            return set()

        return user.permissions_in_business_area(business_area_slug)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ("first_name", "last_name", "email", "username")
