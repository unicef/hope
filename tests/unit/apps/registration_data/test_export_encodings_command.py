from datetime import UTC, datetime, timedelta
import json
from typing import Any
from unittest import mock
from unittest.mock import patch
import uuid

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.management import call_command
from django.core.management.base import CommandError
import pytest

from extras.test_utils.factories import BusinessAreaFactory, IndividualFactory
from hope.apps.registration_data.management.commands.export_encodings import DedupEngineClient
from hope.models import BusinessArea, Individual

pytestmark = pytest.mark.django_db

COMMAND_MODULE = "hope.apps.registration_data.management.commands.export_encodings"
DEDUP_URL = "https://dedup.test"
DEDUP_TOKEN = "token"

SET_ID_0 = "00000000-0000-0000-0000-000000000000"
SET_ID_1 = "11111111-1111-1111-1111-111111111111"
PENDING_EXPORT_KEY = "exports/1/afghanistan/afghanistan-pending.npy.zip"


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
def afghanistan(db: Any) -> BusinessArea:
    return BusinessAreaFactory(slug="afghanistan", name="Afghanistan")


@pytest.fixture
def state_key() -> str:
    return f"export-encodings-tests/{uuid.uuid4().hex}/state.json"


@pytest.fixture
def individuals_for_chunk_submit(afghanistan: BusinessArea) -> list[Individual]:
    eligible = [
        IndividualFactory(business_area=afghanistan, photo="photo_0.jpg"),
        IndividualFactory(business_area=afghanistan, photo="photo_1.jpg"),
        IndividualFactory(business_area=afghanistan, photo="photo_2.jpg"),
        IndividualFactory(business_area=afghanistan, photo="photo_3.jpg"),
        IndividualFactory(business_area=afghanistan, photo="photo_4.jpg"),
    ]
    IndividualFactory(business_area=afghanistan, photo="")
    IndividualFactory(business_area=afghanistan, photo="w.jpg", withdrawn=True)
    IndividualFactory(business_area=afghanistan, photo="d.jpg", duplicate=True)
    return sorted(eligible, key=lambda individual: individual.id)


@pytest.fixture
def four_individuals_with_photos(afghanistan: BusinessArea) -> list[Individual]:
    return [
        IndividualFactory(business_area=afghanistan, photo="photo_0.jpg"),
        IndividualFactory(business_area=afghanistan, photo="photo_1.jpg"),
        IndividualFactory(business_area=afghanistan, photo="photo_2.jpg"),
        IndividualFactory(business_area=afghanistan, photo="photo_3.jpg"),
    ]


@pytest.fixture
def partially_uploaded_submit_state(
    four_individuals_with_photos: list[Individual],
    state_key: str,
) -> str:
    state = {
        "run_id": "abc12345",
        "chunk_size": 4,
        "upload_batch_size": 2,
        "business_areas": ["afghanistan"],
        "chunks": [
            {
                "reference_id": "enc-afghanistan-abc12345-00000",
                "business_area": "afghanistan",
                "index": 0,
                "set_id": SET_ID_0,
                "image_count": 2,
                "first_individual_id": None,
                "last_individual_id": None,
                "step": "uploading",
                "uploaded_batches": 1,
                "engine_state": None,
            }
        ],
        "exports": {},
    }
    default_storage.save(state_key, ContentFile(json.dumps(state).encode()))
    return state_key


@pytest.fixture
def fully_processed_submit_state(
    four_individuals_with_photos: list[Individual],
    state_key: str,
) -> str:
    state = {
        "run_id": "abc12345",
        "chunk_size": 4,
        "upload_batch_size": 2,
        "business_areas": ["afghanistan"],
        "chunks": [
            {
                "reference_id": "enc-afghanistan-abc12345-00000",
                "business_area": "afghanistan",
                "index": 0,
                "set_id": SET_ID_0,
                "image_count": 4,
                "first_individual_id": None,
                "last_individual_id": None,
                "step": "processed",
                "uploaded_batches": 2,
                "engine_state": "Processing",
            }
        ],
        "exports": {},
    }
    default_storage.save(state_key, ContentFile(json.dumps(state).encode()))
    return state_key


