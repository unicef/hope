"""Guardrail for the cross business area IDOR class of bug (GHSA-2xf8-jjc2-9pmv).

Permissions are checked against the business area and the program of the url path, while an object
referenced by id in the request body is loaded globally. A writable relation field over a model that
carries business area or program data therefore has to narrow its queryset to the scope of the path,
which is what ScopedRelatedField does.

This test walks every REST route, instantiates the serializer of every write action and fails on any
such field that is neither scoped nor listed below. Adding a field to the allow list is a deliberate
decision that needs a reason next to it.
"""

from django.urls import get_resolver
import pytest
from rest_framework import serializers
from rest_framework.relations import ManyRelatedField, RelatedField

from hope.apps.core.api.fields import ScopedRelatedFieldMixin

# Fields of these models never belong to a single business area.
GLOBAL_MODELS = {"BusinessArea", "Partner", "Area", "AreaType", "Country", "User", "Role"}

# Model fields that place an object inside a business area or a program.
SCOPE_FIELDS = {"business_area", "program", "program_cycle", "payment_plan"}

WRITE_ACTIONS = ("create", "update", "copy", "import", "assign", "message", "sample", "approve", "reassign", "split")

# (viewset, action, field): why it does not have to be scoped.
ALLOWED_UNSCOPED = {
    # The view checks the office of every item against the business area of the payment plan it is
    # assigning them to, and that plan comes from the scoped get_object.
    ("PaymentPlanViewSet", "assign_funds_commitments", "fund_commitment_items_ids.<cannot instantiate>"),
}


def _scope_fields_of(model: type) -> list[str]:
    if model.__name__ in GLOBAL_MODELS:
        return []
    names = {field.name for field in model._meta.get_fields()}
    return sorted(names & SCOPE_FIELDS)


def _filtered_fields(node: object) -> set[str]:
    """Model fields the queryset already compares against, whatever the depth of the relation."""
    target = getattr(getattr(node, "lhs", None), "target", None)
    if target is not None:
        return {target.name}
    return {name for child in getattr(node, "children", ()) for name in _filtered_fields(child)}


def _is_already_scoped(field: RelatedField) -> bool:
    if isinstance(field, ScopedRelatedFieldMixin):
        return True
    queryset = field.queryset
    # the name of the table shows up in the repr of the where clause, so the fields it compares
    # have to be read from the tree instead of matched as text
    return queryset is not None and bool(_filtered_fields(queryset.all().query.where) & SCOPE_FIELDS)


def _viewsets_of_rest_api() -> set[type]:
    found = set()

    def walk(patterns: list, prefix: str = "") -> None:
        for pattern in patterns:
            if hasattr(pattern, "url_patterns"):
                walk(pattern.url_patterns, prefix + str(pattern.pattern))
                continue
            viewset = getattr(pattern.callback, "cls", None)
            if viewset is not None and (prefix + str(pattern.pattern)).startswith("api/rest"):
                found.add(viewset)

    walk(get_resolver().url_patterns)
    return found


def _serializers_of(viewset: type) -> dict:
    found = dict(getattr(viewset, "serializer_classes_by_action", {}) or {})
    if getattr(viewset, "serializer_class", None) is not None:
        found.setdefault("<default>", viewset.serializer_class)
    return found


def _unwrap(field: object) -> object:
    """Reach the field that actually resolves an id through list and many wrappers."""
    while isinstance(field, ManyRelatedField) or isinstance(getattr(field, "child_relation", None), RelatedField):
        field = field.child_relation
    if isinstance(getattr(field, "child", None), (RelatedField, serializers.BaseSerializer)):
        field = field.child
    return field


def _unscoped_relation_fields(serializer_cls: type, seen: set | None = None) -> list[tuple[str, bool]]:
    """Writable relation fields over models with business area or program data, and whether they are scoped."""
    seen = seen if seen is not None else set()
    if serializer_cls in seen:
        return []
    seen.add(serializer_cls)
    try:
        fields = serializer_cls().fields
    except Exception:  # noqa: BLE001 - a serializer that cannot be built has to be looked at by hand
        return [("<cannot instantiate>", False)]

    found = []
    for name, declared in fields.items():
        if declared.read_only:
            continue
        field = _unwrap(declared)
        if isinstance(field, RelatedField):
            if field.queryset is not None and _scope_fields_of(field.queryset.model):
                found.append((name, _is_already_scoped(field)))
        elif isinstance(field, serializers.BaseSerializer):
            found.extend(
                (f"{name}.{nested_name}", scoped)
                for nested_name, scoped in _unscoped_relation_fields(type(field), seen)
            )
    return found


def collect_unscoped_fields() -> set[tuple[str, str, str]]:
    found = set()
    for viewset in _viewsets_of_rest_api():
        for action, serializer_cls in _serializers_of(viewset).items():
            if action != "<default>" and not any(write in action for write in WRITE_ACTIONS):
                continue
            found.update(
                (viewset.__name__, action, name)
                for name, scoped in _unscoped_relation_fields(serializer_cls)
                if not scoped
            )
    return found


@pytest.mark.django_db
def test_every_writable_relation_field_over_scoped_data_is_scoped() -> None:
    assert collect_unscoped_fields() == ALLOWED_UNSCOPED
