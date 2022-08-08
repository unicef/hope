from datetime import timezone

from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, pre_delete, pre_save
from django.dispatch import receiver

from hct_mis_api.apps.account.models import UserRole, Role
from hct_mis_api.apps.core.models import BusinessArea


@receiver(post_save, sender=UserRole)
def post_save_userrole(sender, instance, *args, **kwargs):
    instance.user.last_modify_date = timezone.now()
    instance.user.save()


@receiver(pre_delete, sender=UserRole)
def pre_delete_userrole(sender, instance, *args, **kwargs):
    instance.user.last_modify_date = timezone.now()
    instance.user.save()


@receiver(pre_save, sender=get_user_model())
def pre_save_user(sender, instance, *args, **kwargs):
    instance.available_for_export = True
    instance.last_modify_date = timezone.now()


@receiver(post_save, sender=get_user_model())
def post_save_user(sender, instance, created, *args, **kwargs):
    if created is False:
        return

    business_area = BusinessArea.objects.filter(slug="global").first()
    role = Role.objects.filter(name="Basic User").first()
    if business_area and role:
        UserRole.objects.get_or_create(business_area=business_area, user=instance, role=role)
