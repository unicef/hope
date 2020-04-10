import concurrent.futures as concurrent_futures
import datetime as dt
import functools
import json
import re
from typing import List

import django
import factory
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.template.defaultfilters import slugify
import datetime as dt


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


class JSONFactory(factory.DictFactory):
    """A Json factory class to get JSON strings."""

    @classmethod
    def _generate(cls, create, attrs):
        obj_dict = super()._generate(create, attrs)
        return json.dumps(obj_dict)


def update_model(model: django.db.models.Model, changeset: dict):
    for attrib, value in changeset.items():
        if hasattr(model, attrib):
            setattr(model, attrib, value)
    model.save()


def filter_relational_fields(model: django.db.models.Model) -> list:
    """Get Only Relational Fields."""
    return list(
        filter(
            lambda field: field not in model._meta.fields,
            model._meta.get_fields(),
        )
    )


def set_field_object_association(
    from_model: django.db.models.Model,
    to_model: django.db.models.Model,
    field: django.db.models.Field,
):
    """Adds an association field to a model from another model.

    Args:
        from_model (django.db.models.Model): The model to copy associated field from.
        to_model (django.db.models.Model): The model to copy associated field to.
        field (django.db.models.Field): The Field value(s) to copy.
    """
    from_model_foreign_relation_set = getattr(from_model, field.name)
    to_model_foreign_relation_set = getattr(to_model, field.name)
    to_model_foreign_relation_set.set(from_model_foreign_relation_set.all())


def copy_associations_async(
    from_model: django.db.models.Model,
    to_model: django.db.models.Model,
    exclude_foreign_fields: list,
) -> django.db.models.Model:
    """Copy reverse and M2M associations concurrently.

    Args:
        from_model (django.db.models.Model): The model to copy associated field from.
        to_model (django.db.models.Model): The model to copy associated field to.
        field (django.db.models.Field): The Field value(s) to copy.
        exclude_foreign_fields (List[django.db.models.Field]): List of relatable field value(s) to copy.

    Returns:
        The updated model to copy associations to.
    """
    set_assocation_partial_fn = functools.partial(
        set_field_object_association, from_model, to_model
    )
    # You can't use context manager. See Why: graphene/relay/mutation.py line 70
    executor = concurrent_futures.ThreadPoolExecutor(
        max_workers=len(exclude_foreign_fields)
    )
    _results = list(
        executor.map(set_assocation_partial_fn, exclude_foreign_fields,)
    )
    executor.shutdown(wait=True)
    return to_model


def get_choices_values(choices):
    return tuple(
        choice[0] if isinstance(choice, tuple) else choice for choice in choices
    )


def serialize_flex_attributes():
    """
    Flexible Attributes objects to dict mapping:
        "individuals": {
            "id_type_i_f": {
                "type": "SINGLE_CHOICE",
                "choices": (
                    ("BIRTH_CERTIFICATE", "Birth Certificate"),
                    ("DRIVERS_LICENSE", "Driver's License"),
                    ("UNHCR_ID", "UNHCR ID"),
                    ("NATIONAL_ID", "National ID"),
                    ("NATIONAL_PASSPORT", "National Passport"),
                    ("OTHER", "Other"),
                    ("NOT_AVAILABLE", "Not Available"),
                ),
            },
        },
        "households": {
            "assistance_type_h_f": {
                "type": "MULTIPLE_CHOICE",
                "choices": (
                    (1, "Option 1"),
                    (2, "Option 2"),
                    (3, "Option 3"),
                    (4, "Option 4"),
                    (5, "Option 5"),
                    (6, "Option 6"),
                    (7, "Option 7"),
                ),
            },
        }
    """
    from core.models import FlexibleAttribute

    flex_attributes = FlexibleAttribute.objects.all()

    result_dict = {
        "individuals": {},
        "households": {},
    }

    for attr in flex_attributes:
        associated_with = (
            "households" if attr.associated_with == 0 else "individuals"
        )

        result_dict[associated_with][attr.name] = {
            "type": attr.type,
            "choices": list(attr.choices.values_list("name", flat=True)),
        }
    return result_dict


def age_to_dob_range_query(field_name, age_min, age_max):
    query_dict = {}
    this_year = dt.date.today().year
    if age_min == age_max and age_min is not None:
        return Q(**{f"{field_name}__year": this_year - age_min})
    if age_min:
        query_dict[f"{field_name}__year__lte"] = this_year - age_min
    if age_max:
        query_dict[f"{field_name}__year__gte"] = this_year - age_max
    return Q(**query_dict)


def age_to_dob_query(comparision_method, args):
    field_name = "individuals__dob"
    comparision_method_args_count = {
        "RANGE": 2,
        "NOT_IN_RANGE": 2,
        "EQUALS": 1,
        "NOT_EQUALS": 1,
        "GREATER_THAN": 1,
        "LESS_THAN": 1,
    }
    args_count = comparision_method_args_count.get(comparision_method)
    if args_count is None:
        raise ValidationError(
            f"Age filter query don't supports {comparision_method} type"
        )
    if len(args) != args_count:
        raise ValidationError(
            f"Age {comparision_method} filter query expect {args_count} arguments"
        )
    if comparision_method == "RANGE":
        return age_to_dob_range_query(field_name, *args)
    if comparision_method == "NOT_IN_RANGE":
        return ~(age_to_dob_range_query(field_name, *args))
    if comparision_method == "EQUALS":
        return age_to_dob_range_query(field_name, args[0], args[0])
    if comparision_method == "NOT_EQUALS":
        return ~(age_to_dob_range_query(field_name, args[0], args[0]))
    if comparision_method == "GREATER_THAN":
        return age_to_dob_range_query(field_name, args[0], None)
    if comparision_method == "LESS_THAN":
        return age_to_dob_range_query(field_name, None, args[0])
    raise ValidationError(
        f"Age filter query don't supports {comparision_method} type"
    )


def get_attr_value(name, object, default=None):
    if isinstance(object, dict):
        return object.get(name, default)
    return getattr(name, object, default)
