from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField
from sorl.thumbnail import ImageField

from hct_mis_api.apps.household.const import NATIONALITIES
from hct_mis_api.apps.utils.models import TimeStampedUUIDModel


class Household(TimeStampedUUIDModel):
    RESIDENCE_STATUS_CHOICE = (
        ('REFUGEE', _('Refugee')),
        ('MIGRANT', _('Migrant')),
        ('CITIZEN', _('Citizen')),
        ('IDP', _('IDP')),
        ('OTHER', _('Other')),
    )

    household_ca_id = models.CharField(max_length=255)
    consent = ImageField()
    residence_status = models.CharField(
        max_length=255,
        choices=RESIDENCE_STATUS_CHOICE,
    )
    nationality = models.CharField(
        max_length=255,
        choices=NATIONALITIES,
    )
    family_size = models.PositiveIntegerField(blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    location = models.ForeignKey('core.Location', related_name='households', on_delete=models.CASCADE)
    registration_data_import_id = models.ForeignKey('RegistrationDataImport', related_name='households',
                                                    on_delete=models.CASCADE)


class Individual(TimeStampedUUIDModel):
    SEX_CHOICE = (
        ('MALE', _('Male')),
        ('FEMALE', _('Female')),
    )
    MARTIAL_STATUS_CHOICE = (
        ('SINGLE', _('SINGLE')),
        ('MARRIED', _('Married')),
        ('WIDOW', _('Widow')),
        ('DIVORCED', _('Divorced')),
        ('SEPARATED', _('Separated')),
    )
    # N/A, Birth Certificate, Driving License, UNHCR ID card, National ID, National Passport
    IDENTIFICATION_TYPE_CHOICE = (
        ('NA', _('N/A')),
        ('BIRTH_CERTIFICATE', _('Birth Certificate')),
        ('DRIVING_LICENSE', _('Driving License')),
        ('UNHCR_ID_CARD', _('UNHCR ID card')),
        ('NATIONAL_ID', _('National ID')),
        ('NATIONAL_PASSPORT', _('National Passport')),
    )
    individual_ca_id = models.CharField(max_length=255)
    full_name = models.CharField(max_length=255)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    sex = models.CharField(
        max_length=255,
        choices=SEX_CHOICE,
    )
    dob = models.DateField(blank=True, null=True)
    estimated_dob = models.DateField(blank=True, null=True)
    nationality = models.CharField(
        max_length=255,
        choices=NATIONALITIES,
    )
    martial_status = models.CharField(
        max_length=255,
        choices=MARTIAL_STATUS_CHOICE,
    )
    phone_number = PhoneNumberField(blank=True)
    identification_type = models.CharField(
        max_length=255,
        choices=IDENTIFICATION_TYPE_CHOICE,
    )
    identification_number = models.CharField(max_length=255)
    household = models.ForeignKey('Household', related_name='individuals', on_delete=models.CASCADE)
    registration_data_import_id = models.ForeignKey('RegistrationDataImport', related_name='individuals',
                                                    on_delete=models.CASCADE)

    def __str__(self):
        return self.full_name


class RegistrationDataImport(TimeStampedUUIDModel):
    IN_PROGRESS = 'IN_PROGRESS'
    DONE = 'DONE'
    STATUS_CHOICE = (
        IN_PROGRESS, _('In progress'),
        DONE, _('Done'),
    )
    DATA_SOURCE_CHOICE = (
        ('XLS', 'Excel'),
        ('3RD_PARTY', '3rd party'),
        ('XML', 'XML'),
        ('OTHER', 'Other'),
    )
    name = models.CharField(max_length=255)
    status = models.CharField(
        max_length=255,
        choices=STATUS_CHOICE,
    )
    import_date = models.DateTimeField()
    imported_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='registration_data_imports',
                                    on_delete=models.CASCADE)
    data_source = models.CharField(
        max_length=255,
        choices=DATA_SOURCE_CHOICE,
    )
    number_of_individuals = models.PositiveIntegerField()
    number_of_households = models.PositiveIntegerField()

    def __str__(self):
        return self.name
