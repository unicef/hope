from typing import TYPE_CHECKING
from uuid import UUID

from django.db.models import QuerySet

if TYPE_CHECKING:
    from hope.apps.account.models import Partner
    from hope.apps.geo.models import Area


class VisibilityBackend:
    """Visibility backend that checks if the user has access to a specific area within a program."""

    @classmethod
    def has_area_access(cls, partner: "Partner", area_id: str | UUID, program_id: str | UUID) -> bool:
        area_limits = cls.get_area_limits_for_program(partner, program_id)
        return not area_limits.exists() or area_limits.filter(id=area_id).exists()

    @classmethod
    def has_area_limits_in_program(cls, partner: "Partner", program_id: str | UUID) -> bool:
        return cls.get_area_limits_for_program(partner, program_id).exists()

    @classmethod
    def get_areas_for_program(cls, partner: "Partner", program_id: str | UUID) -> QuerySet["Area"]:
        from hope.apps.geo.models import Area

        area_limits = cls.get_area_limits_for_program(partner, program_id)
        return area_limits or Area.objects.filter(area_type__country__business_areas__program__id=program_id)

    @classmethod
    def get_area_limits_for_program(cls, partner: "Partner", program_id: str | UUID) -> QuerySet["Area"]:
        from hope.apps.account.models import AdminAreaLimitedTo
        from hope.apps.geo.models import Area

        area_limits = AdminAreaLimitedTo.objects.filter(partner=partner, program_id=program_id)
        return Area.objects.filter(admin_area_limits__in=area_limits)
