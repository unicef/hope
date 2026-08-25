"""Tests for the blue-green index-versioning helpers in index_management.

versioned_doc is exercised against REAL per-program Document classes (subclassing goes through the
elasticsearch-dsl metaclass, which a MagicMock cannot emulate); ES itself is a mock.
"""

from unittest.mock import MagicMock

import pytest

from extras.test_utils.factories import ProgramFactory
from hope.apps.household.documents import get_household_doc, get_individual_doc
from hope.apps.household.services.index_management import (
    create_versioned_index,
    existing_version_numbers,
    mapping_content_hash,
    versioned_doc,
)
from hope.models import Program

pytestmark = pytest.mark.django_db


@pytest.fixture
def program() -> Program:
    return ProgramFactory(status=Program.ACTIVE)


@pytest.fixture
def ind_doc(program: Program) -> type:
    return get_individual_doc(str(program.id))


@pytest.fixture
def hh_doc(program: Program) -> type:
    return get_household_doc(str(program.id))


def _es_with_versions(versions_by_name: dict) -> MagicMock:
    es = MagicMock()
    es.indices.get.side_effect = lambda **kw: {
        f"{name}_v{n}": {}
        for name, versions in versions_by_name.items()
        if kw["index"] == f"{name}_v*"
        for n in versions
    }
    return es


def test_versioned_doc_targets_suffixed_index(ind_doc: type) -> None:
    vdoc = versioned_doc(ind_doc, "v2")

    assert vdoc._index._name == f"{ind_doc._index._name}_v2"


def test_versioned_doc_leaves_base_class_untouched(ind_doc: type) -> None:
    base_name = ind_doc._index._name

    versioned_doc(ind_doc, "v2")

    assert ind_doc._index._name == base_name


def test_versioned_doc_inherits_queryset(program: Program, ind_doc: type) -> None:
    vdoc = versioned_doc(ind_doc, "v2")

    assert vdoc().get_queryset().model is ind_doc().get_queryset().model


def test_existing_version_numbers_parses_only_matching(ind_doc: type) -> None:
    name = ind_doc._index._name
    es = MagicMock()
    es.indices.get.return_value = {f"{name}_v1": {}, f"{name}_v7": {}, f"{name}_vX": {}, f"{name}other_v3": {}}

    assert sorted(existing_version_numbers(es, name)) == [1, 7]


def test_mapping_content_hash_ignores_meta() -> None:
    base = {"properties": {"full_name": {"type": "text"}}}

    assert mapping_content_hash(base) == mapping_content_hash({**base, "_meta": {"hope_mapping_hash": "x"}})


def test_mapping_content_hash_differs_on_content_change() -> None:
    base = {"properties": {"full_name": {"type": "text"}}}
    changed = {"properties": {"full_name": {"type": "keyword"}}}

    assert mapping_content_hash(base) != mapping_content_hash(changed)


def test_create_versioned_index_dark_has_no_alias_and_a_mapping_stamp(ind_doc: type) -> None:
    es = _es_with_versions({})

    target = create_versioned_index(es, ind_doc, suffix="v2", attach_alias=False)

    assert target == f"{ind_doc._index._name}_v2"
    kwargs = es.indices.create.call_args.kwargs
    assert kwargs["index"] == target
    assert kwargs["aliases"] is None
    assert kwargs["mappings"]["_meta"]["hope_mapping_hash"] == mapping_content_hash(kwargs["mappings"])


def test_create_versioned_index_auto_suffix_attaches_alias(ind_doc: type) -> None:
    name = ind_doc._index._name
    es = _es_with_versions({name: [1, 2]})

    target = create_versioned_index(es, ind_doc)

    assert target == f"{name}_v3"
    assert es.indices.create.call_args.kwargs["aliases"] == {name: {}}