@pytest.fixture
def submit_state_with_batch_size_1000(afghanistan: BusinessArea, state_key: str) -> str:
    state = {
        "run_id": "abc12345",
        "chunk_size": 10000,
        "upload_batch_size": 1000,
        "business_areas": ["afghanistan"],
        "chunks": [],
        "exports": {},
    }
    default_storage.save(state_key, ContentFile(json.dumps(state).encode()))
    return state_key


@pytest.fixture
def processing_chunk_state(state_key: str) -> str:
    state = {
        "run_id": "abc12345",
        "chunk_size": 10000,
        "upload_batch_size": 5000,
        "business_areas": ["afghanistan"],
        "chunks": [
            {
                "reference_id": "enc-afghanistan-abc12345-00000",
                "business_area": "afghanistan",
                "index": 0,
                "set_id": SET_ID_0,
                "image_count": 1,
                "first_individual_id": None,
                "last_individual_id": None,
                "step": "processed",
                "uploaded_batches": 1,
                "engine_state": "Processing",
            }
        ],
        "exports": {},
    }
    default_storage.save(state_key, ContentFile(json.dumps(state).encode()))
    return state_key


@pytest.fixture
def encoded_chunk_state(state_key: str) -> str:
    state = {
        "run_id": "abc12345",
        "chunk_size": 10000,
        "upload_batch_size": 5000,
        "business_areas": ["afghanistan"],
        "chunks": [
            {
                "reference_id": "enc-afghanistan-abc12345-00000",
                "business_area": "afghanistan",
                "index": 0,
                "set_id": SET_ID_0,
                "image_count": 1,
                "first_individual_id": None,
                "last_individual_id": None,
                "step": "processed",
                "uploaded_batches": 1,
                "engine_state": "Encoded",
            }
        ],
        "exports": {},
    }
    default_storage.save(state_key, ContentFile(json.dumps(state).encode()))
    return state_key


@pytest.fixture
def encoded_two_chunk_state(state_key: str) -> str:
    # Chunks are stored out of index order on purpose: export must sort by index.
    state = {
        "run_id": "abc12345",
        "chunk_size": 2,
        "upload_batch_size": 5000,
        "business_areas": ["afghanistan"],
        "chunks": [
            {
                "reference_id": "enc-afghanistan-abc12345-00001",
                "business_area": "afghanistan",
                "index": 1,
                "set_id": SET_ID_1,
                "image_count": 1,
                "first_individual_id": None,
                "last_individual_id": None,
                "step": "processed",
                "uploaded_batches": 1,
                "engine_state": "Encoded",
            },
            {
                "reference_id": "enc-afghanistan-abc12345-00000",
                "business_area": "afghanistan",
                "index": 0,
                "set_id": SET_ID_0,
                "image_count": 2,
                "first_individual_id": None,
                "last_individual_id": None,
                "step": "processed",
                "uploaded_batches": 1,
                "engine_state": "Encoded",
            },
        ],
        "exports": {},
    }
    default_storage.save(state_key, ContentFile(json.dumps(state).encode()))
    return state_key


@pytest.fixture
def pending_export_state(state_key: str) -> str:
    state = {
        "run_id": "abc12345",
        "chunk_size": 10000,
        "upload_batch_size": 5000,
        "business_areas": ["afghanistan"],
        "chunks": [
            {
                "reference_id": "enc-afghanistan-abc12345-00000",
                "business_area": "afghanistan",
                "index": 0,
                "set_id": SET_ID_0,
                "image_count": 1,
                "first_individual_id": None,
                "last_individual_id": None,
                "step": "processed",
                "uploaded_batches": 1,
                "engine_state": "Encoded",
            }
        ],
        "exports": {
            "afghanistan:npy": {
                "key": PENDING_EXPORT_KEY,
                "format": "npy",
                "state": "pending",
                "requested_at": datetime.now(UTC).isoformat(),
            }
        },
    }
    default_storage.save(state_key, ContentFile(json.dumps(state).encode()))
    return state_key


