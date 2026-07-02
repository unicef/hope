"""Tests for the es_populate_delta management command.

ES-touching helpers (rebuild_program_indexes / check_program_indexes) are mocked, so these
tests need no live Elasticsearch cluster: `--using default` is a registered alias and the
DB-only change-detection logic is exercised directly.
"""

import datetime
from io import StringIO
from unittest.mock import patch

from django.core.management import call_command
from django.core.management.base import CommandError
from django.utils import timezone
import pytest

from extras.test_utils.factories import (
    BusinessAreaFactory,
    DocumentFactory,
    HouseholdFactory,
    IndividualFactory,
    IndividualIdentityFactory,
    ProgramFactory,
)
from hope.apps.household.management.commands.es_populate_delta import Command
from hope.models import Household, Individual, IndividualIdentity, Program

pytestmark = pytest.mark.django_db

CMD = "es_populate_delta"
REBUILD = "hope.apps.household.management.commands.es_populate_delta.rebuild_program_indexes"
CHECK = "hope.apps.household.management.commands.es_populate_delta.check_program_indexes"


# ── _parse_since ─────────────────────────────────────────────────────────────


def test_parse_since_naive_is_made_aware() -> None:
    dt = Command._parse_since("2026-07-01T09:00:00")
    assert timezone.is_aware(dt)


def test_parse_since_accepts_z_suffix_as_utc() -> None:
    dt = Command._parse_since("2026-07-01T09:00:00Z")
    assert timezone.is_aware(dt)
    assert dt.utcoffset() == datetime.timedelta(0)


def test_parse_since_invalid_raises() -> None:
    with pytest.raises(CommandError):
        Command._parse_since("not-a-timestamp")


# ── _changed_program_ids (the core delta detection) ──────────────────────────


def test_changed_program_ids_detects_all_related_sources() -> None:
    since = timezone.now()
    past = since - datetime.timedelta(hours=1)
    future = since + datetime.timedelta(hours=1)

    # A: Individual changed after `since` -> detected.
    ind_a = IndividualFactory()
    Individual.all_merge_status_objects.filter(pk=ind_a.pk).update(updated_at=future)

    # B: Individual changed before `since` -> excluded.
    ind_b = IndividualFactory()
    Individual.all_merge_status_objects.filter(pk=ind_b.pk).update(updated_at=past)

    # C: Household changed after `since`, its members old -> detected via Household.
    hh_c = HouseholdFactory()
    Household.objects.filter(pk=hh_c.pk).update(updated_at=future)
    Individual.all_merge_status_objects.filter(household=hh_c).update(updated_at=past)

    # D: Document changed after `since`, its individual old -> detected via Document.
    doc_d = DocumentFactory()
    Individual.all_merge_status_objects.filter(pk=doc_d.individual_id).update(updated_at=past)
    from hope.models import Document

    Document.all_merge_status_objects.filter(pk=doc_d.pk).update(updated_at=future)

    # E: IndividualIdentity changed after `since` (model_utils `modified`), individual old.
    idy_e = IndividualIdentityFactory()
    Individual.all_merge_status_objects.filter(pk=idy_e.individual_id).update(updated_at=past)
    IndividualIdentity.all_merge_status_objects.filter(pk=idy_e.pk).update(modified=future)

    result = Command._changed_program_ids(since)

    assert ind_a.program_id in result
    assert ind_b.program_id not in result
    assert hh_c.program_id in result
    assert doc_d.individual.program_id in result  # via Document
    assert idy_e.individual.program_id in result  # via IndividualIdentity


# ── _apply_scope_filters ─────────────────────────────────────────────────────


