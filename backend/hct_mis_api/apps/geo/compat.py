from django.db import models
from django.db.models import BLANK_CHOICE_DASH
from django.utils.functional import lazy

from .models import Country


class GeoCountryDescriptor:
    def __init__(self, field):
        self.field = field

    def __get__(self, instance=None, owner=None):
        if instance is None:
            return self
        # Check in case this field was deferred.
        if self.field.name not in instance.__dict__:
            instance.refresh_from_db(fields=[self.field.name])
        value = instance.__dict__[self.field.name]
        if self.field.multiple:
            return [self.country(code) for code in value]
        return self.country(value)

    def country(self, code) -> Country:
        return Country.objects.get(iso_code2=code)

    def __set__(self, instance, value):
        value = self.field.get_clean_value(value)
        instance.__dict__[self.field.name] = value


class GeoCountryField(models.CharField):
    descriptor_class = GeoCountryDescriptor

    def __init__(self, *args, **kwargs):
        self.multiple = kwargs.pop("multiple", None)
        self.blank_label = kwargs.pop("blank_label", None)
        kwargs["choices"] = [(None, None)]
        if "max_length" not in kwargs:
            if self.multiple:
                kwargs["max_length"] = len(self.countries) * 3 - 1
            else:
                kwargs["max_length"] = 2
        super().__init__(*args, **kwargs)

    def get_choices(self, include_blank=True, blank_choice=None, *args, **kwargs):
        # TODO: refactor
        if self.choices[0] == (None, None):  # type: ignore
            self.choices = Country.objects.all().values_list("iso_code2", "name")
        if blank_choice is None:
            if self.blank_label is None:
                blank_choice = BLANK_CHOICE_DASH
            else:
                blank_choice = [("", self.blank_label)]
        if self.multiple:
            include_blank = False
        return super().get_choices(include_blank=include_blank, blank_choice=blank_choice, *args, **kwargs)

    get_choices = lazy(get_choices, list)
