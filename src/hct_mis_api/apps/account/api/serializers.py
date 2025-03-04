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

    def get_permissions(self, obj: BusinessArea) -> list:
        user = self.context["request"].user
        if user:
            return user.permissions_in_business_area(obj.slug)
        return []

    def get_is_accountability_applicable(self, obj: BusinessArea) -> bool:
        return all([bool(flag_state("ALLOW_ACCOUNTABILITY_MODULE")), obj.is_accountability_applicable])

    class Meta:
        model = BusinessArea
        fields = (
            "id",
            "name",
            "slug",
            "permissions",
            "is_accountability_applicable",
        )


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        exclude = ("id",)


class ProfileSerializer(serializers.ModelSerializer):
    permissions_in_scope = serializers.SerializerMethodField()
    business_areas = serializers.SerializerMethodField()
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

    def get_business_areas(self, user: User) -> ReturnDict:
        return UserBusinessAreaSerializer(
            user.business_areas, many=True, context={"request": self.context.get("request", {})}
        ).data

    @staticmethod
    def get_partner_roles(user: User) -> ReturnDict:
        role_ids = list(user.partner.role_assignments.order_by("business_area__slug").values_list("role_id", flat=True))
        return RoleSerializer(Role.objects.filter(id__in=role_ids), many=True).data

    @staticmethod
    def get_user_roles(user: User) -> ReturnDict:
        role_ids = list(user.role_assignments.order_by("business_area__slug").values_list("role_id", flat=True))
        return RoleSerializer(Role.objects.filter(id__in=role_ids), many=True).data

    def get_permissions_in_scope(self, user: User) -> set:
        request = self.context.get("request", {})
        business_area_slug = request.parser_context.get("kwargs", {}).get("business_area_slug")
        programme_code = request.parser_context.get("kwargs", {}).get("program_programme_code")
        program_id = Program.objects.get(programme_code=programme_code, business_area__slug=business_area_slug).id
        return user.permissions_in_business_area(business_area_slug, program_id)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ("first_name", "last_name", "email", "username")
