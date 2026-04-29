from datetime import date
from decimal import Decimal
import json
from unittest.mock import MagicMock
from uuid import uuid4

from django.db.models import JSONField, Value
from django.db.models.functions import Cast, Lower
import pytest
from rest_framework.exceptions import ValidationError

from extras.test_utils.factories import (
    BusinessAreaFactory,
    HouseholdFactory,
    IndividualFactory,
    ProgramFactory,
)
from extras.test_utils.factories.core import (
    FlexibleAttributeChoiceFactory,
    FlexibleAttributeFactory,
    FlexibleAttributeForPDUFactory,
)
from hope.apps.core.utils import (
    AutoCompleteFilterTemp,
    CaseInsensitiveTuple,
    CustomOrderingFilter,
    FlexFieldsEncoder,
    JSONBSet,
    SheetImageLoader,
    _apply_dict_fields,
    build_arg_dict_from_dict,
    build_arg_dict_from_dict_if_exists,
    build_flex_arg_dict_from_list_if_exists,
    chart_create_filter_query,
    chart_get_filtered_qs,
    check_concurrency_version_in_mutation,
    chunks,
    clear_cache_for_key,
    get_attr_value,
    get_combined_attributes,
    get_count_and_percentage,
    get_fields_attr_generators,
    map_unicef_ids_to_households_unicef_ids,
    nested_dict_get,
    nested_getattr,
    rename_dict_keys,
    resolve_assets_list,
    resolve_flex_fields_choices_to_string,
    rows_iterator,
    safe_getattr,
    send_email_notification,
    send_email_notification_on_commit,
    serialize_flex_attributes,
    sort_by_attr,
    stable_ids_hash,
    to_choice_object,
    to_dict,
    to_snake_case,
    unique_slugify,
)
from hope.apps.payment.utils import get_payment_delivered_quantity_status_and_value
from hope.models import BusinessArea, FlexibleAttribute, Household, Individual, Payment

# ============================================================================
# Pure function tests (no DB needed)
# ============================================================================


def test_nested_dict_get_returns_none_for_non_dict_intermediate():
    assert nested_dict_get({"path": "string_not_dict"}, "path.to.value") is None


def test_nested_dict_get_returns_value_for_valid_path():
    assert nested_dict_get({"a": {"b": {"c": 42}}}, "a.b.c") == 42


def test_nested_dict_get_returns_none_for_missing_key():
    assert nested_dict_get({"a": {"b": 1}}, "a.x") is None


@pytest.mark.parametrize(
    ("count", "expected"),
    [
        (1, {"count": 1, "percentage": 100.0}),
        (0, {"count": 0, "percentage": 0.0}),
    ],
)
def test_get_count_and_percentage_without_total_uses_count_as_denominator(count, expected):
    assert get_count_and_percentage(count) == expected


@pytest.mark.parametrize(
    ("count", "total", "expected"),
    [
        (5, 1, {"count": 5, "percentage": 500.0}),
        (20, 20, {"count": 20, "percentage": 100.0}),
        (5, 25, {"count": 5, "percentage": 20.0}),
    ],
)
def test_get_count_and_percentage_with_total_calculates_correctly(count, total, expected):
    assert get_count_and_percentage(count, total) == expected


@pytest.mark.parametrize(
    ("delivered_quantity", "entitlement_quantity", "expected_status", "expected_value"),
    [
        (-1, Decimal("10.00"), Payment.STATUS_ERROR, None),
        (0, Decimal("10.00"), Payment.STATUS_NOT_DISTRIBUTED, 0),
        (5.00, Decimal("10.00"), Payment.STATUS_DISTRIBUTION_PARTIAL, Decimal("5.00")),
        (10.00, Decimal("10.00"), Payment.STATUS_DISTRIBUTION_SUCCESS, Decimal("10.00")),
    ],
)
def test_get_payment_delivered_quantity_status_and_value_returns_correct_status(
    delivered_quantity, entitlement_quantity, expected_status, expected_value
):
    result = get_payment_delivered_quantity_status_and_value(delivered_quantity, entitlement_quantity)
    assert result == (expected_status, expected_value)


@pytest.mark.parametrize(
    "invalid_quantity",
    [None, ""],
)
def test_get_payment_delivered_quantity_status_and_value_raises_for_invalid_input(invalid_quantity):
    with pytest.raises(Exception, match="Invalid delivered quantity"):
        get_payment_delivered_quantity_status_and_value(invalid_quantity, Decimal("10.00"))


def test_get_payment_delivered_quantity_status_and_value_raises_when_exceeds_entitlement():
    with pytest.raises(Exception, match="Invalid delivered quantity"):
        get_payment_delivered_quantity_status_and_value(20.00, Decimal("10.00"))


def test_stable_ids_hash_is_order_independent_and_normalizes_values():
    first_uuid = uuid4()
    second_uuid = uuid4()

    assert stable_ids_hash([first_uuid, "abc", second_uuid]) == stable_ids_hash(
        [str(second_uuid), str(first_uuid), "abc"]
    )


