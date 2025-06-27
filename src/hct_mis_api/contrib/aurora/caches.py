from typing import Any

from rest_framework_extensions.key_constructor.bits import KeyBitBase

from hct_mis_api.api.caches import KeyConstructorMixin, get_or_create_cache_key
from hct_mis_api.contrib.aurora.models import Organization, Project, Registration


class OrganizationListVersionsKeyBit(KeyBitBase):
    specific_view_cache_key = "aurora_organization_list"

    def get_data(
        self, params: Any, view_instance: Any, view_method: Any, request: Any, args: tuple, kwargs: dict
    ) -> str:
        version_key = f"{self.specific_view_cache_key}:{Organization.objects.latest('updated_at').updated_at}:{Organization.objects.all().count()}"
        version = get_or_create_cache_key(version_key, version_key)
        return str(version)


class ProjectListVersionsKeyBit(KeyBitBase):
    specific_view_cache_key = "aurora_project_list"

    def get_data(
        self, params: Any, view_instance: Any, view_method: Any, request: Any, args: tuple, kwargs: dict
    ) -> str:
        version_key = f"{self.specific_view_cache_key}:{Project.objects.latest('updated_at').updated_at}:{Project.objects.all().count()}"
        version = get_or_create_cache_key(version_key, version_key)
        return str(version)


class RegistrationListVersionsKeyBit(KeyBitBase):
    specific_view_cache_key = "aurora_registration_list"

    def get_data(
        self, params: Any, view_instance: Any, view_method: Any, request: Any, args: tuple, kwargs: dict
    ) -> str:
        version_key = f"{self.specific_view_cache_key}:{Registration.objects.latest('updated_at').updated_at}:{Registration.objects.all().count()}"
        version = get_or_create_cache_key(version_key, version_key)
        return str(version)


class AuroraKeyConstructor(KeyConstructorMixin):
    organization_list_versions = OrganizationListVersionsKeyBit()
    project_list_versions = ProjectListVersionsKeyBit()
    registration_list_versions = RegistrationListVersionsKeyBit()
