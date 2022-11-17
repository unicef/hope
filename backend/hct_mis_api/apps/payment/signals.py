from django.db.models.signals import post_save
from django.dispatch import receiver

from hct_mis_api.apps.payment.celery_tasks import (
    create_individuals_payment_channels_for_new_delivery_mechanism,
)
from hct_mis_api.apps.payment.models import DeliveryMechanism


@receiver(post_save, sender=DeliveryMechanism)
def post_save_delivery_mechanism(sender, instance, created, *args, **kwargs):
    # TODO maybe we should move to DeliveryMechanismAdmin button
    # TODO what about Update?
    if created:
        create_individuals_payment_channels_for_new_delivery_mechanism.delay(instance.id)
