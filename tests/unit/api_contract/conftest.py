import json

from django.core import serializers as _ser
from django.core.serializers.json import DjangoJSONEncoder as _DjangoEncoder
from django.db import DEFAULT_DB_ALIAS
from django.http.response import ResponseHeaders
import drf_api_checker.utils as _checker_utils
import factory.base
from freezegun import freeze_time
import pytest

FROZEN_TIME = "2025-01-01T00:00:00Z"

# ---------------------------------------------------------------------------
# Monkeypatch 1: ResponseEncoder
#
# The library's ResponseEncoder has a commented-out fallback
# (``return json.JSONEncoder.default(self, obj)``), so any type
# it doesn't explicitly handle (UUID, Decimal, date, lazy strings ...)
# silently serializes to ``null``.
#
# We replace it with DjangoJSONEncoder (which handles all those types)
# plus explicit ResponseHeaders support.
# ---------------------------------------------------------------------------


class _HopeEncoder(_DjangoEncoder):
    def default(self, obj):
        if isinstance(obj, ResponseHeaders):
            return dict(obj)
        if isinstance(obj, set):
            return sorted(obj)
        return super().default(obj)


_checker_utils.ResponseEncoder = _HopeEncoder


# ---------------------------------------------------------------------------
# Monkeypatch 2: load_fixtures
#
# The library's load_fixtures saves objects in ``master + deps`` order,
# but FK targets (deps) must exist BEFORE the master.  We reverse the
# order to ``deps + master`` so FK constraints are satisfied.
# Additionally, uses save-or-update to handle objects that already exist
# in the DB (e.g. deps shared across multiple frozenfixtures).
# ---------------------------------------------------------------------------


def _save_or_update(deserialized_obj, using):
    """Save a deserialized object, falling back to UPDATE on duplicate key.

    Handles both pk-based existence and unique-constraint conflicts (e.g.
    two fixtures that reference ``Partner`` with the same ``name`` but
    different PKs).  Also restores M2M relations (e.g. Group.permissions)
    which ``save_base()`` does not handle.
    """
    model = deserialized_obj.object.__class__
    obj = deserialized_obj.object
    pk = obj.pk

    if pk is not None and model.objects.using(using).filter(pk=pk).exists():
        obj.save_base(using=using, raw=True, force_update=True)
    else:
        existing = _find_conflicting_object(model, obj, using)
        if existing is not None:
            for f in model._meta.local_fields:
                if not f.primary_key:
                    setattr(existing, f.attname, getattr(obj, f.attname))
            existing.save_base(using=using, raw=True, force_update=True)
            deserialized_obj.object = existing
        else:
            obj.save_base(using=using, raw=True)

    if deserialized_obj.m2m_data:
        for accessor_name, object_list in deserialized_obj.m2m_data.items():
            getattr(deserialized_obj.object, accessor_name).set(object_list)


def _find_conflicting_object(model, obj, using):
    """Search for an existing row that would conflict on unique constraints."""
    for field in model._meta.local_fields:
        if field.unique and not field.primary_key:
            val = getattr(obj, field.attname)
            if val is not None:
                try:
                    return model.objects.using(using).get(**{field.attname: val})
                except model.DoesNotExist:
                    continue
    return None


def _load_fixtures_fixed(file, ignorenonexistent=False, using=DEFAULT_DB_ALIAS):
    content = json.loads(_checker_utils._read(file))
    ret = {}
    for name, struct in content.items():
        master = struct["master"]
        many = isinstance(master, (list, tuple))
        deps = struct["deps"]
        if not many:
            master = [master]

        # deps reversed (deepest FK targets first), then master.
        # The library serializes deps in discovery order (shallow→deep),
        # but DB inserts need deep→shallow so FK targets exist first.
        objects = _ser.deserialize(
            "json",
            json.dumps(list(reversed(deps)) + master),
            using=using,
            ignorenonexistent=ignorenonexistent,
        )
        saved = []
        for obj in objects:
            _save_or_update(obj, using)
            saved.append(obj.object)

        # saved has [*deps, *master] — extract only master objects from the end
        master_objects = saved[len(deps) :]
        if many:
            ret[name] = master_objects
        else:
            ret[name] = master_objects[0]
    return ret


_checker_utils.load_fixtures = _load_fixtures_fixed


# ---------------------------------------------------------------------------
# Reset factory_boy sequences before each test so that parallel workers
# (-n auto) produce deterministic values regardless of execution order.
# ---------------------------------------------------------------------------


def _all_factory_subclasses(cls):
    for sc in cls.__subclasses__():
        yield sc
        yield from _all_factory_subclasses(sc)


@pytest.fixture(autouse=True)
def _reset_factory_sequences():
    for subcls in _all_factory_subclasses(factory.base.BaseFactory):
        subcls.reset_sequence(0, force=True)


@pytest.fixture(autouse=True)
def _freeze_time():
    with freeze_time(FROZEN_TIME, ignore=["elasticsearch", "elasticsearch_dsl"]):
        yield