@pytest.fixture
def ready_export_state(state_key: str) -> str:
    state = {
        "run_id": "abc12345",
        "chunk_size": 10000,
        "upload_batch_size": 5000,
        "business_areas": ["afghanistan"],
        "chunks": [
            {
                "reference_id": "enc-afghanistan-abc12345-00000",
                "business_area": "afghanistan",
                "index": 0,
                "set_id": SET_ID_0,
                "image_count": 1,
                "first_individual_id": None,
                "last_individual_id": None,
                "step": "processed",
                "uploaded_batches": 1,
                "engine_state": "Encoded",
            }
        ],
        "exports": {
            "afghanistan:npy": {
                "key": PENDING_EXPORT_KEY,
                "format": "npy",
                "state": "ready",
                "url": "https://blob/exports/1/afghanistan/a.zip?sig=first",
                "expires_at": "2026-08-13T12:00:00Z",
                "requested_at": datetime.now(UTC).isoformat(),
            }
        },
    }
    default_storage.save(state_key, ContentFile(json.dumps(state).encode()))
    return state_key


@pytest.fixture
def failed_export_state(state_key: str) -> str:
    state = {
        "run_id": "abc12345",
        "chunk_size": 10000,
        "upload_batch_size": 5000,
        "business_areas": ["afghanistan"],
        "chunks": [
            {
                "reference_id": "enc-afghanistan-abc12345-00000",
                "business_area": "afghanistan",
                "index": 0,
                "set_id": SET_ID_0,
                "image_count": 1,
                "first_individual_id": None,
                "last_individual_id": None,
                "step": "processed",
                "uploaded_batches": 1,
                "engine_state": "Encoded",
            }
        ],
        "exports": {
            "afghanistan:npy": {
                "key": None,
                "format": "npy",
                "state": "failed",
                "error": "boom",
                "requested_at": datetime.now(UTC).isoformat(),
            }
        },
    }
    default_storage.save(state_key, ContentFile(json.dumps(state).encode()))
    return state_key


@pytest.fixture
def timed_out_export_state(state_key: str) -> str:
    state = {
        "run_id": "abc12345",
        "chunk_size": 10000,
        "upload_batch_size": 5000,
        "business_areas": ["afghanistan"],
        "chunks": [
            {
                "reference_id": "enc-afghanistan-abc12345-00000",
                "business_area": "afghanistan",
                "index": 0,
                "set_id": SET_ID_0,
                "image_count": 1,
                "first_individual_id": None,
                "last_individual_id": None,
                "step": "processed",
                "uploaded_batches": 1,
                "engine_state": "Encoded",
            }
        ],
        "exports": {
            "afghanistan:npy": {
                "key": PENDING_EXPORT_KEY,
                "format": "npy",
                "state": "pending",
                "requested_at": (datetime.now(UTC) - timedelta(hours=3)).isoformat(),
            }
        },
    }
    default_storage.save(state_key, ContentFile(json.dumps(state).encode()))
    return state_key