# ============================================================================
# CustomOrderingFilter tests (no DB needed)
# ============================================================================


def test_custom_ordering_filter_applies_lower_and_plain_fields():
    from django.db.models.functions import Lower

    ordering_filter = CustomOrderingFilter(field_name="ordering")
    ordering_filter.lower_dict = {"name": Lower("name"), "id": "id"}
    ordering_filter.param_map = {"name": "name", "id": "id"}

    mock_qs = MagicMock()
    mock_qs.order_by.return_value = mock_qs

    # Test ascending Lower field (isinstance True branch)
    ordering_filter.filter(mock_qs, ["name"])
    call_args = mock_qs.order_by.call_args[0]
    assert isinstance(call_args[0], Lower)

    # Test descending Lower field
    ordering_filter.filter(mock_qs, ["-name"])
    call_args = mock_qs.order_by.call_args[0]
    assert hasattr(call_args[0], "descending")

    # Test plain field — isinstance False branch (not Lower)
    ordering_filter.filter(mock_qs, ["id"])
    call_args = mock_qs.order_by.call_args[0]
    assert call_args[0] == "id"


# ============================================================================
# _apply_dict_fields tests (no DB needed)
# ============================================================================


def test_apply_dict_fields_skips_nonexistent_attribute():
    """When instance lacks the attribute, data should remain unchanged."""
    data = {}
    instance = MagicMock(spec=[])  # no attributes at all
    _apply_dict_fields(data, instance, {"missing_field": ["name"]})
    assert data == {}


def test_apply_dict_fields_single_object_produces_dict():
    """When the field is a single object (no .db), data[key] should be a dict."""
    related_obj = MagicMock()
    related_obj.full_name = "John Doe"

    instance = MagicMock()
    instance.related = related_obj
    # Ensure the related object does NOT have a .db attribute (single object, not a manager)
    del related_obj.db

    data = {}
    _apply_dict_fields(data, instance, {"related": ["full_name"]})
    assert data["related"] == {"full_name": "John Doe"}


def test_apply_dict_fields_queryset_produces_list():
    """When the field has .db (queryset manager), data[key] should be a list of dicts."""
    child1 = MagicMock()
    child1.name = "Alice"
    child2 = MagicMock()
    child2.name = "Bob"

    manager = MagicMock()
    manager.db = "default"  # has .db attribute, simulating a manager
    manager.all.return_value = [child1, child2]

    instance = MagicMock()
    instance.children = manager

    data = {}
    _apply_dict_fields(data, instance, {"children": ["name"]})
    assert data["children"] == [{"name": "Alice"}, {"name": "Bob"}]


def test_apply_dict_fields_queryset_empty_nested_not_appended():
    """When nested fields don't resolve, empty dicts should not be appended to the list."""
    obj_with_no_matching_attr = MagicMock(spec=[])  # no attributes

    manager = MagicMock()
    manager.db = "default"
    manager.all.return_value = [obj_with_no_matching_attr]

    instance = MagicMock()
    instance.items = manager

    data = {}
    _apply_dict_fields(data, instance, {"items": ["nonexistent_field"]})
    assert data["items"] == []


def test_apply_dict_fields_single_object_empty_nested_still_sets_key():
    """For single objects, even if nested fields don't resolve, data[key] should be set to empty dict."""
    related_obj = MagicMock(spec=[])  # no attributes
    del related_obj.db  # ensure it's treated as single object

    instance = MagicMock()
    instance.related = related_obj

    data = {}
    _apply_dict_fields(data, instance, {"related": ["nonexistent"]})
    assert data["related"] == {}


# ============================================================================
# to_dict tests (need DB)
# ============================================================================


@pytest.fixture
def business_area():
    return BusinessAreaFactory(slug="afghanistan", name="Afghanistan")


@pytest.fixture
def program(business_area):
    return ProgramFactory(business_area=business_area)


@pytest.fixture
def household_with_individuals(business_area, program):
    household = HouseholdFactory(business_area=business_area, program=program)
    rdi = household.registration_data_import
    IndividualFactory(business_area=business_area, program=program, household=household, registration_data_import=rdi)
    IndividualFactory(business_area=business_area, program=program, household=household, registration_data_import=rdi)
    return household


@pytest.fixture
def individual_with_household(business_area, program):
    household = HouseholdFactory(business_area=business_area, program=program)
    rdi = household.registration_data_import
    return IndividualFactory(
        business_area=business_area, program=program, household=household, registration_data_import=rdi
    )


@pytest.mark.django_db
def test_to_dict_includes_nested_fields_for_related_objects(household_with_individuals):
    result = to_dict(
        household_with_individuals,
        fields=["id"],
        dict_fields={"individuals": ["full_name", "birth_date"]},
    )

    assert "individuals" in result
    assert len(result["individuals"]) >= 2
    assert all("full_name" in ind for ind in result["individuals"])


