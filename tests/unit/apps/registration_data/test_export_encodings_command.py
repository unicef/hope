from datetime import UTC, datetime, timedelta
import json
from unittest import mock
from unittest.mock import patch
import uuid

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.management import call_command
from django.core.management.base import CommandError
import pytest

from extras.test_utils.factories import BusinessAreaFactory, IndividualFactory

pytestmark = pytest.mark.django_db

COMMAND_MODULE = "hope.apps.registration_data.management.commands.export_encodings"
COMMON_ARGS = ["--dedup-url", "https://dedup.test", "--dedup-token", "token"]


@pytest.fixture
def mock_client() -> mock.MagicMock:
    with patch(f"{COMMAND_MODULE}.DedupEngineClient") as client_class:
        client = client_class.return_value
        client.create_set.side_effect = lambda reference_pk, name: {"id": str(uuid.uuid4())}
        client.get_set.return_value = {"state": "Encoded"}
        client.create_export.side_effect = lambda reference_pk, set_ids, export_format: {
            "key": f"exports/1/{reference_pk}/{reference_pk}-{uuid.uuid4().hex[:6]}.{export_format}.zip",
            "state": "pending",
        }
        client.export_status.return_value = {"state": "pending"}
        yield client


@pytest.fixture
def afghanistan() -> object:
    return BusinessAreaFactory(slug="afghanistan", name="Afghanistan")


@pytest.fixture
def state_key() -> str:
    return f"export-encodings-tests/{uuid.uuid4().hex}/state.json"


def read_state(state_key: str) -> dict:
    with default_storage.open(state_key, "rb") as f:
        return json.load(f)


def write_state(state_key: str, state: dict) -> None:
    if default_storage.exists(state_key):
        default_storage.delete(state_key)
    default_storage.save(state_key, ContentFile(json.dumps(state).encode()))


def submit(state_key: str, extra: list[str] | None = None) -> None:
    call_command(
        "export_encodings",
        "--mode",
        "submit",
        "--state-file",
        state_key,
        "--business-areas",
        "afghanistan",
        *COMMON_ARGS,
        *(extra or []),
    )


def export(state_key: str, extra: list[str] | None = None) -> None:
    call_command("export_encodings", "--mode", "export", "--state-file", state_key, *COMMON_ARGS, *(extra or []))


def test_submit_chunks_deterministically_and_processes_each_chunk(
    mock_client: mock.MagicMock, afghanistan: object, state_key: str
) -> None:
    individuals = [IndividualFactory(business_area=afghanistan, photo=f"photo_{i}.jpg") for i in range(5)]
    # Excluded individuals must not be submitted.
    IndividualFactory(business_area=afghanistan, photo="")
    IndividualFactory(business_area=afghanistan, photo="w.jpg", withdrawn=True)
    IndividualFactory(business_area=afghanistan, photo="d.jpg", duplicate=True)

    submit(state_key, ["--chunk-size", "2"])

    state = read_state(state_key)
    assert state["upload_batch_size"] == 5000
    assert len(state["chunks"]) == 3  # 5 individuals / chunk size 2
    assert [chunk["index"] for chunk in state["chunks"]] == [0, 1, 2]
    assert all(chunk["step"] == "processed" for chunk in state["chunks"])
    assert [chunk["image_count"] for chunk in state["chunks"]] == [2, 2, 1]
    run_id = state["run_id"]
    assert state["chunks"][0]["reference_id"] == f"enc-afghanistan-{run_id}-00000"

    assert mock_client.create_set.call_count == 3
    assert mock_client.mark_ready.call_count == 3
    assert mock_client.process.call_count == 3
    mock_client.process.assert_called_with(state["chunks"][2]["set_id"], encode_only=True)

    # Filename-mode payload: reference_pk + storage key only, no image content.
    items = [item for call_args in mock_client.register_images.call_args_list for item in call_args.args[1]]
    assert all(set(item) == {"reference_pk", "filename"} for item in items)
    # Chunk membership is deterministic: ordered by individual id.
    assert [item["reference_pk"] for item in items] == sorted(str(individual.id) for individual in individuals)