@pytest.fixture
def jsonl_ready_export_state(state_key: str) -> str:
    state = {
        "run_id": "abc12345",
        "chunk_size": 10000,
        "upload_batch_size": 5000,
        "business_areas": ["afghanistan"],
        "chunks": [
            {
                "reference_id": "enc-afghanistan-abc12345-00000",
                "business_area": "afghanistan",
                "index": 0,
                "set_id": SET_ID_0,
                "image_count": 1,
                "first_individual_id": None,
                "last_individual_id": None,
                "step": "processed",
                "uploaded_batches": 1,
                "engine_state": "Encoded",
            }
        ],
        "exports": {
            "afghanistan:jsonl": {
                "key": "exports/1/afghanistan/afghanistan-ready.jsonl.zip",
                "format": "jsonl",
                "state": "ready",
                "url": "https://blob/a.jsonl.zip?sig=x",
                "expires_at": "2026-08-13T12:00:00Z",
                "requested_at": datetime.now(UTC).isoformat(),
            }
        },
    }
    default_storage.save(state_key, ContentFile(json.dumps(state).encode()))
    return state_key


def test_submit_chunks_deterministically_and_processes_each_chunk(
    mock_client: mock.MagicMock,
    individuals_for_chunk_submit: list[Individual],
    state_key: str,
) -> None:
    call_command(
        "export_encodings",
        "--mode",
        "submit",
        "--state-file",
        state_key,
        "--business-areas",
        "afghanistan",
        "--dedup-url",
        DEDUP_URL,
        "--dedup-token",
        DEDUP_TOKEN,
        "--chunk-size",
        "2",
    )

    with default_storage.open(state_key, "rb") as handle:
        state = json.load(handle)

    assert state["upload_batch_size"] == 5000
    assert len(state["chunks"]) == 3
    assert state["chunks"][0]["index"] == 0
    assert state["chunks"][1]["index"] == 1
    assert state["chunks"][2]["index"] == 2
    assert state["chunks"][0]["step"] == "processed"
    assert state["chunks"][1]["step"] == "processed"
    assert state["chunks"][2]["step"] == "processed"
    assert state["chunks"][0]["image_count"] == 2
    assert state["chunks"][1]["image_count"] == 2
    assert state["chunks"][2]["image_count"] == 1
    assert state["chunks"][0]["reference_id"] == f"enc-afghanistan-{state['run_id']}-00000"
    assert mock_client.create_set.call_count == 3
    assert mock_client.mark_ready.call_count == 3
    assert mock_client.process.call_count == 3
    mock_client.process.assert_called_with(state["chunks"][2]["set_id"], encode_only=True)


def test_submit_registers_images_in_id_order_with_filename_payload(
    mock_client: mock.MagicMock,
    individuals_for_chunk_submit: list[Individual],
    state_key: str,
) -> None:
    call_command(
        "export_encodings",
        "--mode",
        "submit",
        "--state-file",
        state_key,
        "--business-areas",
        "afghanistan",
        "--dedup-url",
        DEDUP_URL,
        "--dedup-token",
        DEDUP_TOKEN,
        "--chunk-size",
        "2",
    )

    first_batch = mock_client.register_images.call_args_list[0].args[1]
    second_batch = mock_client.register_images.call_args_list[1].args[1]
    third_batch = mock_client.register_images.call_args_list[2].args[1]
    assert first_batch == [
        {
            "reference_pk": str(individuals_for_chunk_submit[0].id),
            "filename": individuals_for_chunk_submit[0].photo.name,
        },
        {
            "reference_pk": str(individuals_for_chunk_submit[1].id),
            "filename": individuals_for_chunk_submit[1].photo.name,
        },
    ]
    assert second_batch == [
        {
            "reference_pk": str(individuals_for_chunk_submit[2].id),
            "filename": individuals_for_chunk_submit[2].photo.name,
        },
        {
            "reference_pk": str(individuals_for_chunk_submit[3].id),
            "filename": individuals_for_chunk_submit[3].photo.name,
        },
    ]
    assert third_batch == [
        {
            "reference_pk": str(individuals_for_chunk_submit[4].id),
            "filename": individuals_for_chunk_submit[4].photo.name,
        },
    ]


