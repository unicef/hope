import datetime as dt
import re

from django.core.exceptions import ValidationError
from django.db.models import Q, F
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


def get_choices_values(choices):
    return tuple(
        choice[0] if isinstance(choice, tuple) else choice for choice in choices
    )


def serialize_flex_attributes():
    """
    Flexible Attributes objects to dict mapping:
        "individuals": {
            "test_i_f": {
                "id": "a1741e3c-0e24-4a60-8d2f-463943abaebb",
                "type": "SELECT_ONE",
                "name": "test_i_f",
                "lookup": "test_i_f",
                "required": True,
                "label": {
                    "English(EN)": "This is test label"
                },
                "hint": "",
                "choices": [
                    {
                        "English(EN)": "Yes",
                        "value": 0
                    }
                ],
                "associated_with": Individual,
            },
        },
        "households": {
            "test_h_f": {
                "id": "a1741e3c-0e24-4a60-8d2f-463943abaebb",
                "type": "SELECT_ONE",
                "name": "test_h_f",
                "lookup": "test_h_f",
                "required": True,
                "label": {
                    "English(EN)": "This is test label"
                },
                "hint": "",
                "choices": [
                    {
                        "English(EN)": "Yes",
                        "value": 0
                    }
                ],
                "associated_with": Household,
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
            "Household" if attr.associated_with == 0 else "Individual"
        )
        dict_key = associated_with.lower() + "s"

        result_dict[dict_key][attr.name] = {
            "id": attr.id,
            "type": attr.type,
            "name": attr.name,
            "lookup": attr.name,
            "required": attr.required,
            "label": attr.label,
            "hint": attr.hint,
            "choices": list(attr.choices.values("label", value=F("name"))),
            "associated_with": associated_with,
        }

    return result_dict


def get_combined_attributes():
    from core.core_fields_attributes import (
        CORE_FIELDS_SEPARATED_WITH_NAME_AS_KEY,
    )

    flex_attrs = serialize_flex_attributes()
    return {
        **CORE_FIELDS_SEPARATED_WITH_NAME_AS_KEY["individuals"],
        **flex_attrs["individuals"],
        **CORE_FIELDS_SEPARATED_WITH_NAME_AS_KEY["households"],
        **flex_attrs["households"],
    }


def age_to_birth_date_range_query(field_name, age_min, age_max):
    query_dict = {}
    this_year = dt.date.today().year
    if age_min == age_max and age_min is not None:
        return Q(**{f"{field_name}__year": this_year - age_min})
    if age_min:
        query_dict[f"{field_name}__year__lte"] = this_year - age_min
    if age_max:
        query_dict[f"{field_name}__year__gte"] = this_year - age_max
    return Q(**query_dict)


def age_to_birth_date_query(comparision_method, args):
    field_name = "individuals__birth_date"
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
        return age_to_birth_date_range_query(field_name, *args)
    if comparision_method == "NOT_IN_RANGE":
        return ~(age_to_birth_date_range_query(field_name, *args))
    if comparision_method == "EQUALS":
        return age_to_birth_date_range_query(field_name, args[0], args[0])
    if comparision_method == "NOT_EQUALS":
        return ~(age_to_birth_date_range_query(field_name, args[0], args[0]))
    if comparision_method == "GREATER_THAN":
        return age_to_birth_date_range_query(field_name, args[0], None)
    if comparision_method == "LESS_THAN":
        return age_to_birth_date_range_query(field_name, None, args[0])
    raise ValidationError(
        f"Age filter query don't supports {comparision_method} type"
    )


def get_attr_value(name, object, default=None):
    if isinstance(object, dict):
        return object.get(name, default)
    return getattr(object, name, default)


def to_choice_object(choices):
    return [{"name": name, "value": value} for value, name in choices]


def get_admin_areas_as_choices(admin_level):
    from core.models import AdminArea

    return [
        {"label": {"English(EN)": admin_area.title}, "value": admin_area.title,}
        for admin_area in AdminArea.objects.filter(
            admin_area_type__admin_level=admin_level
        )
    ]
