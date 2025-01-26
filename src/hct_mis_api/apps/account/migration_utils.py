from django.conf import settings
from django.db.models import Count
from django.db import migrations
from django.db.models import Q
from django.utils import timezone
from mptt import register

from hct_mis_api.apps.account.models import Role
from hct_mis_api.apps.account.permissions import DEFAULT_PERMISSIONS_LIST_FOR_IS_UNICEF_PARTNER


def migrate_user_roles_logic(apps):
    """
    Handle migration of user roles.
    UserRole model was replaced with RoleAssignment model, which includes a program field.
    After model update, existing UserRoles would have program=null, granting users access to all programs by default.
    This migration will fetch the programs for specific Business Areas from UserRole
    and create RoleAssignment entries for each program to preserve the original access.
    """
    RoleAssignment = apps.get_model('account', 'RoleAssignment')
    ProgramPartnerThrough = apps.get_model('program', 'ProgramPartnerThrough')

    # do not change UserRoles for Global as it can stay with program=None
    user_roles = RoleAssignment.objects.filter(
        user__isnull=False, program__isnull=True
    ).exclude(business_area__slug="global").select_related("user", "user__partner", "business_area")
    new_assignments = []
    updated_roles = []
    expiration_time = timezone.now()

    program_access_mapping = {
        (partner_id, business_area_id): list(ProgramPartnerThrough.objects.filter(
            partner_id=partner_id, program__business_area_id=business_area_id
        ).values_list('program', flat=True)) for partner_id, business_area_id in user_roles.values_list('user__partner_id', 'business_area_id').distinct()
    }

    for user_role in user_roles:
        user = user_role.user
        partner = user.partner
        business_area = user_role.business_area

        programs = program_access_mapping.get((partner.id, business_area.id), []) if partner else []

        if programs:
            user_role.program = programs[0]
            updated_roles.append(user_role)
            new_assignments.extend(
                RoleAssignment(
                    user=user,
                    partner=None,
                    role=user_role.role,
                    business_area=business_area,
                    program=program,
                    expiry_date=user_role.expiry_date
                ) for program in programs[1:]
            )
        else:
            # If user has no partner
            # or their partner does not have access to any program in the UserRole's Business Area,
            # make the user role inactive.
            # In another case, the user would gain access to all programs.
            user_role.expiry_date = expiration_time
            updated_roles.append(user_role)

    if updated_roles:
        RoleAssignment.objects.bulk_update(updated_roles, ["program", "expiry_date"])
    if new_assignments:
        RoleAssignment.objects.bulk_create(new_assignments)


def migrate_partner_roles_and_access_logic(apps):
    """
    Handle migration of partner roles and access.
    ProgramPartnerThrough and BusinessAreaPartnerThrough models need to be migrated into RoleAssignment model.
    For each combination of role in the BusinessAreaPartnerThrough and a program in the ProgramPartnerThrough,
    that partner has access to within the BA of the role -> the RoleAssignment entry needs to be created.

    Additionally, area access defined on areas filed in ProgramPartnerThrough needs to be moved to
    AdminAreaLimitedTo model and the logic needs changing - create records in the AdminAreaLimitedTo only
    if this is NOT a full-area-access - so if there are area limits applied.
    """
    RoleAssignment = apps.get_model('account', 'RoleAssignment')
    ProgramPartnerThrough = apps.get_model('program', 'ProgramPartnerThrough')
    BusinessAreaPartnerThrough = apps.get_model('core', 'BusinessAreaPartnerThrough')
    AdminAreaLimitedTo = apps.get_model('account', 'AdminAreaLimitedTo')
    Partner = apps.get_model('account', 'Partner')
    register(Partner)

    # do not create RoleAssignments for partners that are parents or UNICEF
    partner_roles = BusinessAreaPartnerThrough.objects.exclude(
        Q(partner_id__in=Partner.objects.filter(parent__isnull=False).values_list("parent_id", flat=True))
        | Q(partner__name="UNICEF")
    ).select_related("partner", "business_area").prefetch_related("roles")
    new_assignments = []
    new_area_limits = []

    program_access_mapping = {
        (partner_id, business_area_id): list(ProgramPartnerThrough.objects.filter(
            partner_id=partner_id, program__business_area_id=business_area_id
        ).values_list('program', flat=True)) for partner_id, business_area_id in partner_roles.values_list('partner_id', 'business_area_id').distinct()
    }

    for partner_role in partner_roles:
        partner = partner_role.partner
        business_area = partner_role.business_area
        roles = partner_role.roles.all()

        programs = program_access_mapping.get((partner.id, business_area.id), [])

        # Create RoleAssignments only if the partner has access to any program in the Business Area
        # of the BusinessAreaPartnerThrough
        if programs:
            new_assignments.extend(
                RoleAssignment(
                    user=None,
                    partner=partner,
                    role=role,
                    business_area=business_area,
                    program=program
                ) for role in roles for program in programs
            )

    if new_assignments:
        RoleAssignment.objects.bulk_create(new_assignments)

    # area limits - only for non-full-area-access; do not create records for partners that are parents
    area_access = ProgramPartnerThrough.objects.filter(full_area_access=False).exclude(
        partner_id__in=Partner.objects.filter(parent__isnull=False).values_list("parent_id", flat=True)
    ).select_related('partner', 'program').prefetch_related('areas')
    for access in area_access:
        new_area_limits.append(
            AdminAreaLimitedTo(
                partner=access.partner,
                program=access.program,
                areas=access.areas.all()
            )
        )
    if new_area_limits:
        AdminAreaLimitedTo.objects.bulk_create(new_area_limits)


