import base64
import gzip
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
        client.get_encodings_page.return_value = {"results": [], "next": None}
        yield client


@pytest.fixture
def afghanistan() -> object:
    return BusinessAreaFactory(slug="afghanistan", name="Afghanistan")


@pytest.fixture
def state_key() -> str:
    return f"export-encodings-tests/{uuid.uuid4().hex}/state.json"


@pytest.fixture
def output_prefix() -> str:
    return f"export-encodings-tests/{uuid.uuid4().hex}/out"


def read_state(state_key: str) -> dict:
    with default_storage.open(state_key, "rb") as f:
        return json.load(f)


def write_state(state_key: str, state: dict) -> None:
    if default_storage.exists(state_key):
        default_storage.delete(state_key)
    default_storage.save(state_key, ContentFile(json.dumps(state).encode()))


def read_gzip_lines(name: str) -> list[dict]:
    with default_storage.open(name, "rb") as f, gzip.GzipFile(fileobj=f) as gz:
        return [json.loads(line) for line in gz]


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


def collect(state_key: str, output_prefix: str) -> None:
    call_command(
        "export_encodings",
        "--mode",
        "collect",
        "--state-file",
        state_key,
        "--output-dir",
        output_prefix,
        *COMMON_ARGS,
    )


def test_submit_chunks_deterministically_and_processes_each_chunk(
    mock_client: mock.MagicMock, afghanistan: object, state_key: str
) -> None:
    individuals = [IndividualFactory(business_area=afghanistan, photo=f"photo_{i}.jpg") for i in range(5)]
    # Excluded individuals must not be submitted.
    IndividualFactory(business_area=afghanistan, photo="")
    IndividualFactory(business_area=afghanistan, photo="w.jpg", withdrawn=True)
    IndividualFactory(business_area=afghanistan, photo="d.jpg", duplicate=True)

    submit(state_key, ["--chunk-size", "2", "--image-transfer", "filename"])

    state = read_state(state_key)
    assert state["image_transfer"] == "filename"
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

    # Chunk membership is deterministic: ordered by individual id.
    uploaded_pks = [
        item["reference_pk"] for call_args in mock_client.register_images.call_args_list for item in call_args.args[1]
    ]
    assert uploaded_pks == sorted(str(individual.id) for individual in individuals)


def test_submit_base64_sends_image_content_and_records_missing_files(
    mock_client: mock.MagicMock, afghanistan: object, state_key: str
) -> None:
    with_file = IndividualFactory(business_area=afghanistan, photo=ContentFile(b"image-bytes", name="ok.png"))
    without_file = IndividualFactory(business_area=afghanistan, photo="does_not_exist.jpg")

    submit(state_key, ["--image-transfer", "base64"])

    items = [item for call_args in mock_client.register_images.call_args_list for item in call_args.args[1]]
    assert len(items) == 1
    assert items[0]["reference_pk"] == str(with_file.id)
    assert base64.b64decode(items[0]["image"]) == b"image-bytes"

    state = read_state(state_key)
    assert state["chunks"][0]["missing_files"] == [str(without_file.id)]
    assert state["chunks"][0]["image_count"] == 1


def test_submit_resume_skips_already_uploaded_batches_and_processed_chunks(
    mock_client: mock.MagicMock, afghanistan: object, state_key: str
) -> None:
    for i in range(4):
        IndividualFactory(business_area=afghanistan, photo=f"photo_{i}.jpg")

    submit(state_key, ["--chunk-size", "4", "--image-transfer", "filename", "--upload-batch-size", "2"])
    assert mock_client.register_images.call_count == 2

    # Simulate a crash after the first of two batches was uploaded.
    state = read_state(state_key)
    state["chunks"][0]["step"] = "uploading"
    state["chunks"][0]["uploaded_batches"] = 1
    state["chunks"][0]["image_count"] = 2
    write_state(state_key, state)
    mock_client.register_images.reset_mock()
    mock_client.create_set.reset_mock()

    submit(state_key, ["--chunk-size", "4", "--image-transfer", "filename", "--upload-batch-size", "2"])

    mock_client.create_set.assert_not_called()  # set already exists
    assert mock_client.register_images.call_count == 1  # only the second batch
    state = read_state(state_key)
    assert state["chunks"][0]["step"] == "processed"
    assert state["chunks"][0]["image_count"] == 4

    # A fully processed state file is a no-op on re-run.
    mock_client.register_images.reset_mock()
    submit(state_key, ["--chunk-size", "4", "--image-transfer", "filename", "--upload-batch-size", "2"])
    mock_client.register_images.assert_not_called()