@pytest.mark.django_db
def test_to_dict_resolves_dotted_field_paths(individual_with_household):
    result = to_dict(
        individual_with_household,
        fields=["id"],
        dict_fields={"household": ["program.name"]},
    )

    assert "household" in result
    assert "name" in result["household"]


# ============================================================================
# Tier 1 — pure-Python tests (no DB)
# ============================================================================


@pytest.mark.parametrize(
    ("needle", "expected"),
    [("foo", True), ("FOO", True), ("Foo", True), ("bar", False)],
)
def test_case_insensitive_tuple_contains(needle, expected):
    assert (needle in CaseInsensitiveTuple(("Foo", "Baz"))) is expected


@pytest.mark.parametrize(
    ("obj", "name", "default", "expected"),
    [
        ({"a": 1}, "a", None, 1),
        ({"a": 1}, "missing", "fallback", "fallback"),
    ],
)
def test_get_attr_value_for_dict(obj, name, default, expected):
    assert get_attr_value(name, obj, default) == expected


def test_get_attr_value_for_object_returns_via_getattr():
    obj = MagicMock(some_attr="value")
    assert get_attr_value("some_attr", obj) == "value"


def test_get_attr_value_for_object_returns_default_when_missing():
    obj = MagicMock(spec=[])
    assert get_attr_value("missing", obj, "fallback") == "fallback"


def test_to_choice_object_sorts_by_name():
    choices = [("v_b", "Banana"), ("v_a", "Apple"), ("v_c", "Cherry")]

    result = to_choice_object(choices)

    assert result == [
        {"name": "Apple", "value": "v_a"},
        {"name": "Banana", "value": "v_b"},
        {"name": "Cherry", "value": "v_c"},
    ]


def test_rename_dict_keys_renames_dict_recursively():
    obj = {"a_b": 1, "nested": {"c_d": [{"e_f": 2}]}}
    result = rename_dict_keys(obj, lambda k: k.upper())
    assert result == {"A_B": 1, "NESTED": {"C_D": [{"E_F": 2}]}}


def test_rename_dict_keys_returns_scalar_unchanged():
    assert rename_dict_keys(42, str.upper) == 42


def test_rename_dict_keys_renames_inside_list():
    assert rename_dict_keys([{"a": 1}, {"b": 2}], str.upper) == [{"A": 1}, {"B": 2}]


def test_nested_getattr_returns_value_for_dotted_path():
    obj = MagicMock()
    obj.a.b.c = "deep"
    assert nested_getattr(obj, "a.b.c") == "deep"


def test_nested_getattr_returns_default_when_path_missing():
    obj = MagicMock(spec=[])
    assert nested_getattr(obj, "missing.path", default="fallback") == "fallback"


def test_nested_getattr_raises_when_no_default():
    obj = MagicMock(spec=[])
    with pytest.raises(AttributeError):
        nested_getattr(obj, "missing")


def test_build_arg_dict_from_dict_maps_keys():
    assert build_arg_dict_from_dict({"src_a": 1, "src_b": 2}, {"dst_a": "src_a", "dst_b": "src_b"}) == {
        "dst_a": 1,
        "dst_b": 2,
    }


def test_build_arg_dict_from_dict_returns_none_for_missing_source_key():
    assert build_arg_dict_from_dict({}, {"dst": "missing"}) == {"dst": None}


def test_build_arg_dict_from_dict_if_exists_skips_missing():
    assert build_arg_dict_from_dict_if_exists({"src_a": 1}, {"dst_a": "src_a", "dst_b": "src_b"}) == {"dst_a": 1}


def test_build_flex_arg_dict_from_list_if_exists_keeps_only_present_keys():
    assert build_flex_arg_dict_from_list_if_exists({"a": 1, "c": 3}, ["a", "b", "c"]) == {"a": 1, "c": 3}


@pytest.mark.parametrize(
    ("camel", "expected"),
    [
        ("CamelCase", "Camel_case"),
        ("Camel", "Camel"),
        ("CamelCaseWord", "Camel_case_word"),
        ("Camel2Case", "Camel_2_case"),
        ("already_snake_case", "already_snake_case"),
    ],
)
def test_to_snake_case(camel, expected):
    assert to_snake_case(camel) == expected


def test_check_concurrency_version_returns_for_none():
    target = MagicMock(version=5)
    check_concurrency_version_in_mutation(None, target)


def test_check_concurrency_version_passes_when_match():
    target = MagicMock(version=5)
    check_concurrency_version_in_mutation(5, target)


def test_check_concurrency_version_raises_when_mismatch():
    target = MagicMock(version=5)

    with pytest.raises(ValidationError):
        check_concurrency_version_in_mutation(3, target)