def test_submit_resume_skips_already_uploaded_batches(
    mock_client: mock.MagicMock,
    partially_uploaded_submit_state: str,
) -> None:
    call_command(
        "export_encodings",
        "--mode",
        "submit",
        "--state-file",
        partially_uploaded_submit_state,
        "--business-areas",
        "afghanistan",
        "--dedup-url",
        DEDUP_URL,
        "--dedup-token",
        DEDUP_TOKEN,
        "--chunk-size",
        "4",
        "--upload-batch-size",
        "2",
    )

    mock_client.create_set.assert_not_called()
    assert mock_client.register_images.call_count == 1

    with default_storage.open(partially_uploaded_submit_state, "rb") as handle:
        state = json.load(handle)
    assert state["chunks"][0]["step"] == "processed"
    assert state["chunks"][0]["image_count"] == 4


def test_submit_fully_processed_is_noop_on_rerun(
    mock_client: mock.MagicMock,
    fully_processed_submit_state: str,
) -> None:
    call_command(
        "export_encodings",
        "--mode",
        "submit",
        "--state-file",
        fully_processed_submit_state,
        "--business-areas",
        "afghanistan",
        "--dedup-url",
        DEDUP_URL,
        "--dedup-token",
        DEDUP_TOKEN,
        "--chunk-size",
        "4",
        "--upload-batch-size",
        "2",
    )

    mock_client.create_set.assert_not_called()
    mock_client.register_images.assert_not_called()


def test_submit_rejects_conflicting_pinned_parameters(
    mock_client: mock.MagicMock,
    submit_state_with_batch_size_1000: str,
) -> None:
    with pytest.raises(CommandError, match="upload_batch_size"):
        call_command(
            "export_encodings",
            "--mode",
            "submit",
            "--state-file",
            submit_state_with_batch_size_1000,
            "--business-areas",
            "afghanistan",
            "--dedup-url",
            DEDUP_URL,
            "--dedup-token",
            DEDUP_TOKEN,
            "--upload-batch-size",
            "2000",
        )


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
            "--dedup-url",
            DEDUP_URL,
            "--dedup-token",
            DEDUP_TOKEN,
        )


def test_status_updates_engine_state(
    mock_client: mock.MagicMock,
    processing_chunk_state: str,
) -> None:
    mock_client.get_set.return_value = {"state": "Encoding"}

    call_command(
        "export_encodings",
        "--mode",
        "status",
        "--state-file",
        processing_chunk_state,
        "--dedup-url",
        DEDUP_URL,
        "--dedup-token",
        DEDUP_TOKEN,
    )

    mock_client.get_set.assert_called_once_with(SET_ID_0)
    with default_storage.open(processing_chunk_state, "rb") as handle:
        state = json.load(handle)
    assert state["chunks"][0]["engine_state"] == "Encoding"


def test_export_requests_export_when_all_chunks_encoded(
    mock_client: mock.MagicMock,
    encoded_two_chunk_state: str,
) -> None:
    call_command(
        "export_encodings",
        "--mode",
        "export",
        "--state-file",
        encoded_two_chunk_state,
        "--dedup-url",
        DEDUP_URL,
        "--dedup-token",
        DEDUP_TOKEN,
    )

    with default_storage.open(encoded_two_chunk_state, "rb") as handle:
        state = json.load(handle)

    export_entry = state["exports"]["afghanistan:npy"]
    assert export_entry["state"] == "pending"
    assert export_entry["key"].startswith("exports/1/afghanistan/")
    assert export_entry["format"] == "npy"
    assert export_entry["requested_at"]
    # Sets are passed in chunk-index order even though the state file stores them reversed.
    mock_client.create_export.assert_called_once_with(
        reference_pk="afghanistan",
        set_ids=[SET_ID_0, SET_ID_1],
        export_format="npy",
    )


