from typing import Any, Iterable

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.cache import cache
from django.db.models import Q
from django.db.models.signals import m2m_changed, post_save, pre_delete, pre_save
from django.dispatch import receiver
from django.utils import timezone

from hct_mis_api.api.caches import get_or_create_cache_key
from hct_mis_api.apps.account.caches import get_user_permissions_version_key
from hct_mis_api.apps.account.models import Partner, Role, RoleAssignment, User
from hct_mis_api.apps.core.models import BusinessArea


@receiver(post_save, sender=RoleAssignment)
@receiver(pre_delete, sender=RoleAssignment)
def post_save_pre_delete_role_assignment(sender: Any, instance: User, *args: Any, **kwargs: Any) -> None:
    if instance.user:
        instance.user.last_modify_date = timezone.now()
        instance.user.save()


@receiver(pre_save, sender=get_user_model())
def pre_save_user(sender: Any, instance: User, *args: Any, **kwargs: Any) -> None:
    instance.last_modify_date = timezone.now()


@receiver(post_save, sender=get_user_model())
def post_save_user(sender: Any, instance: User, created: bool, *args: Any, **kwargs: Any) -> None:
    if created is False:
        return

    business_area = BusinessArea.objects.filter(slug="global").first()
    role = Role.objects.filter(name="Basic User").first()
    if business_area and role:
        RoleAssignment.objects.get_or_create(business_area=business_area, user=instance, role=role)


@receiver(m2m_changed, sender=Partner.allowed_business_areas.through)
def allowed_business_areas_changed(sender: Any, instance: Partner, action: str, pk_set: set, **kwargs: Any) -> None:
    if action == "post_remove":
        removed_business_areas_ids = pk_set
        RoleAssignment.objects.filter(partner=instance, business_area_id__in=removed_business_areas_ids).delete()

    elif action == "pre_clear":
        instance._removed_business_areas = list(instance.allowed_business_areas.all())

    elif action == "post_clear":
        removed_business_areas = getattr(instance, "_removed_business_areas", [])
        RoleAssignment.objects.filter(partner=instance, business_area__in=removed_business_areas).delete()


# Signals for permissions caches invalidation


def _invalidate_user_permissions_cache(users: Iterable) -> None:
    for user in users:
        version_key = get_user_permissions_version_key(user)
        get_or_create_cache_key(version_key, 0)
        cache.incr(version_key)


@receiver(post_save, sender=RoleAssignment)
@receiver(pre_delete, sender=RoleAssignment)
def invalidate_permissions_cache_on_role_assignment_change(
    sender: Any, instance: RoleAssignment, **kwargs: Any
) -> None:
    """
    Invalidate the cache for the User/Partner's Users associated with the RoleAssignment
    when the RoleAssignment is created, updated, or deleted.
    """
    if instance.user:
        users = [instance.user]
    else:
        users = instance.partner.user_set.all()
    _invalidate_user_permissions_cache(users)


@receiver(post_save, sender=Role)
@receiver(pre_delete, sender=Role)
def invalidate_permissions_cache_on_role_change(sender: Any, instance: Role, **kwargs: Any) -> None:
    """
    Invalidate the cache for the User/Partner's Users associated with the Role through a RoleAssignment
    when the Role is created, updated, or deleted.
    """
    users = User.objects.filter(
        Q(role_assignments__role=instance) | Q(partner__role_assignments__role=instance)
    ).distinct()
    _invalidate_user_permissions_cache(users)


@receiver(m2m_changed, sender=Group.permissions.through)
def invalidate_permissions_cache_on_group_permissions_change(
    sender: Any, instance: Group, action: str, **kwargs: Any
) -> None:
    """
    Invalidate the cache for all Users that are assigned to that Group
    or are assigned to this Group's RoleAssignment
    or their Partner is assigned to this Group's RoleAssignment
    when the Group's permissions are updated.
    """
    if action in ["post_add", "post_remove", "post_clear"]:
        users = User.objects.filter(
            Q(groups=instance) | Q(role_assignments__group=instance) | Q(partner__role_assignments__group=instance)
        ).distinct()
        _invalidate_user_permissions_cache(users)


@receiver(post_save, sender=Group)
@receiver(pre_delete, sender=Group)
def invalidate_permissions_cache_on_group_change(sender: Any, instance: Group, **kwargs: Any) -> None:
    """
    Invalidate the cache for all Users that are assigned to that Group
    or are assigned to this Group's RoleAssignment
    or their Partner is assigned to this Group's RoleAssignment
    when the Group is created, updated, or deleted.
    """
    users = User.objects.filter(
        Q(groups=instance) | Q(role_assignments__group=instance) | Q(partner__role_assignments__group=instance)
    ).distinct()
    _invalidate_user_permissions_cache(users)


@receiver(m2m_changed, sender=User.groups.through)
def invalidate_permissions_cache_on_user_groups_change(action: str, instance: User, pk_set: set, **kwargs: Any) -> None:
    """
    Invalidate the cache for a User when their Groups are modified.
    """
    if action in {"post_add", "post_remove", "post_clear"}:
        _invalidate_user_permissions_cache([instance])


@receiver(post_save, sender=User)
@receiver(pre_delete, sender=User)
def invalidate_permissions_cache_on_user_change(sender: Any, instance: User, **kwargs: Any) -> None:
    """
    Invalidate the cache for a User when they are updated. (For example change of partner or is_superuser flag)
    """
    _invalidate_user_permissions_cache([instance])
