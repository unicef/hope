import enum
import json
import operator
import re
from typing import List

import factory
from django.template.defaultfilters import slugify
from household.models import Household

from . import models

_INTEGER = "INTEGER"
_SELECT_ONE = "SELECT_ONE"


def decode_id_string(id_string):
    if not id_string:
        return

    from base64 import b64decode

    return b64decode(id_string).decode().split(":")[1]


def unique_slugify(
    instance, value, slug_field_name="slug", queryset=None, slug_separator="-"
):
    """
    Calculates and stores a unique slug of ``value`` for an instance.

    ``slug_field_name`` should be a string matching the name of the field to
    store the slug in (and the field to check against for uniqueness).

    ``queryset`` usually doesn't need to be explicitly provided - it'll default
    to using the ``.all()`` queryset from the model's default manager.
    """
    slug_field = instance._meta.get_field(slug_field_name)

    slug = getattr(instance, slug_field.attname)
    slug_len = slug_field.max_length

    # Sort out the initial slug, limiting its length if necessary.
    slug = slugify(value)
    if slug_len:
        slug = slug[:slug_len]
    slug = _slug_strip(slug, slug_separator)
    original_slug = slug

    # Create the queryset if one wasn't explicitly provided and exclude the
    # current instance from the queryset.
    if queryset is None:
        queryset = instance.__class__._default_manager.all()
    if instance.pk:
        queryset = queryset.exclude(pk=instance.pk)

    # Find a unique slug. If one matches, at '-2' to the end and try again
    # (then '-3', etc).
    next = 2
    while not slug or queryset.filter(**{slug_field_name: slug}):
        slug = original_slug
        end = "%s%s" % (slug_separator, next)
        if slug_len and len(slug) + len(end) > slug_len:
            slug = slug[: slug_len - len(end)]
            slug = _slug_strip(slug, slug_separator)
        slug = "%s%s" % (slug, end)
        next += 1

    setattr(instance, slug_field.attname, slug)


def _slug_strip(value, separator="-"):
    """
    Cleans up a slug by removing slug separator characters that occur at the
    beginning or end of a slug.

    If an alternate separator is used, it will also replace any instances of
    the default '-' separator with the new separator.
    """
    separator = separator or ""
    if separator == "-" or not separator:
        re_sep = "-"
    else:
        re_sep = "(?:-|%s)" % re.escape(separator)
    # Remove multiple instances and if an alternate separator is provided,
    # replace the default '-' separator.
    if separator != re_sep:
        value = re.sub("%s+" % re_sep, separator, value)
    # Remove separator from the beginning and end of the slug.
    if separator:
        if separator != "-":
            re_sep = re.escape(separator)
        value = re.sub(r"^%s+|%s+$" % (re_sep, re_sep), "", value)
    return value


class EnumGetChoices(enum.Enum):
    """Subclasses Enum class for additional methods."""

    def __init__(self, *args, **kwargs):
        super().__init__()

    @classmethod
    def get_choices(cls) -> List[tuple]:
        return [(field.name, field.value) for field in cls]


class JSONFactory(factory.DictFactory):
    """A Json factory class to get JSON strings."""

    @classmethod
    def _generate(cls, create, attrs):
        obj_dict = super()._generate(create, attrs)
        return json.dumps(obj_dict)


# TODO(codecakes): make it dynamic when possible.
def get_core_fields() -> List:
    """Gets list of flex metadatatype objects. """

    get_item_fn = operator.itemgetter(1)
    associated_with = models.FlexibleAttribute.ASSOCIATED_WITH_CHOICES

    return [
        {
            "id": "05c6be72-22ac-401b-9d3f-0a7e7352aa87",
            "type": _INTEGER,
            "name": "years_in_school",
            "label": {"English(EN)": "years in school"},
            "hint": "number of years spent in school",
            "required": True,
            "choices": [],
            "associated_with": get_item_fn(associated_with[1]),
        },
        {
            "id": "a1741e3c-0e24-4a60-8d2f-463943abaebb",
            "type": _INTEGER,
            "name": "age",
            "label": {"English(EN)": "age"},
            "hint": "age in years",
            "required": True,
            "choices": [],
            "associated_with": get_item_fn(associated_with[1]),
        },
        {
            "id": "d6aa9669-ae82-4e3c-adfe-79b5d95d0754",
            "type": _INTEGER,
            "name": "family_size",
            "label": {"English(EN)": "Family Size"},
            "hint": "how many persons in the household",
            "required": True,
            "choices": [],
            "associated_with": get_item_fn(associated_with[0]),
        },
        {
            "id": "3c2473d6-1e81-4025-86c7-e8036dd92f4b",
            "type": _SELECT_ONE,
            "name": "residence_status",
            "required": True,
            "label": {"English(EN)": "Residence Status"},
            "hint": "residential status of household",
            "choices": [
                {"name": name, "label": str(value)}
                for name, value in Household.RESIDENCE_STATUS_CHOICE
            ],
            "associated_with": get_item_fn(associated_with[0]),
        },
    ]
