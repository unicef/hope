import datetime as dt
import re
from collections import MutableMapping
from typing import List

from django.core.exceptions import ValidationError
from django.db.models import Q, F, Model
from django.forms import model_to_dict
from django.template.defaultfilters import slugify


class CaseInsensitiveTuple(tuple):
    def __contains__(self, key, *args, **kwargs):
        return key.casefold() in (element.casefold() for element in self)


class LazyEvalMethodsDict(MutableMapping):
    def __init__(self, *args, **kwargs):
        self._dict = dict(*args, **kwargs)

    def __getitem__(self, k):
        v = self._dict.__getitem__(k)
        if callable(v):
            v = v()
            self.__setitem__(k, v)
        return v

    def __setitem__(self, key, value):
        self._dict[key] = value

    def __delitem__(self, key):
        return self._dict[key]

    def __iter__(self):
        return iter(self._dict)

    def __len__(self):
        return len(self._dict)


def decode_id_string(id_string):
    if not id_string:
        return

    from base64 import b64decode

    return b64decode(id_string).decode().split(":")[1]


def encode_id_base64(id_string, model_name):
    if not id_string:
        return

    from base64 import b64encode

    return b64encode(f"{model_name}Node:{str(id_string)}".encode("utf-8")).decode()


def unique_slugify(instance, value, slug_field_name="slug", queryset=None, slug_separator="-"):
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
        associated_with = "Household" if attr.associated_with == 0 else "Individual"
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
    from core.core_fields_attributes import CORE_FIELDS_SEPARATED_WITH_NAME_AS_KEY

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
    if age_min is not None:
        query_dict[f"{field_name}__year__lte"] = this_year - age_min
    if age_max is not None:
        query_dict[f"{field_name}__year__gte"] = this_year - age_max
    return Q(**query_dict)


def age_to_birth_date_query(comparision_method, args, rule_filter):
    field_name = f"{'individuals' if rule_filter.head_of_household else 'head_of_household'}__birth_date"
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
        raise ValidationError(f"Age filter query don't supports {comparision_method} type")
    if len(args) != args_count:
        raise ValidationError(f"Age {comparision_method} filter query expect {args_count} arguments")
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
    raise ValidationError(f"Age filter query don't supports {comparision_method} type")


def get_attr_value(name, object, default=None):
    if isinstance(object, dict):
        return object.get(name, default)
    return getattr(object, name, default)


def to_choice_object(choices):
    return [{"name": name, "value": value} for value, name in choices]


def rename_dict_keys(obj, convert_func):
    if isinstance(obj, dict):
        new = {}
        for k, v in obj.items():
            new[convert_func(k)] = rename_dict_keys(v, convert_func)
    elif isinstance(obj, list):
        new = []
        for v in obj:
            new.append(rename_dict_keys(v, convert_func))
    else:
        return obj
    return new


raise_attribute_error = object()


def nested_getattr(obj, attr, default=raise_attribute_error):
    import functools

    try:
        return functools.reduce(getattr, attr.split("."), obj)
    except AttributeError:
        if default != raise_attribute_error:
            return default
        raise


def nested_dict_get(dictionary, path):
    import functools

    return functools.reduce(lambda d, key: d.get(key, None) if isinstance(d, dict) else None, path.split("."), dictionary)


def get_count_and_percentage(input_list, all_items_list):
    count = len(input_list)
    all_items_count = len(all_items_list) or 1
    percentage = (count / all_items_count) * 100
    return {"count": count, "percentage": percentage}


def encode_ids(results: List[dict], model_name: str, key: str) -> List[dict]:
    if results:
        for result in results:
            result_id = result[key]
            result[key] = encode_id_base64(result_id, model_name)
    return results


def to_dict(instance, fields=None, dict_fields=None):
    if fields is None:
        fields = [f.name for f in instance._meta.fields]

    data = model_to_dict(instance, fields)

    for field in fields:
        main_field = getattr(instance, field, "__NOT_EXIST__")
        if main_field != "__NOT_EXIST__":
            data[field] = main_field if issubclass(type(main_field), Model) else main_field

    if dict_fields and isinstance(dict_fields, dict):
        for main_field_key, nested_fields in dict_fields.items():
            main_field = getattr(instance, main_field_key, "__NOT_EXIST__")
            if main_field != "__NOT_EXIST__":
                if hasattr(main_field, "db"):
                    objs = main_field.all()
                    data[main_field_key] = []
                    multi = True
                else:
                    objs = [main_field]
                    multi = False

                for obj in objs:
                    instance_data_dict = {}
                    for nested_field in nested_fields:
                        attrs_to_get = nested_field.split(".")
                        value = None
                        for attr in attrs_to_get:
                            if value:
                                value = getattr(value, attr, "__EMPTY_VALUE__")
                            else:
                                value = getattr(obj, attr, "__EMPTY_VALUE__")
                        if value != "__EMPTY_VALUE__":
                            instance_data_dict[attrs_to_get[-1]] = value
                    if instance_data_dict and multi is True:
                        data[main_field_key].append(instance_data_dict)
                    elif multi is False:
                        data[main_field_key] = instance_data_dict

    return data


def build_arg_dict(model_object, mapping_dict):
    args = {}
    for key in mapping_dict:
        args[key] = nested_getattr(model_object, mapping_dict[key], None)
    return args


def build_arg_dict_from_dict(data_dict, mapping_dict):
    args = {}
    for key, value in mapping_dict.items():
        args[key] = data_dict.get(value)
    return args


def is_valid_uuid(uuid_str):
    from uuid import UUID

    try:
        UUID(uuid_str, version=4)
        return True
    except ValueError:
        return False