def test_export_format_flag_is_passed_and_recorded(
    mock_client: mock.MagicMock,
    encoded_chunk_state: str,
) -> None:
    call_command(
        "export_encodings",
        "--mode",
        "export",
        "--state-file",
        encoded_chunk_state,
        "--dedup-url",
        DEDUP_URL,
        "--dedup-token",
        DEDUP_TOKEN,
        "--export-format",
        "jsonl",
    )

    with default_storage.open(encoded_chunk_state, "rb") as handle:
        state = json.load(handle)

    export_entry = state["exports"]["afghanistan:jsonl"]
    assert export_entry["format"] == "jsonl"
    assert ".jsonl.zip" in export_entry["key"]
    assert mock_client.create_export.call_args.kwargs["export_format"] == "jsonl"


def test_both_export_formats_coexist_for_one_co(
    mock_client: mock.MagicMock,
    jsonl_ready_export_state: str,
) -> None:
    call_command(
        "export_encodings",
        "--mode",
        "export",
        "--state-file",
        jsonl_ready_export_state,
        "--dedup-url",
        DEDUP_URL,
        "--dedup-token",
        DEDUP_TOKEN,
        "--export-format",
        "npy",
    )

    with default_storage.open(jsonl_ready_export_state, "rb") as handle:
        state = json.load(handle)

    assert state["exports"]["afghanistan:npy"]["state"] == "pending"
    assert ".npy.zip" in state["exports"]["afghanistan:npy"]["key"]
    mock_client.create_export.assert_called_once()
    # The ready jsonl entry was untouched by the npy request.
    assert state["exports"]["afghanistan:jsonl"]["state"] == "ready"
    assert state["exports"]["afghanistan:jsonl"]["url"].endswith("sig=x")


def test_export_skips_co_with_unencoded_chunks(
    mock_client: mock.MagicMock,
    processing_chunk_state: str,
) -> None:
    mock_client.get_set.return_value = {"state": "Encoding"}

    call_command(
        "export_encodings",
        "--mode",
        "export",
        "--state-file",
        processing_chunk_state,
        "--dedup-url",
        DEDUP_URL,
        "--dedup-token",
        DEDUP_TOKEN,
    )

    mock_client.create_export.assert_not_called()
    with default_storage.open(processing_chunk_state, "rb") as handle:
        state = json.load(handle)
    assert state["exports"] == {}


def test_export_poll_stores_signed_url(
    mock_client: mock.MagicMock,
    pending_export_state: str,
) -> None:
    mock_client.export_status.return_value = {
        "state": "ready",
        "url": "https://blob/exports/1/afghanistan/a.zip?sig=first",
        "expires_at": "2026-08-13T12:00:00Z",
    }

    call_command(
        "export_encodings",
        "--mode",
        "export",
        "--state-file",
        pending_export_state,
        "--dedup-url",
        DEDUP_URL,
        "--dedup-token",
        DEDUP_TOKEN,
    )

    mock_client.export_status.assert_called_once_with(PENDING_EXPORT_KEY)
    with default_storage.open(pending_export_state, "rb") as handle:
        state = json.load(handle)
    export_entry = state["exports"]["afghanistan:npy"]
    assert export_entry["state"] == "ready"
    assert export_entry["url"].endswith("sig=first")
    assert export_entry["expires_at"] == "2026-08-13T12:00:00Z"


def test_export_renews_signed_url_on_repoll(
    mock_client: mock.MagicMock,
    ready_export_state: str,
) -> None:
    mock_client.export_status.return_value = {
        "state": "ready",
        "url": "https://blob/exports/1/afghanistan/a.zip?sig=renewed",
        "expires_at": "2026-08-20T12:00:00Z",
    }

    call_command(
        "export_encodings",
        "--mode",
        "export",
        "--state-file",
        ready_export_state,
        "--dedup-url",
        DEDUP_URL,
        "--dedup-token",
        DEDUP_TOKEN,
    )

    mock_client.create_export.assert_not_called()
    with default_storage.open(ready_export_state, "rb") as handle:
        state = json.load(handle)
    assert state["exports"]["afghanistan:npy"]["url"].endswith("sig=renewed")
    assert state["exports"]["afghanistan:npy"]["expires_at"] == "2026-08-20T12:00:00Z"