@pytest.mark.parametrize(
    ("filters", "expected"),
    [
        ({}, {}),
        ({"program": "p1"}, {"id": "p1"}),
        ({"administrative_area": "a1"}, {"admin_areas__id": "a1"}),
        ({"program": "p1", "administrative_area": "a1"}, {"id": "p1", "admin_areas__id": "a1"}),
    ],
)
def test_chart_create_filter_query(filters, expected):
    assert chart_create_filter_query(filters) == expected


def test_chart_get_filtered_qs_default_year_path_uses_created_at():
    qs = MagicMock()
    qs.filter.return_value = qs

    chart_get_filtered_qs(qs, year=2024)

    args, kwargs = qs.filter.call_args
    year_q = args[0]
    assert "created_at__year" in str(year_q)


def test_chart_get_filtered_qs_custom_year_path_combines_with_or():
    qs = MagicMock()
    qs.filter.return_value = qs

    chart_get_filtered_qs(qs, year=2024, year_filter_path="a,b")

    args, kwargs = qs.filter.call_args
    year_q = args[0]
    assert "a__year" in str(year_q)
    assert "b__year" in str(year_q)


def test_chart_get_filtered_qs_drops_global_business_area_filter():
    qs = MagicMock()
    qs.filter.return_value = qs

    chart_get_filtered_qs(qs, year=2024, business_area_slug_filter={"business_area__slug": "global"})

    _, kwargs = qs.filter.call_args
    assert "business_area__slug" not in kwargs


def test_chart_get_filtered_qs_passes_additional_filters():
    qs = MagicMock()
    qs.filter.return_value = qs

    chart_get_filtered_qs(qs, year=2024, additional_filters={"name__icontains": "x"})

    _, kwargs = qs.filter.call_args
    assert kwargs == {"name__icontains": "x"}


def test_chart_get_filtered_qs_keeps_non_global_business_area_filter():
    qs = MagicMock()
    qs.filter.return_value = qs

    chart_get_filtered_qs(qs, year=2024, business_area_slug_filter={"business_area__slug": "afghanistan"})

    _, kwargs = qs.filter.call_args
    assert kwargs == {"business_area__slug": "afghanistan"}


def test_chunks_yields_full_buckets():
    result = list(chunks([1, 2, 3, 4, 5, 6], 2))
    assert result == [[1, 2], [3, 4], [5, 6]]


def test_chunks_yields_partial_last_bucket():
    result = list(chunks([1, 2, 3, 4, 5], 2))
    assert result == [[1, 2], [3, 4], [5]]


def test_chunks_handles_empty_iterable():
    assert list(chunks([], 5)) == []


def test_flex_fields_encoder_serializes_date_as_isoformat():
    payload = {"day": date(2024, 6, 1)}
    assert json.loads(json.dumps(payload, cls=FlexFieldsEncoder)) == {"day": "2024-06-01"}


def test_flex_fields_encoder_serializes_decimal_as_string():
    payload = {"amount": Decimal("12.50")}
    assert json.loads(json.dumps(payload, cls=FlexFieldsEncoder)) == {"amount": "12.50"}


def test_flex_fields_encoder_falls_back_to_super_for_unknown_types():
    with pytest.raises(TypeError):
        json.dumps({"x": object()}, cls=FlexFieldsEncoder)


def test_jsonb_set_wraps_new_value_in_cast():
    expr = JSONBSet("col", Value("{path}"), {"foo": "bar"}, create_missing=False)

    assert expr.function == "jsonb_set"
    assert isinstance(expr.output_field, JSONField)
    cast_expr = expr.source_expressions[2]
    assert isinstance(cast_expr, Cast)
    assert expr.source_expressions[3].value is False


def test_safe_getattr_for_dict_uses_get():
    assert safe_getattr({"a": 1}, "a") == 1


def test_safe_getattr_returns_none_for_missing_dict_key():
    assert safe_getattr({}, "missing") is None


def test_safe_getattr_for_object_uses_getattr():
    obj = MagicMock(spec=["a"], a=42)
    assert safe_getattr(obj, "a") == 42


def test_safe_getattr_returns_none_for_missing_object_attr():
    assert safe_getattr(MagicMock(spec=[]), "missing") is None


def test_sort_by_attr_for_objects_sorts_by_nested_attr():
    item_b = MagicMock(child=MagicMock(name_attr="banana"))
    item_a = MagicMock(child=MagicMock(name_attr="apple"))
    item_c = MagicMock(child=MagicMock(name_attr="cherry"))

    result = sort_by_attr([item_b, item_a, item_c], "child.name_attr")

    assert result == [item_a, item_b, item_c]


def test_sort_by_attr_for_dicts_sorts_by_key():
    items = [{"name": "banana"}, {"name": "apple"}, {"name": "cherry"}]

    result = sort_by_attr(items, "name")

    assert [item["name"] for item in result] == ["apple", "banana", "cherry"]


