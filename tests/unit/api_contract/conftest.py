import json

from django.core import serializers as _ser
from django.core.serializers.json import DjangoJSONEncoder as _DjangoEncoder
from django.db import DEFAULT_DB_ALIAS
from django.http.response import ResponseHeaders
import drf_api_checker.utils as _checker_utils

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

    Also restores M2M relations (e.g. Group.permissions) which
    ``save_base()`` does not handle.
    """
    Model = deserialized_obj.object.__class__  # noqa: N806
    pk = deserialized_obj.object.pk
    if pk is not None and Model.objects.using(using).filter(pk=pk).exists():
        deserialized_obj.object.save_base(using=using, raw=True, force_update=True)
    else:
        deserialized_obj.object.save_base(using=using, raw=True)
    if deserialized_obj.m2m_data:
        for accessor_name, object_list in deserialized_obj.m2m_data.items():
            getattr(deserialized_obj.object, accessor_name).set(object_list)


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
