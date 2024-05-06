from typing import Dict

from django.conf import settings

from hct_mis_api.apps.account.models import Partner, Role
from hct_mis_api.apps.core.models import BusinessArea, BusinessAreaPartnerThrough
from hct_mis_api.apps.geo.models import Area
from hct_mis_api.apps.program.models import Program, ProgramPartnerThrough

"""
permissions structure
{
    "business_area_id": {
        "roles": ["role_id_1", "role_id_2"],
        "programs": {"program_id": ["admin_id"]}
    }
}
"""


def migrate_partner_permissions_and_access() -> None:
    for partner in Partner.objects.exclude(name=settings.DEFAULT_EMPTY_PARTNER):
        if partner.is_unicef:
            migrate_unicef_access(partner)
        else:
            roles_dict, access_dict = get_partner_data(partner.permissions)
            migrate_partner_permissions(partner, roles_dict)
            migrate_partner_access(partner, access_dict)


def get_partner_data(permissions_dict: Dict) -> tuple[Dict, Dict]:
    roles_dict = {}
    access_dict = {}
    for business_area_id, perm_in_business_area in permissions_dict.items():
        roles_dict[business_area_id] = perm_in_business_area.get("roles")
        if perm_in_business_area.get("programs"):
            for program_id, admin_ids in perm_in_business_area.get("programs", {}).items():
                access_dict[program_id] = admin_ids
    return roles_dict, access_dict


def migrate_partner_permissions(partner: Partner, roles_dict: Dict) -> None:
    for business_area_id, roles in roles_dict.items():
        roles = Role.objects.filter(id__in=roles)
        if roles:
            ba_partner_through, _ = BusinessAreaPartnerThrough.objects.get_or_create(
                partner=partner, business_area_id=business_area_id
            )
            ba_partner_through.roles.set(roles)


def migrate_partner_access(partner: Partner, access_dict: Dict) -> None:
    for program_id, admin_ids in access_dict.items():
        program = Program.objects.filter(id=program_id).first()
        if admin_ids:
            areas = Area.objects.filter(id__in=admin_ids)
        else:
            areas = Area.objects.filter(area_type__country__business_areas=program.business_area)
        if program and areas:
            program_partner_through, _ = ProgramPartnerThrough.objects.get_or_create(
                partner=partner, program_id=program_id
            )
            program_partner_through.areas.set(areas)


def migrate_unicef_access(partner: Partner) -> None:
    for ba in BusinessArea.objects.all():
        areas = Area.objects.filter(area_type__country__business_areas=ba)
        for program in Program.objects.filter(business_area=ba):
            program_partner_through, _ = ProgramPartnerThrough.objects.get_or_create(partner=partner, program=program)
            program_partner_through.areas.set(areas)