def test_sort_by_attr_treats_missing_path_as_empty_string():
    has_attr = MagicMock(child=MagicMock(name_attr="zzz"))
    missing = MagicMock(spec=[])

    result = sort_by_attr([has_attr, missing], "child.name_attr")

    assert result[0] is missing
    assert result[1] is has_attr


# ============================================================================
# Tier 3 — mock / I-O tests (no DB)
# ============================================================================


class _StubAnchorFrom:
    def __init__(self, row, col):
        self.row = row
        self.col = col


class _StubAnchor:
    def __init__(self, row, col):
        self._from = _StubAnchorFrom(row, col)


class _StubImage:
    def __init__(self, row, col, payload):
        self.anchor = _StubAnchor(row, col)
        self._data = lambda: payload


@pytest.fixture
def reset_sheet_image_loader():
    SheetImageLoader._images = {}
    yield
    SheetImageLoader._images = {}


def test_sheet_image_loader_indexes_images_by_cell(reset_sheet_image_loader):
    sheet = MagicMock()
    sheet._images = [_StubImage(row=4, col=2, payload=b"x")]

    SheetImageLoader(sheet)

    assert "C5" in SheetImageLoader._images


def test_sheet_image_loader_image_in_returns_true_for_known_cell(reset_sheet_image_loader):
    sheet = MagicMock()
    sheet._images = [_StubImage(row=0, col=0, payload=b"x")]
    loader = SheetImageLoader(sheet)

    assert loader.image_in("A1") is True


def test_sheet_image_loader_image_in_returns_false_for_unknown_cell(reset_sheet_image_loader):
    sheet = MagicMock()
    sheet._images = []
    loader = SheetImageLoader(sheet)

    assert loader.image_in("Z99") is False


def test_sheet_image_loader_get_returns_pil_image(reset_sheet_image_loader):
    from PIL import Image as PILImage

    buf = io_for_pil()
    sheet = MagicMock()
    sheet._images = [_StubImage(row=0, col=0, payload=buf)]
    loader = SheetImageLoader(sheet)

    img = loader.get("A1")

    assert isinstance(img, PILImage.Image)


def test_sheet_image_loader_get_raises_for_missing_cell(reset_sheet_image_loader):
    sheet = MagicMock()
    sheet._images = []
    loader = SheetImageLoader(sheet)

    with pytest.raises(ValueError, match="doesn't contain an image"):
        loader.get("Z99")


def io_for_pil() -> bytes:
    """Smallest valid PNG payload, returned as bytes for SheetImageLoader.get()."""
    import base64

    one_pixel_png_base64 = (
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
    )
    return base64.b64decode(one_pixel_png_base64)


def test_rows_iterator_skips_header_and_empty_rows():
    cell_value = MagicMock(value="content")
    cell_empty = MagicMock(value=None)

    sheet = MagicMock()
    sheet.max_row = 4
    sheet.__getitem__.side_effect = lambda i: {
        2: [cell_value, cell_value],
        3: [cell_empty, cell_empty],
        4: [cell_value, cell_empty],
    }[i]

    rows = list(rows_iterator(sheet))

    assert len(rows) == 2
    assert rows[0] == [cell_value, cell_value]
    assert rows[1] == [cell_value, cell_empty]


def test_send_email_notification_with_user_renders_html_and_text(mocker):
    mocker.patch("hope.apps.core.utils.render_to_string", side_effect=["<html>body</html>", "text body"])
    user = MagicMock()
    service = MagicMock(html_template="email.html", text_template="email.txt")
    service.get_email_context.return_value = {"title": "Hello"}

    send_email_notification(service, user=user)

    service.get_email_context.assert_called_once_with(user)
    user.email_user.assert_called_once_with(subject="Hello", html_body="<html>body</html>", text_body="text body")


def test_send_email_notification_without_user_falls_back_to_service_user(mocker):
    mocker.patch("hope.apps.core.utils.render_to_string", return_value="rendered")
    service = MagicMock(html_template="h", text_template="t")
    service.get_email_context.return_value = {"title": "Hi"}

    send_email_notification(service)

    service.get_email_context.assert_called_once_with()
    service.user.email_user.assert_called_once()


def test_send_email_notification_with_context_kwargs_passes_them(mocker):
    mocker.patch("hope.apps.core.utils.render_to_string", return_value="rendered")
    user = MagicMock()
    service = MagicMock(html_template="h", text_template="t")
    service.get_email_context.return_value = {"title": "Hi"}

    send_email_notification(service, user=user, context_kwargs={"foo": "bar"})

    service.get_email_context.assert_called_once_with(foo="bar")


def test_send_email_notification_on_commit_schedules_callback(mocker):
    on_commit = mocker.patch("hope.apps.core.utils.transaction.on_commit")

    send_email_notification_on_commit(MagicMock(), user=MagicMock())

    assert on_commit.call_count == 1
    assert callable(on_commit.call_args[0][0])