def test_apply_scope_filters_by_code_uuid_and_business_area() -> None:
    ba = BusinessAreaFactory()
    p1 = ProgramFactory(business_area=ba)
    p2 = ProgramFactory()

    def ids(**opts: object) -> set:
        base = Program.objects.all()
        return set(Command._apply_scope_filters(base, opts).values_list("id", flat=True))

    assert ids(program=p1.code, business_area=None) == {p1.id}
    assert ids(program=str(p2.id), business_area=None) == {p2.id}
    assert ids(program=None, business_area=ba.slug) == {p1.id}
    # business area + program that isn't in it -> empty
    assert ids(program=str(p2.id), business_area=ba.slug) == set()


# ── handle: argument validation ──────────────────────────────────────────────


def test_requires_since_or_reconcile() -> None:
    with pytest.raises(CommandError):
        call_command(CMD, "--using", "default")


def test_unknown_using_alias_raises() -> None:
    with pytest.raises(CommandError):
        call_command(CMD, "--using", "does-not-exist", "--reconcile")


# ── handle: reconcile / since / failures / scope / dry-run ────────────────────


@patch(REBUILD, return_value=(True, "ok"))
@patch(CHECK, return_value=(False, "count mismatch"))
def test_reconcile_rebuilds_mismatched_programs(mock_check, mock_rebuild) -> None:
    prog = ProgramFactory(status=Program.ACTIVE)

    call_command(CMD, "--using", "default", "--reconcile", stdout=StringIO())

    mock_rebuild.assert_called_once()
    assert mock_rebuild.call_args.args[0] == str(prog.id)


@patch(REBUILD, return_value=(True, "ok"))
def test_since_rebuilds_changed_program(mock_rebuild) -> None:
    prog = ProgramFactory(status=Program.ACTIVE)
    IndividualFactory(program=prog, business_area=prog.business_area)
    since = (timezone.now() - datetime.timedelta(days=1)).isoformat()

    call_command(CMD, "--using", "default", "--since", since, stdout=StringIO())

    mock_rebuild.assert_called_once()
    assert mock_rebuild.call_args.args[0] == str(prog.id)


@patch(REBUILD, return_value=(False, "boom"))
@patch(CHECK, return_value=(False, "count mismatch"))
def test_failed_programs_are_listed_and_command_errors(mock_check, mock_rebuild) -> None:
    prog = ProgramFactory(status=Program.ACTIVE)
    out = StringIO()

    with pytest.raises(CommandError):
        call_command(CMD, "--using", "default", "--reconcile", stdout=out)

    printed = out.getvalue()
    assert "Failed programs" in printed
    assert prog.code in printed
    assert "boom" in printed


@patch(REBUILD)
def test_scope_filter_no_match_warns_and_skips(mock_rebuild) -> None:
    ProgramFactory(status=Program.ACTIVE)
    out = StringIO()

    call_command(CMD, "--using", "default", "--reconcile", "--program", "no-such-code", stdout=out)

    assert "No programs match" in out.getvalue()
    mock_rebuild.assert_not_called()


@patch(REBUILD)
@patch(CHECK, return_value=(False, "count mismatch"))
def test_dry_run_lists_programs_without_rebuilding(mock_check, mock_rebuild) -> None:
    prog = ProgramFactory(status=Program.ACTIVE)
    out = StringIO()

    call_command(CMD, "--using", "default", "--reconcile", "--dry-run", stdout=out)

    printed = out.getvalue()
    assert "summary:" in printed
    assert prog.code in printed
    mock_rebuild.assert_not_called()


@patch("hope.apps.household.management.commands.es_populate_delta.DRY_RUN_PRINT_LIMIT", 0)
@patch(REBUILD)
@patch(CHECK, return_value=(False, "count mismatch"))
def test_dry_run_suppresses_list_above_print_limit(mock_check, mock_rebuild) -> None:
    prog = ProgramFactory(status=Program.ACTIVE)
    out = StringIO()

    call_command(CMD, "--using", "default", "--reconcile", "--dry-run", stdout=out)

    printed = out.getvalue()
    assert "suppressed" in printed
    assert prog.code not in printed  # per-program list suppressed
    mock_rebuild.assert_not_called()
