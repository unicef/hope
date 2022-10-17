import functools
import io
import itertools
import logging
import string
import pytz
from collections import OrderedDict
from collections.abc import MutableMapping
from datetime import date, datetime

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import QuerySet, Q
from django.utils import timezone

from django_filters import OrderingFilter
from graphql import GraphQLError
from PIL import Image

logger = logging.getLogger(__name__)


class CaseInsensitiveTuple(tuple):
    def __contains__(self, key, *args, **kwargs):
        return key.casefold() in (element.casefold() for element in self)


def decode_id_string(id_string):
    if not id_string:
        return

    from base64 import b64decode

    return b64decode(id_string).decode().split(":")[1]


def encode_id_base64(id_string, model_name):
    if not id_string:
        return

    from base64 import b64encode

    return b64encode(f"{model_name}Node:{str(id_string)}".encode()).decode()


def unique_slugify(instance, value, slug_field_name="slug", queryset=None, slug_separator="-"):
    """
    Calculates and stores a unique slug of ``value`` for an instance.

    ``slug_field_name`` should be a string matching the name of the field to
    store the slug in (and the field to check against for uniqueness).

    ``queryset`` usually doesn't need to be explicitly provided - it'll default
    to using the ``.all()`` queryset from the model's default manager.
    """
    from django.template.defaultfilters import slugify

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
        end = f"{slug_separator}{next}"
        if slug_len and len(slug) + len(end) > slug_len:
            slug = slug[: slug_len - len(end)]
            slug = _slug_strip(slug, slug_separator)
        slug = f"{slug}{end}"
        next += 1

    setattr(instance, slug_field.attname, slug)


def _slug_strip(value, separator="-"):
    import re

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
        re_sep = "(?:-|{})".format(re.escape(separator))
    # Remove multiple instances and if an alternate separator is provided,
    # replace the default '-' separator.
    if separator != re_sep:
        value = re.sub("{}+".format(re_sep, separator, value))  # noqa: F523 # TODO: bug?
    # Remove separator from the beginning and end of the slug.
    if separator:
        if separator != "-":
            re_sep = re.escape(separator)

        value = re.sub(r"^{}+|{}+$".format(re_sep, re_sep), "", value)
    return value


def serialize_flex_attributes():
    from django.db.models import F

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
    from hct_mis_api.apps.core.models import FlexibleAttribute

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
            "xlsx_field": attr.name,
            "lookup": attr.name,
            "required": attr.required,
            "label": attr.label,
            "hint": attr.hint,
            "choices": list(attr.choices.values("label", value=F("name"))),
            "associated_with": associated_with,
        }

    return result_dict


def get_combined_attributes():
    from hct_mis_api.apps.core.core_fields_attributes import FieldFactory, Scope

    flex_attrs = serialize_flex_attributes()
    return {
        **FieldFactory.from_scopes([Scope.GLOBAL, Scope.XLSX, Scope.HOUSEHOLD_ID, Scope.COLLECTOR])
        .apply_business_area(None)
        .to_dict_by("xlsx_field"),
        **flex_attrs["individuals"],
        **flex_attrs["households"],
    }


def get_attr_value(name, obj, default=None):
    if isinstance(obj, (MutableMapping, dict)):
        return obj.get(name, default)
    return getattr(obj, name, default)


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
    except AttributeError as e:
        if default != raise_attribute_error:
            return default
        logger.exception(e)
        raise


def nested_dict_get(dictionary, path):
    import functools

    return functools.reduce(
        lambda d, key: d.get(key, None) if isinstance(d, dict) else None,
        path.split("."),
        dictionary,
    )


def get_count_and_percentage(input_list, all_items_list):
    count = len(input_list)
    all_items_count = len(all_items_list) or 1
    percentage = (count / all_items_count) * 100
    return {"count": count, "percentage": percentage}


def encode_ids(results: list[dict], model_name: str, key: str) -> list[dict]:
    if results:
        for result in results:
            result_id = result[key]
            result[key] = encode_id_base64(result_id, model_name)
    return results


def to_dict(instance, fields=None, dict_fields=None):
    from django.db.models import Model
    from django.forms import model_to_dict

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
    return {key: nested_getattr(model_object, mapping_dict[key], None) for key in mapping_dict}


def build_arg_dict_from_dict(data_dict, mapping_dict):
    return {key: data_dict.get(value) for key, value in mapping_dict.items()}