def test_autocomplete_filter_temp_choices_returns_label_when_lookup_val_present():
    target_obj = MagicMock(__str__=lambda self: "Resolved Label")
    target_qs = MagicMock()
    target_qs.first.return_value = target_obj
    target_qs.__bool__ = lambda self: True

    instance = MagicMock(spec=AutoCompleteFilterTemp)
    instance.lookup_kwarg = "lookup"
    instance.lookup_kwarg_isnull = "lookup__isnull"
    instance.lookup_val = "abc"
    instance.field = MagicMock()
    instance.field.target_field.name = "id"
    instance.target_model = MagicMock()
    instance.target_model.objects.filter.return_value = target_qs

    changelist = MagicMock()
    changelist.get_query_string.return_value = "?qs"

    result = AutoCompleteFilterTemp.choices(instance, changelist)

    assert result == ["Resolved Label"]
    instance.target_model.objects.filter.assert_called_once_with(id="abc")


def test_autocomplete_filter_temp_choices_returns_empty_when_no_lookup_val():
    instance = MagicMock(spec=AutoCompleteFilterTemp)
    instance.lookup_kwarg = "lookup"
    instance.lookup_kwarg_isnull = "lookup__isnull"
    instance.lookup_val = None

    changelist = MagicMock()
    changelist.get_query_string.return_value = "?qs"

    result = AutoCompleteFilterTemp.choices(instance, changelist)

    assert result == []


def test_normalize_fields_accepts_dict_input():
    flt = CustomOrderingFilter(fields={"name": "name", "id": "id"})
    assert flt.normalize_fields({"name": "name"}) == {"name": "name"}


def test_normalize_fields_accepts_iterable_of_strings():
    flt = CustomOrderingFilter(fields=["name", "id"])
    assert flt.lower_dict == {"name": "name", "id": "id"}


def test_normalize_fields_extracts_source_name_from_lower_wrapper():
    flt = CustomOrderingFilter(fields=[Lower("name"), "id"])
    assert isinstance(flt.lower_dict["name"], Lower)
    assert flt.lower_dict["id"] == "id"


def test_normalize_fields_raises_when_input_not_iterable():
    flt = CustomOrderingFilter(fields=["name"])
    with pytest.raises(ValueError, match="must be an iterable"):
        flt.normalize_fields(123)


def test_normalize_fields_raises_assertion_for_invalid_field_entry():
    flt = CustomOrderingFilter(fields=["name"])
    with pytest.raises(AssertionError, match="must contain strings"):
        flt.normalize_fields([42])


def test_custom_ordering_filter_returns_qs_unchanged_for_empty_value():
    flt = CustomOrderingFilter(fields=["name"])
    qs = MagicMock()

    result = flt.filter(qs, [])

    assert result is qs
    qs.order_by.assert_not_called()


# ============================================================================
# Tier 2 — DB / factory tests
# ============================================================================


@pytest.fixture
def slug_business_area():
    return BusinessAreaFactory(name="Initial", code="INI001")


@pytest.mark.django_db
def test_unique_slugify_assigns_initial_slug(slug_business_area):
    fresh = BusinessArea(name="Fresh", code="FR1")
    unique_slugify(fresh, "Brand New Area")
    assert fresh.slug == "brand-new-area"


@pytest.mark.django_db
def test_unique_slugify_appends_counter_on_collision(slug_business_area):
    BusinessAreaFactory(name="Taken Slug", code="TS001")
    fresh = BusinessArea(name="X", code="X1")
    unique_slugify(fresh, "Taken Slug")
    assert fresh.slug == "taken-slug-2"


@pytest.mark.django_db
def test_unique_slugify_excludes_existing_pk_from_uniqueness_check(slug_business_area):
    unique_slugify(slug_business_area, "Initial")
    assert slug_business_area.slug == "initial"


@pytest.mark.django_db
def test_unique_slugify_handles_alternate_separator():
    fresh = BusinessArea(name="X", code="X2")
    unique_slugify(fresh, "Alpha Beta", slug_separator="_")
    assert fresh.slug == "alpha_beta"


@pytest.mark.django_db
def test_unique_slugify_uses_explicit_queryset_when_provided():
    BusinessAreaFactory(name="Custom Source", code="CS001")
    fresh = BusinessArea(name="X", code="X3")

    unique_slugify(fresh, "Custom Source", queryset=BusinessArea.objects.none())

    assert fresh.slug == "custom-source"


@pytest.mark.django_db
def test_unique_slugify_truncates_slug_when_collision_exceeds_max_length(monkeypatch):
    BusinessAreaFactory(name="Aaaa", code="A1")
    fresh = BusinessArea(name="Y", code="Y1")
    slug_field = BusinessArea._meta.get_field("slug")
    monkeypatch.setattr(slug_field, "max_length", 5)

    unique_slugify(fresh, "Aaaa")

    assert fresh.slug == "aaa-2"