def migrate_unicef_partners_logic(apps):
    """
    Handle migration of UNICEF partner into UNICEF HQ and UNICEF Partners per BusinessArea.
    UNICEF partner will become parent Partner for UNICEF HQ and UNICEF Partners per BusinessArea.

    UNICEF HQ will hold "Role with all permissions" for all Business Areas (with program=None so whole BA access)
    UNICEF Partners per BusinessArea will hold role with permissions specified in DEFAULT_PERMISSIONS_IS_UNICEF_PARTNER
    within the Business Area specific for them. Within this BA they will have access to all programs.

    Users currently assigned to UNICEF partner will be assigned to UNICEF HQ and UNICEF Partners per BusinessArea based on their roles.
    If user holds roles in multiple Business Areas, they will be assigned to UNICEF HQ.
    """
    RoleAssignment = apps.get_model('account', 'RoleAssignment')
    Partner = apps.get_model('account', 'Partner')
    BusinessArea = apps.get_model('core', 'BusinessArea')
    User = apps.get_model('account', 'User')
    register(Partner)

    new_assignments = []

    unicef_partner = Partner.objects.filter(name="UNICEF").first()

    # update Role with all permissions with is_available_for_partner=False
    role_with_all_permissions = Role.objects.filter(name="Role with all permissions").first()
    role_with_all_permissions.is_available_for_partner = False
    role_with_all_permissions.save()

    role_for_unicef_subpartners = Role.objects.create(
        name="Role for UNICEF Partners",
        is_visible_on_ui=False,
        is_available_for_partner=False,
        permissions=DEFAULT_PERMISSIONS_LIST_FOR_IS_UNICEF_PARTNER,
    )

    unicef_hq = Partner.objects.create(name=settings.UNICEF_HQ, parent=unicef_partner)
    unicef_hq.allowed_business_areas.set(BusinessArea.objects.all())

    for business_area in BusinessArea.objects.all():
        unicef_subpartner = Partner.objects.create(name=f"UNICEF Partner for {business_area.slug}", parent=unicef_partner)
        unicef_subpartner.allowed_business_areas.add(business_area)

        new_assignments.append(
            RoleAssignment(
                user=None,
                partner=unicef_subpartner,
                role=role_for_unicef_subpartners,
                business_area=business_area,
                program=None
            )
        )

        new_assignments.append(
            RoleAssignment(
                user=None,
                partner=unicef_hq,
                role=role_with_all_permissions,
                business_area=business_area,
                program=None
            )
        )

    if new_assignments:
        RoleAssignment.objects.bulk_create(new_assignments)


    # handle UNICEF users

    # UNICEF users with roles in multiple Business Areas will be assigned to UNICEF HQ
    User.objects.filter(partner=unicef_partner).annotate(
        ba_count=Count("role_assignments__business_area", distinct=True)
    ).filter(ba_count__gt=1).update(partner=unicef_hq)

    # UNICEF users with roles in single Business Area will be assigned to UNICEF Sub-partner for that Business Area
    unicef_users_in_single_ba = User.objects.filter(partner=unicef_partner).annotate(
        ba_count=Count("role_assignments__business_area", distinct=True)
    ).filter(ba_count=1)

    unicef_subpartners = {
        ba.slug: Partner.objects.get(name=f"UNICEF Sub-partner for {ba.name} [Sub-Partner of UNICEF]")
        for ba in BusinessArea.objects.all()
    }

    for ba in unicef_users_in_single_ba.values_list("role_assignments__business_area", flat=True).distinct():
        unicef_users = unicef_users_in_single_ba.filter(role_assignments__business_area=ba)
        unicef_users.update(partner=unicef_subpartners[ba])

    # UNICEF users with no roles will be assigned to default empty partner
    User.objects.filter(partner=unicef_partner).annotate(
        ba_count=Count("role_assignments__business_area", distinct=True)
    ).filter(ba_count=0).update(partner=settings.DEFAULT_EMPTY_PARTNER)