class CustomOrderingFilter(OrderingFilter):
    def filter(self, qs, value):
        from django.db.models.functions import Lower

        from django_filters.constants import EMPTY_VALUES

        if value in EMPTY_VALUES:
            return qs

        ordering = [self.get_ordering_value(param) for param in value]
        new_ordering = []
        for field in ordering:
            field_name = field
            desc = False
            if field.startswith("-"):
                field_name = field[1:]
                desc = True
            if isinstance(self.lower_dict.get(field_name), Lower):
                lower_field = self.lower_dict.get(field_name)
                if desc:
                    lower_field = lower_field.desc()
                new_ordering.append(lower_field)
            else:
                new_ordering.append(field)
        return qs.order_by(*new_ordering)

    def normalize_fields(self, fields):
        """
        Normalize the fields into an ordered map of {field name: param name}
        """
        from django.db.models.functions import Lower
        from django.utils.itercompat import is_iterable

        # fields is a mapping, copy into new OrderedDict
        if isinstance(fields, dict):
            return OrderedDict(fields)

        # convert iterable of values => iterable of pairs (field name, param name)
        assert is_iterable(fields), "'fields' must be an iterable (e.g., a list, tuple, or mapping)."

        # fields is an iterable of field names
        assert all(
            isinstance(field, (str, Lower))
            or is_iterable(field)
            and len(field) == 2  # may need to be wrapped in parens
            for field in fields
        ), "'fields' must contain strings or (field name, param name) pairs."

        new_fields = []
        self.lower_dict = {}

        for field in fields:
            field_name = field
            if isinstance(field, Lower):
                field_name = field.source_expressions[0].name
            new_fields.append(field_name)
            self.lower_dict[field_name] = field

        return OrderedDict([(f, f) if isinstance(f, (str, Lower)) else f for f in new_fields])


def is_valid_uuid(uuid_str):
    from uuid import UUID

    try:
        UUID(uuid_str, version=4)
        return True
    except ValueError:
        return False


def choices_to_dict(choices):
    return {value: name for value, name in choices}


def decode_and_get_object(encoded_id, model, required):
    from django.shortcuts import get_object_or_404

    if required is True or encoded_id is not None:
        decoded_id = decode_id_string(encoded_id)
        return get_object_or_404(model, id=decoded_id)


def dict_to_camel_case(dictionary):
    from graphene.utils.str_converters import to_camel_case

    if isinstance(dictionary, dict):
        return {to_camel_case(key): value for key, value in dictionary.items()}
    return {}


def to_snake_case(camel_case_string):
    if "_" in camel_case_string:
        return camel_case_string
    import re

    snake_case = re.sub("(?<!^)([A-Z0-9])", r"_\1", camel_case_string)
    return snake_case[0] + snake_case[1:].lower()


def check_concurrency_version_in_mutation(version, target):
    if version is None:
        return
    from graphql import GraphQLError

    if version != target.version:
        logger.error(f"Someone has modified this {target} record, versions {version} != {target.version}")
        raise GraphQLError("Someone has modified this record")


def update_labels_mapping(csv_file):
    """
    WARNING! THIS FUNCTION DIRECTLY MODIFY core_fields_attributes.py

    IF YOU DON'T UNDERSTAND WHAT THIS FUNCTION DO, SIMPLY DO NOT TOUCH OR USE IT

    csv_file: path to csv file, 2 columns needed (field name, english label)
    """
    import csv
    import json
    import re

    from django.conf import settings

    from hct_mis_api.apps.core.core_fields_attributes import FieldFactory, Scope

    with open(csv_file, newline="") as csv_file:
        reader = csv.reader(csv_file)
        next(reader, None)
        fields_mapping = dict(reader)

    labels_mapping = {
        core_field_data["xlsx_field"]: {
            "old": core_field_data["label"],
            "new": {"English(EN)": fields_mapping.get(core_field_data["xlsx_field"], "")},
        }
        for core_field_data in FieldFactory.from_scope(Scope.GLOBAL)
        if core_field_data["label"].get("English(EN)", "") != fields_mapping.get(core_field_data["xlsx_field"], "")
    }

    file_path = f"{settings.PROJECT_ROOT}/apps/core/core_fields_attributes.py"
    with open(file_path) as f:
        content = f.read()
        new_content = content
        for core_field, labels in labels_mapping.items():
            old_label = (
                json.dumps(labels["old"])
                .replace("\\", r"\\")
                .replace('"', r"\"")
                .replace("(", r"\(")
                .replace(")", r"\)")
                .replace("[", r"\[")
                .replace("]", r"\]")
                .replace("?", r"\?")
                .replace("*", r"\*")
                .replace("$", r"\$")
                .replace("^", r"\^")
                .replace(".", r"\.")
            )
            new_label = json.dumps(labels["new"])
            new_content = re.sub(
                rf"(\"label\": )({old_label}),([\S\s]*?)(\"xlsx_field\": \"{core_field}\",)",
                rf"\1{new_label},\3\4",
                new_content,
                flags=re.M,
            )

    with open(file_path, "r+") as f:
        f.truncate(0)

    with open(file_path, "w") as f:
        print(new_content, file=f, end="")


