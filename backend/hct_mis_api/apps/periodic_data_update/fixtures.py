from factory.django import DjangoModelFactory

from hct_mis_api.apps.periodic_data_update.models import PeriodicDataUpdateTemplate, PeriodicDataUpdateUpload


class PeriodicDataUpdateTemplateFactory(DjangoModelFactory):
    class Meta:
        model = PeriodicDataUpdateTemplate


class PeriodicDataUpdateTemplateFactory(DjangoModelFactory):
    class Meta:
        model = PeriodicDataUpdateUpload