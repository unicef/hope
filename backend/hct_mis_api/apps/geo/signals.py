from typing import Any

from django.db.models.signals import post_save
from django.dispatch import receiver

from hct_mis_api.apps.geo.models import Area
from hct_mis_api.apps.program.models import ProgramPartnerThrough


@receiver(post_save, sender=Area)
def handle_add_area_to_full_area_access_program_partner(
    sender: Any, instance: Area, created: bool, **kwargs: Any
) -> None:
    if created:
        business_areas = instance.area_type.country.business_areas.all()
        for business_area in business_areas:
            for program_partner in ProgramPartnerThrough.objects.filter(
                full_area_access=True, program__in=business_area.program_set.all()
            ):
                program_partner.areas.add(instance)
