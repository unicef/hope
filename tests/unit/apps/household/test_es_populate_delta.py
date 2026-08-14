"""Tests for the es_populate_delta management command (incremental, never deletes an index).

ES-touching bits (server version probe, per-program doc classes, ES connection, create/populate,
remove-by-id) are mocked, so these tests need no live Elasticsearch cluster. The DB-only per-program
delta detection (`_program_delta`) is exercised directly against factories.
"""

import datetime
from io import StringIO
from unittest.mock import MagicMock, patch
import uuid

from constance.test import override_config
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
from hope.models import Household, Individual, Program

pytestmark = pytest.mark.django_db

CMD = "es_populate_delta"
_MOD = "hope.apps.household.management.commands.es_populate_delta"
CHECK = f"{_MOD}.check_program_indexes"
CREATE = f"{_MOD}.create_program_indexes"
POPULATE = f"{_MOD}.populate_program_indexes"
PROCESS = f"{_MOD}.Command._process_program"
DELTA = f"{_MOD}.Command._program_delta"
APPLY = f"{_MOD}.Command._apply_delta"
GET_IND_DOC = "hope.apps.household.documents.get_individual_doc"
GET_HH_DOC = "hope.apps.household.documents.get_household_doc"
GET_CONN = "elasticsearch.dsl.connections.get_connection"
REMOVE = "hope.apps.utils.elasticsearch_utils.remove_elasticsearch_documents_by_matching_ids"

OPTS = {"dry_run": False, "chunk_size": 2000, "parallel": False}


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


# ── _program_delta (per-program record-level delta) ───────────────────────────


def test_program_delta_direct_individual_change_is_present() -> None:
    prog = ProgramFactory(status=Program.ACTIVE)
    since = timezone.now() - datetime.timedelta(days=1)
    ind = IndividualFactory(program=prog, business_area=prog.business_area)

    delta = Command._program_delta(str(prog.id), since)

    assert ind.id in delta["ind_present"]
    assert ind.id not in delta["ind_removed"]


def test_program_delta_changed_document_marks_owner_present() -> None:
    prog = ProgramFactory(status=Program.ACTIVE)
    since = timezone.now()
    past = since - datetime.timedelta(hours=1)
    ind = IndividualFactory(program=prog, business_area=prog.business_area)
    Individual.all_merge_status_objects.filter(pk=ind.pk).update(updated_at=past)  # not via direct
    DocumentFactory(individual=ind)  # fresh updated_at -> triggers via documents

    delta = Command._program_delta(str(prog.id), since)

    assert ind.id in delta["ind_present"]


def test_program_delta_changed_identity_marks_owner_present() -> None:
    prog = ProgramFactory(status=Program.ACTIVE)
    since = timezone.now()
    past = since - datetime.timedelta(hours=1)
    ind = IndividualFactory(program=prog, business_area=prog.business_area)
    Individual.all_merge_status_objects.filter(pk=ind.pk).update(updated_at=past)
    IndividualIdentityFactory(individual=ind)  # fresh `modified` -> triggers via identities

    delta = Command._program_delta(str(prog.id), since)

    assert ind.id in delta["ind_present"]


def test_program_delta_soft_deleted_individual_goes_to_removed() -> None:
    prog = ProgramFactory(status=Program.ACTIVE)
    since = timezone.now()
    future = since + datetime.timedelta(hours=1)
    ind = IndividualFactory(program=prog, business_area=prog.business_area)
    Individual.all_objects.filter(pk=ind.pk).update(is_removed=True, updated_at=future)

    delta = Command._program_delta(str(prog.id), since)

    assert ind.id in delta["ind_removed"]
    assert ind.id not in delta["ind_present"]


def test_program_delta_direct_household_change_is_present() -> None:
    prog = ProgramFactory(status=Program.ACTIVE)
    since = timezone.now() - datetime.timedelta(days=1)
    hh = HouseholdFactory(program=prog, business_area=prog.business_area)

    delta = Command._program_delta(str(prog.id), since)

    assert hh.id in delta["hh_present"]


def test_program_delta_household_change_marks_members_present() -> None:
    # Individual doc embeds household.unicef_id / admin1 / admin2 -> a household change must
    # re-index its members even if the member individual itself did not change.
    prog = ProgramFactory(status=Program.ACTIVE)
    since = timezone.now()
    past = since - datetime.timedelta(hours=1)
    hh = HouseholdFactory(program=prog, business_area=prog.business_area)  # fresh updated_at
    member = IndividualFactory(program=prog, business_area=prog.business_area, household=hh)
    Individual.all_merge_status_objects.filter(pk=member.pk).update(updated_at=past)  # not via direct

    delta = Command._program_delta(str(prog.id), since)

    assert member.id in delta["ind_present"]


def test_program_delta_head_change_marks_household_present() -> None:
    # Household doc embeds the head's own name/phone fields -> a change to the head individual
    # must re-index the household.
    prog = ProgramFactory(status=Program.ACTIVE)
    since = timezone.now()
    past = since - datetime.timedelta(hours=1)
    head = IndividualFactory(program=prog, business_area=prog.business_area)  # fresh updated_at
    hh = HouseholdFactory(program=prog, business_area=prog.business_area, head_of_household=head)
    Household.objects.filter(pk=hh.pk).update(updated_at=past)  # not via direct

    delta = Command._program_delta(str(prog.id), since)

    assert hh.id in delta["hh_present"]