@pytest.mark.django_db
def test_unique_slugify_handles_empty_separator():
    fresh = BusinessArea(name="Z", code="Z1")
    unique_slugify(fresh, "Plain Name", slug_separator="")
    assert fresh.slug == "plainname"


@pytest.mark.django_db
def test_unique_slugify_skips_self_exclude_when_instance_has_no_pk():
    fresh = BusinessArea(name="W", code="W1")
    fresh.pk = None

    unique_slugify(fresh, "Some Brand New Name")

    assert fresh.slug == "some-brand-new-name"


@pytest.mark.django_db
def test_unique_slugify_works_with_slug_field_without_max_length(monkeypatch):
    fresh = BusinessArea(name="V", code="V1")
    slug_field = BusinessArea._meta.get_field("slug")
    monkeypatch.setattr(slug_field, "max_length", None)

    unique_slugify(fresh, "Unbounded Slug Name")

    assert fresh.slug == "unbounded-slug-name"


@pytest.mark.django_db
def test_serialize_flex_attributes_groups_by_associated_with():
    individual_attr = FlexibleAttributeFactory(
        name="ind_attr",
        type=FlexibleAttribute.SELECT_ONE,
        associated_with=FlexibleAttribute.ASSOCIATED_WITH_INDIVIDUAL,
    )
    FlexibleAttributeFactory(
        name="hh_attr",
        type=FlexibleAttribute.STRING,
        associated_with=FlexibleAttribute.ASSOCIATED_WITH_HOUSEHOLD,
    )
    pdu_attr = FlexibleAttributeForPDUFactory(label="PDU Excluded")
    choice = FlexibleAttributeChoiceFactory(name="yes", label={"English(EN)": "Yes"})
    choice.flex_attributes.add(individual_attr)

    result = serialize_flex_attributes()

    assert "ind_attr" in result["individuals"]
    assert "hh_attr" in result["households"]
    assert pdu_attr.name not in result["individuals"]
    assert pdu_attr.name not in result["households"]
    assert result["individuals"]["ind_attr"]["associated_with"] == "Individual"
    assert result["individuals"]["ind_attr"]["choices"] == [{"label": {"English(EN)": "Yes"}, "value": "yes"}]


@pytest.mark.django_db
def test_get_combined_attributes_merges_core_fields_and_flex():
    FlexibleAttributeFactory(
        name="combined_ind",
        type=FlexibleAttribute.STRING,
        associated_with=FlexibleAttribute.ASSOCIATED_WITH_INDIVIDUAL,
    )

    result = get_combined_attributes()

    assert "combined_ind" in result
    assert any(key for key in result if key != "combined_ind")


@pytest.mark.django_db
def test_resolve_flex_fields_choices_select_one_stringifies_value():
    FlexibleAttributeFactory(name="select_one_field", type=FlexibleAttribute.SELECT_ONE)
    parent = MagicMock()
    parent.flex_fields = {"select_one_field": 42}

    result = resolve_flex_fields_choices_to_string(parent)

    assert result == {"select_one_field": "42"}


@pytest.mark.django_db
def test_resolve_flex_fields_choices_select_many_stringifies_list():
    FlexibleAttributeFactory(name="select_many_field", type=FlexibleAttribute.SELECT_MANY)
    parent = MagicMock()
    parent.flex_fields = {"select_many_field": [1, 2, 3]}

    result = resolve_flex_fields_choices_to_string(parent)

    assert result == {"select_many_field": ["1", "2", "3"]}


@pytest.mark.django_db
def test_resolve_flex_fields_choices_pdu_strips_none_value_rounds():
    FlexibleAttributeForPDUFactory(label="PDU One")
    parent = MagicMock()
    parent.flex_fields = {
        "pdu_one": {
            "1": {"value": "kept"},
            "2": {"value": None},
        }
    }

    result = resolve_flex_fields_choices_to_string(parent)

    assert result["pdu_one"] == {"1": {"value": "kept"}}


@pytest.mark.django_db
def test_resolve_flex_fields_choices_pdu_drops_field_when_all_rounds_none():
    FlexibleAttributeForPDUFactory(label="PDU All None")
    parent = MagicMock()
    parent.flex_fields = {"pdu_all_none": {"1": {"value": None}}}

    result = resolve_flex_fields_choices_to_string(parent)

    assert "pdu_all_none" not in result


@pytest.mark.django_db
def test_resolve_flex_fields_choices_image_returns_storage_url():
    FlexibleAttributeFactory(name="image_field", type=FlexibleAttribute.IMAGE)
    parent = MagicMock()
    parent.flex_fields = {"image_field": "uploads/photo.png"}

    result = resolve_flex_fields_choices_to_string(parent)

    assert result["image_field"].endswith("uploads/photo.png")


