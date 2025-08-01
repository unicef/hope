from rest_framework import serializers

from hct_mis_api.contrib.aurora.models import Organization, Project, Registration


class OrganizationSerializer(serializers.ModelSerializer):
    aurora_id = serializers.ReadOnlyField(source="source_id")
    hope_id = serializers.SerializerMethodField()

    class Meta:
        model = Organization
        fields = ("aurora_id", "hope_id", "name")

    def get_hope_id(self, obj: Organization) -> str | None:
        return str(obj.business_area.pk) if obj.business_area else None


class ProjectSerializer(serializers.ModelSerializer):
    organization = serializers.ReadOnlyField(source="organization.slug")
    aurora_id = serializers.ReadOnlyField(source="source_id")
    hope_id = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = ("organization", "aurora_id", "hope_id", "name")

    def get_hope_id(self, obj: Project) -> str | None:
        return str(obj.programme.pk) if obj.programme else None


class RegistrationSerializer(serializers.ModelSerializer):
    organization = serializers.ReadOnlyField(source="project.organization.slug")
    aurora_id = serializers.ReadOnlyField(source="source_id")
    project = serializers.SerializerMethodField()

    class Meta:
        model = Registration
        fields = ("organization", "aurora_id", "project", "name")

    def get_project(self, obj: Registration) -> str:
        return str(obj.project.pk)