def test_program_delta_head_document_marks_household_present() -> None:
    prog = ProgramFactory(status=Program.ACTIVE)
    since = timezone.now()
    past = since - datetime.timedelta(hours=1)
    head = IndividualFactory(program=prog, business_area=prog.business_area)
    hh = HouseholdFactory(program=prog, business_area=prog.business_area, head_of_household=head)
    Household.objects.filter(pk=hh.pk).update(updated_at=past)  # not via direct
    DocumentFactory(individual=head)  # head's doc changed -> household doc embed must refresh

    delta = Command._program_delta(str(prog.id), since)

    assert hh.id in delta["hh_present"]


# ── _reference_data_changed ───────────────────────────────────────────────────


def test_reference_data_change_is_detected() -> None:
    from hope.models import BusinessArea

    since = timezone.now()
    future = since + datetime.timedelta(hours=1)
    ba = BusinessAreaFactory()
    BusinessArea.objects.filter(pk=ba.pk).update(updated_at=future)

    assert "BusinessArea" in Command._reference_data_changed(since)


def test_reference_data_unchanged_returns_empty() -> None:
    BusinessAreaFactory()
    since = timezone.now() + datetime.timedelta(hours=1)
    assert Command._reference_data_changed(since) == []


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
    assert ids(program=str(p2.id), business_area=ba.slug) == set()


# ── _process_program (missing index vs delta vs no-delta) ─────────────────────


@patch(POPULATE, return_value=(True, "done"))
@patch(CREATE, return_value=(True, ""))
@patch(GET_HH_DOC)
@patch(GET_IND_DOC)
@patch(GET_CONN)
def test_process_program_missing_index_creates_and_populates(
    mock_conn, mock_ind_doc, mock_hh_doc, mock_create, mock_populate
) -> None:
    mock_conn.return_value.indices.exists.return_value = False

    status, _ = Command()._process_program(str(uuid.uuid4()), timezone.now(), "default", OPTS)

    assert status.startswith("populated")
    mock_create.assert_called_once()
    mock_populate.assert_called_once()


@patch(DELTA, return_value={"ind_present": set(), "ind_removed": set(), "hh_present": set(), "hh_removed": set()})
@patch(GET_HH_DOC)
@patch(GET_IND_DOC)
@patch(GET_CONN)
def test_process_program_existing_index_no_delta(mock_conn, mock_ind_doc, mock_hh_doc, mock_delta) -> None:
    mock_conn.return_value.indices.exists.return_value = True

    status, _ = Command()._process_program(str(uuid.uuid4()), timezone.now(), "default", OPTS)

    assert status == "no delta"


@patch(APPLY)
@patch(DELTA, return_value={"ind_present": {1}, "ind_removed": set(), "hh_present": set(), "hh_removed": set()})
@patch(GET_HH_DOC)
@patch(GET_IND_DOC)
@patch(GET_CONN)
def test_process_program_existing_index_applies_delta(
    mock_conn, mock_ind_doc, mock_hh_doc, mock_delta, mock_apply
) -> None:
    mock_conn.return_value.indices.exists.return_value = True

    status, _ = Command()._process_program(str(uuid.uuid4()), timezone.now(), "default", OPTS)

    assert status == "delta synced"
    mock_apply.assert_called_once()


@patch(APPLY)
@patch(DELTA, return_value={"ind_present": {1}, "ind_removed": set(), "hh_present": set(), "hh_removed": set()})
@patch(GET_HH_DOC)
@patch(GET_IND_DOC)
@patch(GET_CONN)
def test_process_program_dry_run_does_not_apply(mock_conn, mock_ind_doc, mock_hh_doc, mock_delta, mock_apply) -> None:
    mock_conn.return_value.indices.exists.return_value = True
    opts = {**OPTS, "dry_run": True}

    status, _ = Command()._process_program(str(uuid.uuid4()), timezone.now(), "default", opts)

    assert status.startswith("would-sync")
    mock_apply.assert_not_called()


@patch(DELTA, return_value={"ind_present": set(), "ind_removed": set(), "hh_present": set(), "hh_removed": set()})
@patch(f"{_MOD}.versioned_doc", side_effect=lambda doc, suffix: doc)
@patch(GET_HH_DOC)
@patch(GET_IND_DOC)
@patch(GET_CONN)
def test_process_program_target_suffix_wraps_both_docs(
    mock_conn, mock_ind_doc, mock_hh_doc, mock_versioned, mock_delta
) -> None:
    mock_conn.return_value.indices.exists.return_value = True
    opts = {**OPTS, "target_suffix": "v2"}

    Command()._process_program(str(uuid.uuid4()), timezone.now(), "default", opts)

    assert mock_versioned.call_count == 2
    assert all(call.args[1] == "v2" for call in mock_versioned.call_args_list)