def xlrd_rows_iterator(sheet):
    import xlrd

    for row_number in range(1, sheet.nrows):
        row = sheet.row(row_number)

        if all([cell.ctype == xlrd.XL_CELL_EMPTY for cell in row]):
            continue

        yield row


def chart_map_choices(choices):
    return dict(choices)


def chart_get_filtered_qs(
    qs,
    year,
    business_area_slug_filter: dict = None,
    additional_filters: dict = None,
    year_filter_path: str = None,
    payment_verification_gfk: bool = False,
) -> QuerySet:
    # if payment_verification_gfk True will use Q() object for filtering by PaymentPlan and CashPlan
    q_obj = Q()
    if additional_filters is None:
        additional_filters = {}
    if isinstance(additional_filters, Q):
        q_obj, additional_filters = additional_filters, {}
    if year_filter_path is None:
        year_filter = {"created_at__year": year}
    else:
        year_filter = {f"{year_filter_path}__year": year}
        if payment_verification_gfk:
            year_filter = {}
            for k in year_filter_path.split(","):
                q_obj |= Q(**{f"{k}__year": year})

    if business_area_slug_filter is None or "global" in business_area_slug_filter.values():
        business_area_slug_filter = {}

    if payment_verification_gfk and len(business_area_slug_filter) > 1:
        for key, value in business_area_slug_filter.items():
            q_obj |= Q(**{key: value})

    return qs.filter(q_obj, **year_filter, **business_area_slug_filter, **additional_filters)


def parse_list_values_to_int(list_to_parse):
    return list(map(lambda x: int(x or 0), list_to_parse))


def sum_lists_with_values(qs_values, list_len):
    data = [0] * list_len
    for values in qs_values:
        parsed_values = parse_list_values_to_int(values)
        for i, value in enumerate(parsed_values):
            data[i] += value

    return data


def chart_permission_decorator(chart_resolve=None, permissions=None):
    if chart_resolve is None:
        return functools.partial(chart_permission_decorator, permissions=permissions)

    @functools.wraps(chart_resolve)
    def resolve_f(*args, **kwargs):
        from hct_mis_api.apps.core.models import BusinessArea

        _, resolve_info = args
        if resolve_info.context.user.is_authenticated:
            business_area_slug = kwargs.get("business_area_slug", "global")
            business_area = BusinessArea.objects.filter(slug=business_area_slug).first()
            if any(resolve_info.context.user.has_permission(per.name, business_area) for per in permissions):
                return chart_resolve(*args, **kwargs)
            logger.error("Permission Denied")
            raise GraphQLError("Permission Denied")

    return resolve_f


def chart_filters_decoder(filters):
    return {filter_name: decode_id_string(value) for filter_name, value in filters.items()}


def chart_create_filter_query(filters, program_id_path="id", administrative_area_path="admin_areas", payment_verification_gfk=False):
    filter_query = {} if not payment_verification_gfk else Q()
    if filters.get("program") is not None:
        if not payment_verification_gfk:
            filter_query.update({program_id_path: filters.get("program")})
        else:
            for path in program_id_path.split(","):
                filter_query |= Q(**{path: filters.get("program")})
    if filters.get("administrative_area") is not None:
        if not payment_verification_gfk:
            filter_query.update(
                {
                    f"{administrative_area_path}__id": filters.get("administrative_area"),
                    f"{administrative_area_path}__area_type__area_level": 2,
                }
            )
        else:
            for path in administrative_area_path.split(","):
                filter_query |= Q(
                    Q(**{f"{path}__id": filters.get("administrative_area")}) &
                    Q(**{f"{path}__area_type__area_level": 2})
                )

    return filter_query