def test_submit_resume_skips_already_uploaded_batches_and_processed_chunks(
    mock_client: mock.MagicMock, afghanistan: object, state_key: str
) -> None:
    for i in range(4):
        IndividualFactory(business_area=afghanistan, photo=f"photo_{i}.jpg")

    submit(state_key, ["--chunk-size", "4", "--upload-batch-size", "2"])
    assert mock_client.register_images.call_count == 2

    # Simulate a crash after the first of two batches was uploaded.
    state = read_state(state_key)
    state["chunks"][0]["step"] = "uploading"
    state["chunks"][0]["uploaded_batches"] = 1
    state["chunks"][0]["image_count"] = 2
    write_state(state_key, state)
    mock_client.register_images.reset_mock()
    mock_client.create_set.reset_mock()

    submit(state_key, ["--chunk-size", "4", "--upload-batch-size", "2"])

    mock_client.create_set.assert_not_called()  # set already exists
    assert mock_client.register_images.call_count == 1  # only the second batch
    state = read_state(state_key)
    assert state["chunks"][0]["step"] == "processed"
    assert state["chunks"][0]["image_count"] == 4

    # A fully processed state file is a no-op on re-run.
    mock_client.register_images.reset_mock()
    submit(state_key, ["--chunk-size", "4", "--upload-batch-size", "2"])
    mock_client.register_images.assert_not_called()


def test_submit_rejects_conflicting_pinned_parameters(
    mock_client: mock.MagicMock, afghanistan: object, state_key: str
) -> None:
    IndividualFactory(business_area=afghanistan, photo="photo.jpg")
    submit(state_key, ["--upload-batch-size", "1000"])

    with pytest.raises(CommandError, match="upload_batch_size"):
        submit(state_key, ["--upload-batch-size", "2000"])


def test_submit_rejects_unknown_business_area(mock_client: mock.MagicMock, state_key: str) -> None:
    with pytest.raises(CommandError, match="nosuchplace"):
        call_command(
            "export_encodings",
            "--mode",
            "submit",
            "--state-file",
            state_key,
            "--business-areas",
            "nosuchplace",
            *COMMON_ARGS,
        )


def test_status_updates_engine_state(mock_client: mock.MagicMock, afghanistan: object, state_key: str) -> None:
    IndividualFactory(business_area=afghanistan, photo="photo.jpg")
    submit(state_key)

    mock_client.get_set.return_value = {"state": "Encoding"}
    call_command("export_encodings", "--mode", "status", "--state-file", state_key, *COMMON_ARGS)

    state = read_state(state_key)
    assert state["chunks"][0]["engine_state"] == "Encoding"


def test_export_requests_export_when_all_chunks_encoded(
    mock_client: mock.MagicMock, afghanistan: object, state_key: str
) -> None:
    for i in range(3):
        IndividualFactory(business_area=afghanistan, photo=f"photo_{i}.jpg")
    submit(state_key, ["--chunk-size", "2"])

    mock_client.get_set.return_value = {"state": "Encoded"}
    export(state_key)

    state = read_state(state_key)
    export_entry = state["exports"]["afghanistan:npy"]
    assert export_entry["state"] == "pending"
    assert export_entry["key"].startswith("exports/1/afghanistan/")
    assert export_entry["format"] == "npy"  # default format
    assert export_entry["requested_at"]

    # Sets are passed in chunk-index order.
    expected_set_ids = [chunk["set_id"] for chunk in state["chunks"]]
    mock_client.create_export.assert_called_once_with(
        reference_pk="afghanistan", set_ids=expected_set_ids, export_format="npy"
    )


def test_export_format_flag_is_passed_and_recorded(
    mock_client: mock.MagicMock, afghanistan: object, state_key: str
) -> None:
    IndividualFactory(business_area=afghanistan, photo="photo.jpg")
    submit(state_key)

    export(state_key, ["--export-format", "jsonl"])

    state = read_state(state_key)
    export_entry = state["exports"]["afghanistan:jsonl"]
    assert export_entry["format"] == "jsonl"
    assert ".jsonl.zip" in export_entry["key"]
    assert mock_client.create_export.call_args.kwargs["export_format"] == "jsonl"


def test_both_export_formats_coexist_for_one_co(
    mock_client: mock.MagicMock, afghanistan: object, state_key: str
) -> None:
    IndividualFactory(business_area=afghanistan, photo="photo.jpg")
    submit(state_key)

    export(state_key, ["--export-format", "jsonl"])  # requests jsonl export
    mock_client.export_status.return_value = {
        "state": "ready",
        "url": "https://blob/a.jsonl.zip?sig=x",
        "expires_at": "2026-08-13T12:00:00Z",
    }
    export(state_key, ["--export-format", "jsonl"])  # polls jsonl -> ready

    # Requesting npy afterwards creates a second, independent export slot.
    export(state_key, ["--export-format", "npy"])

    state = read_state(state_key)
    assert state["exports"]["afghanistan:jsonl"]["state"] == "ready"
    assert state["exports"]["afghanistan:npy"]["state"] == "pending"
    assert ".npy.zip" in state["exports"]["afghanistan:npy"]["key"]
    assert mock_client.create_export.call_count == 2  # one per format
    # The ready jsonl entry was untouched by the npy request.
    assert state["exports"]["afghanistan:jsonl"]["url"].endswith("sig=x")


