"""Tests for the es_mutate_stream dev/test command (change-stream generator + JSONL log)."""

from io import StringIO
import json
from pathlib import Path

from django.core.management import call_command
import pytest

from extras.test_utils.factories import HouseholdFactory, IndividualFactory
from hope.models import Individual

pytestmark = pytest.mark.django_db

CMD = "es_mutate_stream"
RECORD_KEYS = {
    "ts",
    "action",
    "model",
    "object_id",
    "individual_id",
    "household_id",
    "individual_unicef_id",
    "household_unicef_id",
    "field",
    "old",
    "new",
}


def _run(tmp_path: Path, *extra: str) -> list[dict]:
    log = tmp_path / "m.jsonl"
    call_command(CMD, "--sleep", "0", "--log", str(log), "--i-am-sure", *extra, stdout=StringIO())
    return [json.loads(line) for line in log.read_text().splitlines()]


def test_logs_parseable_records_with_all_keys(tmp_path: Path) -> None:
    HouseholdFactory()
    IndividualFactory()

    rows = _run(tmp_path, "--passes", "1", "--batch", "5", "--delete-every", "0")

    assert rows
    assert all(set(r) >= RECORD_KEYS for r in rows)


def test_individual_record_ids_and_field(tmp_path: Path) -> None:
    IndividualFactory()

    rows = _run(tmp_path, "--passes", "1", "--batch", "1", "--delete-every", "0")

    ind_rec = next(r for r in rows if r["model"] == "Individual")
    assert ind_rec["object_id"] == ind_rec["individual_id"]
    assert ind_rec["field"] == "given_name"
    assert ind_rec["old"] != ind_rec["new"]


def test_household_record_has_null_individual_side(tmp_path: Path) -> None:
    HouseholdFactory()

    rows = _run(tmp_path, "--passes", "1", "--batch", "1", "--delete-every", "0")

    hh_rec = next(r for r in rows if r["model"] == "Household")
    assert hh_rec["individual_id"] is None
    assert hh_rec["individual_unicef_id"] is None
    assert hh_rec["household_id"] == hh_rec["object_id"]
    assert hh_rec["field"] == "residence_status"  # embedded in ES doc -> verifiable, unlike size
    assert hh_rec["old"] != hh_rec["new"]


def test_soft_delete_is_logged(tmp_path: Path) -> None:
    ind = IndividualFactory()

    rows = _run(tmp_path, "--passes", "1", "--batch", "1", "--delete-every", "1")

    sd = next(r for r in rows if r["action"] == "soft_delete")
    assert sd["field"] == "is_removed"
    assert sd["old"] is False
    assert sd["new"] is True
    assert Individual.all_objects.get(pk=ind.pk).is_removed is True


def test_empty_db_warns_and_writes_no_log(tmp_path: Path) -> None:
    out = StringIO()
    log = tmp_path / "m.jsonl"

    call_command(CMD, "--sleep", "0", "--passes", "1", "--log", str(log), "--i-am-sure", stdout=out)

    assert "nothing to mutate" in out.getvalue()
    assert not log.exists()


def test_refuses_to_run_outside_debug_without_confirmation(tmp_path: Path, settings) -> None:
    from django.core.management.base import CommandError

    settings.DEBUG = False

    with pytest.raises(CommandError, match="--i-am-sure"):
        call_command(CMD, "--sleep", "0", "--passes", "1", "--log", str(tmp_path / "m.jsonl"), stdout=StringIO())