class CaIdIterator:
    def __init__(self, name):
        self.name = name
        self.last_id = 0

    def __iter__(self):
        return self

    def __next__(self):
        self.last_id += 1
        return f"123-21-{self.name.upper()}-{self.last_id:05d}"


def resolve_flex_fields_choices_to_string(parent):
    from hct_mis_api.apps.core.models import FlexibleAttribute

    flex_fields = dict(FlexibleAttribute.objects.values_list("name", "type"))
    flex_fields_with_str_choices = {**parent.flex_fields}
    for flex_field_name, value in flex_fields_with_str_choices.items():
        flex_field = flex_fields.get(flex_field_name)
        if flex_field is None:
            continue

        if flex_field in (FlexibleAttribute.SELECT_ONE, FlexibleAttribute.SELECT_MANY):
            if isinstance(value, list):
                new_value = [str(current_choice_value) for current_choice_value in value]
            else:
                new_value = str(value)
            flex_fields_with_str_choices[flex_field_name] = new_value

    return flex_fields_with_str_choices


def get_model_choices_fields(model, excluded=None):
    if excluded is None:
        excluded = []

    return [
        field.name
        for field in model._meta.get_fields()
        if getattr(field, "choices", None) and field.name not in excluded
    ]


class SheetImageLoader:
    """Loads all images in a sheet"""

    _images = {}

    def __init__(self, sheet):
        # Holds an array of A-ZZ
        col_holder = list(
            itertools.chain(
                string.ascii_uppercase,
                ("".join(pair) for pair in itertools.product(string.ascii_uppercase, repeat=2)),
            )
        )
        """Loads all sheet images"""
        sheet_images = sheet._images
        for image in sheet_images:
            row = image.anchor._from.row + 1
            col = col_holder[image.anchor._from.col]
            self._images[f"{col}{row}"] = image._data

    def image_in(self, cell):
        """Checks if there's an image in specified cell"""
        return cell in self._images

    def get(self, cell):
        """Retrieves image data from a cell"""
        if cell not in self._images:
            raise ValueError(f"Cell {cell} doesn't contain an image")
        else:
            image = io.BytesIO(self._images[cell]())
            return Image.open(image)


def fix_flex_type_fields(items, flex_fields):
    for item in items:
        for key, value in item.flex_fields.items():
            if key in flex_fields:
                if value is not None and value != "":
                    item.flex_fields[key] = float(value)
                else:
                    item.flex_fields[key] = None

    return items


def map_unicef_ids_to_households_unicef_ids(excluded_ids_string):
    excluded_ids_array = excluded_ids_string.split(",")
    excluded_ids_array = [excluded_id.strip() for excluded_id in excluded_ids_array]
    excluded_household_ids_array = [excluded_id for excluded_id in excluded_ids_array if excluded_id.startswith("HH")]
    excluded_individuals_ids_array = [
        excluded_id for excluded_id in excluded_ids_array if excluded_id.startswith("IND")
    ]
    from hct_mis_api.apps.household.models import Household

    excluded_household_ids_from_individuals_array = Household.objects.filter(
        individuals__unicef_id__in=excluded_individuals_ids_array
    ).values_list("unicef_id", flat=True)
    excluded_household_ids_array.extend(excluded_household_ids_from_individuals_array)
    return excluded_household_ids_array


@functools.lru_cache(maxsize=None)
def cached_business_areas_slug_id_dict():
    from hct_mis_api.apps.core.models import BusinessArea

    return {str(ba.slug): ba.id for ba in BusinessArea.objects.only("slug")}


def timezone_datetime(value):
    if not value:
        return value
    datetime_value = value
    if isinstance(value, date):
        datetime_value = datetime.combine(datetime_value, datetime.min.time())
    if isinstance(value, str):
        datetime_value = timezone.make_aware(datetime.fromisoformat(value))
    if datetime_value.tzinfo is None or datetime_value.tzinfo.utcoffset(datetime_value) is None:
        return datetime_value.replace(tzinfo=pytz.utc)
    return datetime_value


def get_paginator(qs, page_size, page):
    p = Paginator(qs, page_size)
    try:
        page_obj = p.page(page)
    except PageNotAnInteger:
        page_obj = p.page(1)
    except EmptyPage:
        page_obj = p.page(p.num_pages)
    return p, page_obj