def test_export_failed_clears_key(
    mock_client: mock.MagicMock,
    pending_export_state: str,
) -> None:
    mock_client.export_status.return_value = {"state": "failed", "error": "boom"}

    call_command(
        "export_encodings",
        "--mode",
        "export",
        "--state-file",
        pending_export_state,
        "--dedup-url",
        DEDUP_URL,
        "--dedup-token",
        DEDUP_TOKEN,
    )

    with default_storage.open(pending_export_state, "rb") as handle:
        state = json.load(handle)
    export_entry = state["exports"]["afghanistan:npy"]
    assert export_entry["state"] == "failed"
    assert export_entry["key"] is None
    assert export_entry["error"] == "boom"


def test_export_rerequests_after_failed(
    mock_client: mock.MagicMock,
    failed_export_state: str,
) -> None:
    call_command(
        "export_encodings",
        "--mode",
        "export",
        "--state-file",
        failed_export_state,
        "--dedup-url",
        DEDUP_URL,
        "--dedup-token",
        DEDUP_TOKEN,
    )

    mock_client.create_export.assert_called_once()
    with default_storage.open(failed_export_state, "rb") as handle:
        state = json.load(handle)
    assert state["exports"]["afghanistan:npy"]["state"] == "pending"
    assert state["exports"]["afghanistan:npy"]["key"]


def test_export_reposts_after_pending_timeout(
    mock_client: mock.MagicMock,
    timed_out_export_state: str,
) -> None:
    call_command(
        "export_encodings",
        "--mode",
        "export",
        "--state-file",
        timed_out_export_state,
        "--dedup-url",
        DEDUP_URL,
        "--dedup-token",
        DEDUP_TOKEN,
    )

    mock_client.create_export.assert_called_once()
    with default_storage.open(timed_out_export_state, "rb") as handle:
        state = json.load(handle)
    assert state["exports"]["afghanistan:npy"]["key"] != PENDING_EXPORT_KEY
    assert state["exports"]["afghanistan:npy"]["state"] == "pending"


def test_export_still_pending_within_timeout_does_not_repost(
    mock_client: mock.MagicMock,
    pending_export_state: str,
) -> None:
    call_command(
        "export_encodings",
        "--mode",
        "export",
        "--state-file",
        pending_export_state,
        "--dedup-url",
        DEDUP_URL,
        "--dedup-token",
        DEDUP_TOKEN,
    )

    mock_client.create_export.assert_not_called()
    with default_storage.open(pending_export_state, "rb") as handle:
        state = json.load(handle)
    assert state["exports"]["afghanistan:npy"]["key"] == PENDING_EXPORT_KEY


def test_status_requires_submitted_state(mock_client: mock.MagicMock, state_key: str) -> None:
    with pytest.raises(CommandError, match="submit"):
        call_command(
            "export_encodings",
            "--mode",
            "status",
            "--state-file",
            state_key,
            "--dedup-url",
            DEDUP_URL,
            "--dedup-token",
            DEDUP_TOKEN,
        )


def test_export_requires_submitted_state(mock_client: mock.MagicMock, state_key: str) -> None:
    with pytest.raises(CommandError, match="submit"):
        call_command(
            "export_encodings",
            "--mode",
            "export",
            "--state-file",
            state_key,
            "--dedup-url",
            DEDUP_URL,
            "--dedup-token",
            DEDUP_TOKEN,
        )


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


def test_dedup_engine_client_requests_url_without_double_slash() -> None:
    client = DedupEngineClient(base_url="https://dedup.test/", token=DEDUP_TOKEN)

    with mock.patch.object(client.session, "request", return_value=mock.MagicMock(status_code=200)) as request:
        client._request("GET", "deduplication_sets/")

    request.assert_called_once_with("GET", "https://dedup.test/deduplication_sets/", timeout=300)