@patch(CREATE)
@patch(f"{_MOD}.versioned_doc", side_effect=lambda doc, suffix: doc)
@patch(GET_HH_DOC)
@patch(GET_IND_DOC)
@patch(GET_CONN)
def test_process_program_target_suffix_missing_target_fails_never_creates(
    mock_conn, mock_ind_doc, mock_hh_doc, mock_versioned, mock_create
) -> None:
    mock_conn.return_value.indices.exists.return_value = False
    opts = {**OPTS, "target_suffix": "v2"}

    status, msg = Command()._process_program(str(uuid.uuid4()), timezone.now(), "default", opts)

    assert status == "failed"
    assert "es_reindex" in msg
    mock_create.assert_not_called()


# ── _apply_delta: upsert present, delete removed docs, never delete the index ──


@patch(REMOVE)
def test_apply_delta_upserts_present_and_removes_soft_deleted(mock_remove) -> None:
    prog = ProgramFactory(status=Program.ACTIVE)
    present = IndividualFactory(program=prog, business_area=prog.business_area)
    removed_id = uuid.uuid4()
    ind_doc = MagicMock()
    hh_doc = MagicMock()
    delta = {"ind_present": {present.id}, "ind_removed": {removed_id}, "hh_present": set(), "hh_removed": set()}

    Command._apply_delta(delta, ind_doc, hh_doc, "default", OPTS)

    ind_doc.return_value.update.assert_called_once()
    assert ind_doc.return_value.update.call_args.kwargs["action"] == "index"
    # no using= allowed: update() forwards unknown kwargs into Elasticsearch.bulk(), which rejects them
    assert "using" not in ind_doc.return_value.update.call_args.kwargs
    mock_remove.assert_called_once_with([str(removed_id)], ind_doc, using="default")


def test_command_never_imports_index_delete() -> None:
    # Hard guarantee for "never delete an index": the delete helper is not even in the module.
    import hope.apps.household.management.commands.es_populate_delta as mod

    assert not hasattr(mod, "delete_program_indexes")


# ── handle: argument validation ───────────────────────────────────────────────


def test_requires_since_or_reconcile() -> None:
    with pytest.raises(CommandError):
        call_command(CMD)


def test_target_suffix_with_reconcile_raises() -> None:
    with pytest.raises(CommandError, match="target-suffix"):
        call_command(CMD, "--reconcile", "--target-suffix", "v2")


def test_disabled_elasticsearch_flag_aborts() -> None:
    with pytest.raises(CommandError, match="IS_ELASTICSEARCH_ENABLED"):
        call_command(CMD, "--since", "2026-07-01T09:00:00Z")


# ── handle: --since orchestration / --reconcile / scope ───────────────────────


@patch(PROCESS, return_value=("delta synced", "ind +1/-0 hh +0/-0"))
@override_config(IS_ELASTICSEARCH_ENABLED=True)
def test_since_processes_every_active_program(mock_process) -> None:
    # No cross-program pre-filter: every in-scope program is handed to _process_program.
    prog = ProgramFactory(status=Program.ACTIVE)
    since = (timezone.now() - datetime.timedelta(days=1)).isoformat()

    call_command(CMD, "--since", since, stdout=StringIO())

    mock_process.assert_called_once()
    assert mock_process.call_args.args[0] == str(prog.id)


@patch(PROCESS, return_value=("failed", "boom"))
@override_config(IS_ELASTICSEARCH_ENABLED=True)
def test_since_failure_is_listed_and_command_errors(mock_process) -> None:
    prog = ProgramFactory(status=Program.ACTIVE)
    since = (timezone.now() - datetime.timedelta(days=1)).isoformat()
    out = StringIO()

    with pytest.raises(CommandError):
        call_command(CMD, "--since", since, stdout=out)

    printed = out.getvalue()
    assert "Failed programs" in printed
    assert prog.code in printed
    assert "boom" in printed


@patch(CHECK, return_value=(False, "count mismatch"))
@override_config(IS_ELASTICSEARCH_ENABLED=True)
def test_reconcile_reports_drift_read_only(mock_check) -> None:
    prog = ProgramFactory(status=Program.ACTIVE)
    out = StringIO()

    call_command(CMD, "--reconcile", stdout=out)

    printed = out.getvalue()
    assert "drift" in printed
    assert prog.code in printed


@patch(PROCESS)
@patch(CHECK, return_value=(True, "ok"))
@override_config(IS_ELASTICSEARCH_ENABLED=True)
def test_reconcile_only_does_not_sync(mock_check, mock_process) -> None:
    ProgramFactory(status=Program.ACTIVE)

    call_command(CMD, "--reconcile", stdout=StringIO())

    mock_process.assert_not_called()


@patch(PROCESS)
@override_config(IS_ELASTICSEARCH_ENABLED=True)
def test_scope_no_match_warns_and_skips(mock_process) -> None:
    ProgramFactory(status=Program.ACTIVE)
    since = (timezone.now() - datetime.timedelta(days=1)).isoformat()
    out = StringIO()

    call_command(CMD, "--since", since, "--program", "no-such-code", stdout=out)

    assert "No programs match" in out.getvalue()
    mock_process.assert_not_called()