def test_export_skips_co_with_unencoded_chunks(
    mock_client: mock.MagicMock, afghanistan: object, state_key: str
) -> None:
    IndividualFactory(business_area=afghanistan, photo="photo.jpg")
    submit(state_key)

    mock_client.get_set.return_value = {"state": "Encoding"}
    export(state_key)

    mock_client.create_export.assert_not_called()
    assert read_state(state_key)["exports"] == {}


def test_export_poll_stores_signed_url_and_renews_it_on_repoll(
    mock_client: mock.MagicMock, afghanistan: object, state_key: str
) -> None:
    IndividualFactory(business_area=afghanistan, photo="photo.jpg")
    submit(state_key)
    export(state_key)  # requests the export, stores the key

    mock_client.export_status.return_value = {
        "state": "ready",
        "url": "https://blob/exports/1/afghanistan/a.zip?sig=first",
        "expires_at": "2026-08-13T12:00:00Z",
    }
    export(state_key)  # polls -> ready

    state = read_state(state_key)
    export_entry = state["exports"]["afghanistan:npy"]
    assert export_entry["state"] == "ready"
    assert export_entry["url"].endswith("sig=first")
    assert export_entry["expires_at"] == "2026-08-13T12:00:00Z"
    mock_client.export_status.assert_called_once_with(export_entry["key"])

    # Re-running export on a ready CO re-polls the same key and renews the URL.
    mock_client.export_status.return_value = {
        "state": "ready",
        "url": "https://blob/exports/1/afghanistan/a.zip?sig=renewed",
        "expires_at": "2026-08-20T12:00:00Z",
    }
    export(state_key)
    state = read_state(state_key)
    assert state["exports"]["afghanistan:npy"]["url"].endswith("sig=renewed")
    mock_client.create_export.assert_called_once()  # never re-requested


def test_export_failed_clears_key_and_next_run_rerequests(
    mock_client: mock.MagicMock, afghanistan: object, state_key: str
) -> None:
    IndividualFactory(business_area=afghanistan, photo="photo.jpg")
    submit(state_key)
    export(state_key)

    mock_client.export_status.return_value = {"state": "failed", "error": "boom"}
    export(state_key)

    state = read_state(state_key)
    export_entry = state["exports"]["afghanistan:npy"]
    assert export_entry["state"] == "failed"
    assert export_entry["key"] is None
    assert export_entry["error"] == "boom"

    # Next run re-POSTs under a fresh key.
    export(state_key)
    assert mock_client.create_export.call_count == 2
    state = read_state(state_key)
    assert state["exports"]["afghanistan:npy"]["state"] == "pending"
    assert state["exports"]["afghanistan:npy"]["key"]


def test_export_reposts_after_pending_timeout(mock_client: mock.MagicMock, afghanistan: object, state_key: str) -> None:
    IndividualFactory(business_area=afghanistan, photo="photo.jpg")
    submit(state_key)
    export(state_key)

    state = read_state(state_key)
    old_key = state["exports"]["afghanistan:npy"]["key"]
    state["exports"]["afghanistan:npy"]["requested_at"] = (datetime.now(UTC) - timedelta(hours=3)).isoformat()
    write_state(state_key, state)

    mock_client.export_status.return_value = {"state": "pending"}
    export(state_key)

    assert mock_client.create_export.call_count == 2
    state = read_state(state_key)
    assert state["exports"]["afghanistan:npy"]["key"] != old_key
    assert state["exports"]["afghanistan:npy"]["state"] == "pending"


def test_export_still_pending_within_timeout_does_not_repost(
    mock_client: mock.MagicMock, afghanistan: object, state_key: str
) -> None:
    IndividualFactory(business_area=afghanistan, photo="photo.jpg")
    submit(state_key)
    export(state_key)
    old_key = read_state(state_key)["exports"]["afghanistan:npy"]["key"]

    mock_client.export_status.return_value = {"state": "pending"}
    export(state_key)

    assert mock_client.create_export.call_count == 1
    assert read_state(state_key)["exports"]["afghanistan:npy"]["key"] == old_key


def test_status_and_export_require_submitted_state(mock_client: mock.MagicMock, state_key: str) -> None:
    with pytest.raises(CommandError, match="submit"):
        call_command("export_encodings", "--mode", "status", "--state-file", state_key, *COMMON_ARGS)
    with pytest.raises(CommandError, match="submit"):
        export(state_key)


def test_missing_credentials_raise_command_error(state_key: str, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DEDUPLICATION_ENGINE_API_URL", raising=False)
    monkeypatch.delenv("DEDUPLICATION_ENGINE_API_KEY", raising=False)
    with pytest.raises(CommandError, match="missing"):
        call_command(
            "export_encodings",
            "--mode",
            "status",
            "--state-file",
            state_key,
        )