def test_submit_rejects_conflicting_pinned_parameters(
    mock_client: mock.MagicMock, afghanistan: object, state_key: str
) -> None:
    IndividualFactory(business_area=afghanistan, photo="photo.jpg")
    submit(state_key, ["--image-transfer", "filename"])

    with pytest.raises(CommandError, match="image_transfer"):
        submit(state_key, ["--image-transfer", "base64"])


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
    submit(state_key, ["--image-transfer", "filename"])

    mock_client.get_set.return_value = {"state": "Encoding"}
    call_command("export_encodings", "--mode", "status", "--state-file", state_key, *COMMON_ARGS)

    state = read_state(state_key)
    assert state["chunks"][0]["engine_state"] == "Encoding"


def test_collect_writes_embeddings_file_and_manifest(
    mock_client: mock.MagicMock, afghanistan: object, state_key: str, output_prefix: str
) -> None:
    individual = IndividualFactory(business_area=afghanistan, photo="photo.jpg")
    submit(state_key, ["--image-transfer", "filename"])

    mock_client.get_set.return_value = {"state": "Encoded"}
    mock_client.get_encodings_page.return_value = {
        "results": [
            {
                "reference_pk": str(individual.id),
                "filename": "photo.jpg",
                "embedding": [0.1, 0.2],
                "status_code": 200,
                "model_version": "model-v1",
            },
            {
                "reference_pk": str(uuid.uuid4()),
                "filename": "other.jpg",
                "embedding": None,
                "status_code": 412,
                "model_version": "model-v1",
            },
        ],
        "next": None,
    }

    collect(state_key, output_prefix)

    state = read_state(state_key)
    chunk = state["chunks"][0]
    assert chunk["collected"] is True
    assert chunk["status_counts"] == {"200": 1, "412": 1}
    assert chunk["model_version"] == "model-v1"

    lines = read_gzip_lines(f"{output_prefix}/{chunk['embeddings_file']}")
    assert lines[0]["individual_id"] == str(individual.id)
    assert lines[0]["embedding"] == [0.1, 0.2]
    assert lines[1]["status_code"] == 412
    assert lines[1]["embedding"] is None

    with default_storage.open(f"{output_prefix}/manifest.json", "rb") as f:
        manifest = json.load(f)
    assert manifest["run_id"] == state["run_id"]
    assert manifest["model_versions"] == ["model-v1"]
    assert manifest["status_counts"] == {"200": 1, "412": 1}
    assert manifest["files"][0]["name"] == chunk["embeddings_file"]
    assert manifest["failed_chunks"] == []

    # Collect is idempotent: a second run does not refetch collected chunks.
    mock_client.get_encodings_page.reset_mock()
    collect(state_key, output_prefix)
    mock_client.get_encodings_page.assert_not_called()


def test_collect_skips_sets_that_are_not_encoded_yet_and_defers_manifest(
    mock_client: mock.MagicMock, afghanistan: object, state_key: str, output_prefix: str
) -> None:
    IndividualFactory(business_area=afghanistan, photo="photo.jpg")
    submit(state_key, ["--image-transfer", "filename"])

    mock_client.get_set.return_value = {"state": "Encoding"}
    collect(state_key, output_prefix)

    mock_client.get_encodings_page.assert_not_called()
    assert not default_storage.exists(f"{output_prefix}/manifest.json")
    state = read_state(state_key)
    assert state["chunks"][0]["collected"] is False


def test_collect_paginates_through_all_encoding_pages(
    mock_client: mock.MagicMock, afghanistan: object, state_key: str, output_prefix: str
) -> None:
    IndividualFactory(business_area=afghanistan, photo="photo.jpg")
    submit(state_key, ["--image-transfer", "filename"])

    def make_item() -> dict:
        return {
            "reference_pk": str(uuid.uuid4()),
            "filename": "x.jpg",
            "embedding": [0.5],
            "status_code": 200,
            "model_version": "model-v1",
        }

    mock_client.get_encodings_page.side_effect = [
        {"results": [make_item(), make_item()], "next": "http://next"},
        {"results": [make_item()], "next": None},
    ]

    collect(state_key, output_prefix)

    assert mock_client.get_encodings_page.call_count == 2
    state = read_state(state_key)
    assert len(read_gzip_lines(f"{output_prefix}/{state['chunks'][0]['embeddings_file']}")) == 3


def test_status_and_collect_require_submitted_state(mock_client: mock.MagicMock, state_key: str) -> None:
    with pytest.raises(CommandError, match="submit"):
        call_command("export_encodings", "--mode", "status", "--state-file", state_key, *COMMON_ARGS)


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