@pytest.mark.django_db
def test_resolve_flex_fields_choices_skips_unknown_flex_field():
    parent = MagicMock()
    parent.flex_fields = {"unknown": "value"}

    result = resolve_flex_fields_choices_to_string(parent)

    assert result == {"unknown": "value"}


@pytest.mark.django_db
def test_resolve_flex_fields_choices_image_returns_empty_string_for_falsy_value():
    FlexibleAttributeFactory(name="empty_image_field", type=FlexibleAttribute.IMAGE)
    parent = MagicMock()
    parent.flex_fields = {"empty_image_field": ""}

    result = resolve_flex_fields_choices_to_string(parent)

    assert result["empty_image_field"] == ""


@pytest.mark.django_db
def test_get_fields_attr_generators_yields_only_flex_when_flex_field_true():
    flex = FlexibleAttributeFactory(name="only_flex", type=FlexibleAttribute.STRING)

    result = list(get_fields_attr_generators(flex_field=True))

    assert flex in result


@pytest.mark.django_db
def test_get_fields_attr_generators_yields_only_core_when_flex_field_false():
    FlexibleAttributeFactory(name="excluded_flex", type=FlexibleAttribute.STRING)

    result = list(get_fields_attr_generators(flex_field=False))

    assert all(getattr(item, "name", None) != "excluded_flex" for item in result)
    assert len(result) > 0


@pytest.mark.django_db
def test_get_fields_attr_generators_for_social_worker_program_uses_xlsx_people_scope():
    from extras.test_utils.factories.core import BeneficiaryGroupFactory, DataCollectingTypeFactory
    from hope.models import DataCollectingType

    program = ProgramFactory(
        data_collecting_type=DataCollectingTypeFactory(type=DataCollectingType.Type.SOCIAL),
        beneficiary_group=BeneficiaryGroupFactory(master_detail=False),
    )

    result = list(get_fields_attr_generators(flex_field=False, program_id=str(program.id)))

    assert isinstance(result, list)


@pytest.mark.django_db
def test_map_unicef_ids_handles_empty_string():
    assert map_unicef_ids_to_households_unicef_ids("") == []


@pytest.mark.django_db
def test_map_unicef_ids_separates_hh_and_ind_prefixes_and_resolves(business_area, program):
    household = HouseholdFactory(business_area=business_area, program=program)
    Household.objects.filter(pk=household.pk).update(unicef_id="HH-9001")
    Individual.objects.filter(household=household).update(unicef_id="IND-9001")

    result = map_unicef_ids_to_households_unicef_ids("HH-9001, IND-9001")

    assert result.count("HH-9001") == 2


def test_clear_cache_for_key_removes_only_matching_keys(mocker):
    mock_cache = mocker.patch("hope.apps.core.utils.cache")
    mock_cache.keys.return_value = ["FOO_a", "FOO_b"]

    clear_cache_for_key("FOO_")

    mock_cache.keys.assert_called_once_with("FOO_*")
    assert mock_cache.delete.call_args_list == [mocker.call("FOO_a"), mocker.call("FOO_b")]


def test_clear_cache_for_key_is_noop_when_cache_lacks_keys_method(mocker):
    sentinel = mocker.patch("hope.apps.core.utils.cache", spec=["set", "get", "delete"])

    clear_cache_for_key("FOO_")

    sentinel.delete.assert_not_called()


@pytest.mark.django_db
def test_resolve_assets_list_returns_reduced_list(mocker):
    BusinessAreaFactory(name="kobo-ba", code="KB001")
    mocker.patch("hope.apps.core.kobo.api.KoboAPI.get_all_projects_data", return_value=[{"results": []}])
    mocker.patch("hope.apps.core.kobo.common.reduce_assets_list", return_value=[{"id": "asset"}])

    result = resolve_assets_list("kobo-ba")

    assert result == [{"id": "asset"}]


@pytest.mark.django_db
def test_resolve_assets_list_raises_validation_error_when_business_area_missing():
    with pytest.raises(ValidationError, match="does not exist"):
        resolve_assets_list("missing-slug")


@pytest.mark.django_db
def test_resolve_assets_list_raises_validation_error_on_attribute_error(mocker):
    BusinessAreaFactory(name="kobo-attr-err", code="KAE01")
    mocker.patch("hope.apps.core.kobo.api.KoboAPI.get_all_projects_data", side_effect=AttributeError("kobo broken"))

    with pytest.raises(ValidationError, match="kobo broken"):
        resolve_assets_list("kobo-attr-err")


@pytest.mark.django_db
def test_to_dict_uses_all_model_fields_when_none_provided(business_area):
    result = to_dict(business_area)

    assert "slug" in result
    assert result["slug"] == "afghanistan"


@pytest.mark.django_db
def test_to_dict_skips_fields_missing_on_instance(business_area):
    result = to_dict(business_area, fields=["slug", "nonexistent_attr"])

    assert result["slug"] == "afghanistan"
    assert "nonexistent_attr" not in result
