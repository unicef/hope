"""One-shot tool to encode CO images via the Deduplication Engine and collect embeddings.

Splits individuals of the given business areas into deterministic chunks, submits each
chunk as its own deduplication set group (so engine workers process chunks in parallel),
runs encode-only processing, and later collects the embeddings into shareable
``.jsonl.gz`` files plus a ``manifest.json``.

All progress is tracked in a JSON state file, so every mode is idempotent and safe to
re-run after a crash or interruption.

Usage:

    manage.py export_encodings --mode submit --state-file run1.json \
        --business-areas afghanistan,ukraine --dedup-url https://... --dedup-token ...

    manage.py export_encodings --mode status --state-file run1.json ...

    manage.py export_encodings --mode collect --state-file run1.json --output-dir out/ ...
"""

from argparse import ArgumentParser
import base64
import gzip
import hashlib
import io
import json
import os
import time
from typing import Any
import uuid

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q, QuerySet
import requests

from hope.models import BusinessArea, Individual

DEFAULT_UPLOAD_BATCH_SIZES = {"base64": 200, "filename": 5000}
ENCODINGS_PAGE_SIZE = 1000
# Engine set states in which embeddings are retrievable.
COLLECTIBLE_STATES = {"Encoded", "Deduplicated", "Approved"}
FAILED_STATES = {"Encoding failed", "Deduplication failed", "Failed"}


class DedupEngineClient:
    """Minimal client for the Deduplication Engine REST API (token auth)."""

    MAX_ATTEMPTS = 3
    BACKOFF_SECONDS = 5

    class DedupEngineError(Exception):
        pass

    def __init__(self, base_url: str, token: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers["Authorization"] = f"Token {token}"

    def _request(self, method: str, path: str, **kwargs: Any) -> requests.Response:
        url = f"{self.base_url}/{path}"
        last_error: Exception | None = None
        for attempt in range(1, self.MAX_ATTEMPTS + 1):
            try:
                response = self.session.request(method, url, timeout=300, **kwargs)
            except requests.RequestException as exc:
                last_error = exc
            else:
                if response.status_code < 500:
                    if response.status_code >= 400:
                        raise self.DedupEngineError(
                            f"{method} {url} failed with {response.status_code}: {response.text[:1000]}"
                        )
                    return response
                last_error = self.DedupEngineError(
                    f"{method} {url} failed with {response.status_code}: {response.text[:1000]}"
                )
            if attempt < self.MAX_ATTEMPTS:
                time.sleep(self.BACKOFF_SECONDS * attempt)
        raise self.DedupEngineError(f"{method} {url} failed after {self.MAX_ATTEMPTS} attempts") from last_error

    def create_set(self, reference_pk: str, name: str) -> dict:
        response = self._request(
            "POST",
            "deduplication_sets/",
            json={"reference_pk": reference_pk, "name": name, "notify": False},
        )
        return response.json()

    def register_images(self, set_id: str, items: list[dict]) -> None:
        self._request("POST", f"deduplication_sets/{set_id}/images/", json=items)

    def mark_ready(self, set_id: str) -> None:
        self._request("POST", f"deduplication_sets/{set_id}/ready/")

    def process(self, set_id: str, encode_only: bool = True) -> None:
        params = {"encode_only": "true"} if encode_only else {}
        self._request("POST", f"deduplication_sets/{set_id}/process/", params=params)

    def get_set(self, set_id: str) -> dict:
        return self._request("GET", f"deduplication_sets/{set_id}/").json()

    def get_encodings_page(self, set_id: str, page: int, page_size: int) -> dict:
        response = self._request(
            "GET",
            f"deduplication_sets/{set_id}/encodings/",
            params={"page": page, "page_size": page_size},
        )
        return response.json()


class Command(BaseCommand):
    help = "Encode CO images via the Deduplication Engine (encode_only) and collect embeddings for sharing."

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("--mode", required=True, choices=["submit", "status", "collect"])
        parser.add_argument(
            "--state-file",
            required=True,
            help="Default-storage key of the JSON state file for this run (survives pod restarts).",
        )
        parser.add_argument(
            "--business-areas",
            help="Comma-separated business area slugs to encode (required for submit).",
        )
        parser.add_argument("--dedup-url", default=os.environ.get("DEDUPLICATION_ENGINE_API_URL"))
        parser.add_argument("--dedup-token", default=os.environ.get("DEDUPLICATION_ENGINE_API_KEY"))
        parser.add_argument("--chunk-size", type=int, default=10000)
        parser.add_argument(
            "--image-transfer",
            choices=["base64", "filename"],
            default="base64",
            help="base64: image content in the payload (current engine). "
            "filename: storage path only (requires the shared-blob-storage engine build).",
        )
        parser.add_argument(
            "--upload-batch-size",
            type=int,
            default=None,
            help="Images per registration request. Defaults: 200 (base64) / 5000 (filename).",
        )
        parser.add_argument(
            "--output-dir",
            help="Default-storage prefix for embedding files and manifest (required for collect).",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        if not options["dedup_url"] or not options["dedup_token"]:
            raise CommandError(
                "Deduplication engine URL/token missing: pass --dedup-url/--dedup-token or set "
                "DEDUPLICATION_ENGINE_API_URL/DEDUPLICATION_ENGINE_API_KEY."
            )
        self.client = DedupEngineClient(options["dedup_url"], options["dedup_token"])
        self.state_key = options["state_file"]
        self.state = self._load_state()

        mode = options["mode"]
        if mode == "submit":
            self._run_submit(options)
        elif mode == "status":
            self._run_status()
        else:
            self._run_collect(options)

    # ----- state file (kept in Django default storage so it survives pod restarts) -----

    def _load_state(self) -> dict:
        if default_storage.exists(self.state_key):
            with default_storage.open(self.state_key, "rb") as f:
                return json.load(f)
        return {}

    def _save_state(self) -> None:
        self._save_to_storage(self.state_key, json.dumps(self.state, indent=2).encode())

    @staticmethod
    def _save_to_storage(name: str, data: bytes) -> None:
        # Storage.save() mangles existing names instead of overwriting, so delete first.
        if default_storage.exists(name):
            default_storage.delete(name)
        default_storage.save(name, ContentFile(data))

    # ----- submit -----

    def _individuals_queryset(self, business_area_slug: str) -> QuerySet[Individual]:
        return (
            Individual.all_objects.filter(is_removed=False, business_area__slug=business_area_slug)
            .exclude(Q(photo="") | Q(withdrawn=True) | Q(duplicate=True))
            .order_by("id")
            .only("id", "photo")
        )

    def _run_submit(self, options: dict) -> None:
        if not options["business_areas"]:
            raise CommandError("--business-areas is required for submit mode.")
        slugs = [slug.strip() for slug in options["business_areas"].split(",") if slug.strip()]
        existing = set(BusinessArea.objects.filter(slug__in=slugs).values_list("slug", flat=True))
        if missing := set(slugs) - existing:
            raise CommandError(f"Unknown business area slug(s): {', '.join(sorted(missing))}")

        upload_batch_size = options["upload_batch_size"] or DEFAULT_UPLOAD_BATCH_SIZES[options["image_transfer"]]
        if not self.state:
            self.state = {
                "run_id": uuid.uuid4().hex[:8],
                "chunk_size": options["chunk_size"],
                "image_transfer": options["image_transfer"],
                "upload_batch_size": upload_batch_size,
                "business_areas": slugs,
                "chunks": [],
            }
            self._save_state()
        else:
            # Resume: pinned parameters must match, otherwise batch-offset resume would corrupt uploads.
            for key, value in (
                ("chunk_size", options["chunk_size"]),
                ("image_transfer", options["image_transfer"]),
                ("upload_batch_size", upload_batch_size),
            ):
                if self.state[key] != value:
                    raise CommandError(
                        f"State file was created with {key}={self.state[key]}, but current value is {value}. "
                        "Re-run with matching parameters or use a new state file."
                    )
            if set(self.state["business_areas"]) != set(slugs):
                raise CommandError(
                    f"State file was created for business areas {self.state['business_areas']}; "
                    "use a new state file for a different selection."
                )

        chunk_size = self.state["chunk_size"]
        chunks_by_reference = {chunk["reference_id"]: chunk for chunk in self.state["chunks"]}

        for slug in self.state["business_areas"]:
            queryset = self._individuals_queryset(slug)
            total = queryset.count()
            self.stdout.write(f"{slug}: {total} individuals with photos")
            for index in range((total + chunk_size - 1) // chunk_size):
                reference_id = f"enc-{slug}-{self.state['run_id']}-{index:05d}"
                chunk = chunks_by_reference.get(reference_id)
                if chunk is None:
                    chunk = {
                        "reference_id": reference_id,
                        "business_area": slug,
                        "index": index,
                        "set_id": None,
                        "image_count": 0,
                        "first_individual_id": None,
                        "last_individual_id": None,
                        "step": "pending",
                        "uploaded_batches": 0,
                        "missing_files": [],
                        "engine_state": None,
                        "collected": False,
                        "status_counts": {},
                    }
                    self.state["chunks"].append(chunk)
                    chunks_by_reference[reference_id] = chunk
                if chunk["step"] == "processed":
                    continue
                individuals = list(queryset[index * chunk_size : (index + 1) * chunk_size])
                self._submit_chunk(chunk, individuals)

        self._print_summary()

    def _submit_chunk(self, chunk: dict, individuals: list[Individual]) -> None:
        reference_id = chunk["reference_id"]
        if not individuals:
            chunk["step"] = "processed"
            self._save_state()
            return

        chunk["first_individual_id"] = str(individuals[0].id)
        chunk["last_individual_id"] = str(individuals[-1].id)

        if chunk["set_id"] is None:
            response = self.client.create_set(reference_pk=reference_id, name=reference_id)
            chunk["set_id"] = response["id"]
            chunk["step"] = "created"
            self._save_state()

        batch_size = self.state["upload_batch_size"]
        if chunk["step"] in ("created", "uploading"):
            chunk["step"] = "uploading"
            batches = [individuals[i : i + batch_size] for i in range(0, len(individuals), batch_size)]
            for batch_index, batch in enumerate(batches):
                if batch_index < chunk["uploaded_batches"]:
                    continue
                items, missing = self._build_image_items(batch)
                if items:
                    self.client.register_images(chunk["set_id"], items)
                chunk["image_count"] += len(items)
                chunk["missing_files"].extend(missing)
                chunk["uploaded_batches"] = batch_index + 1
                self._save_state()
            chunk["step"] = "uploaded"
            self._save_state()

        if chunk["step"] == "uploaded":
            self.client.mark_ready(chunk["set_id"])
            chunk["step"] = "ready"
            self._save_state()

        if chunk["step"] == "ready":
            self.client.process(chunk["set_id"], encode_only=True)
            chunk["step"] = "processed"
            chunk["engine_state"] = "Processing"
            self._save_state()

        self.stdout.write(f"  {reference_id}: submitted {chunk['image_count']} images (set {chunk['set_id']})")

    def _build_image_items(self, individuals: list[Individual]) -> tuple[list[dict], list[str]]:
        items = []
        missing = []
        use_base64 = self.state["image_transfer"] == "base64"
        for individual in individuals:
            item = {"reference_pk": str(individual.id), "filename": individual.photo.name}
            if use_base64:
                try:
                    with individual.photo.open("rb") as f:
                        item["image"] = base64.b64encode(f.read()).decode("ascii")
                except OSError:
                    missing.append(str(individual.id))
                    continue
            items.append(item)
        return items, missing

    # ----- status -----

    def _run_status(self) -> None:
        self._require_chunks()
        for chunk in self.state["chunks"]:
            if chunk["set_id"] and not chunk["collected"]:
                chunk["engine_state"] = self.client.get_set(chunk["set_id"])["state"]
        self._save_state()
        self._print_summary()

    # ----- collect -----

    def _run_collect(self, options: dict) -> None:
        self._require_chunks()
        if not options["output_dir"]:
            raise CommandError("--output-dir is required for collect mode.")
        output_prefix = options["output_dir"].rstrip("/")

        for chunk in self.state["chunks"]:
            if chunk["collected"] or not chunk["set_id"]:
                continue
            chunk["engine_state"] = self.client.get_set(chunk["set_id"])["state"]
            self._save_state()
            if chunk["engine_state"] not in COLLECTIBLE_STATES:
                continue
            self._collect_chunk(chunk, output_prefix)

        self._print_summary()
        self._maybe_write_manifest(output_prefix)

    def _collect_chunk(self, chunk: dict, output_prefix: str) -> None:
        file_name = f"{chunk['reference_id']}.jsonl.gz"
        status_counts: dict[str, int] = {}
        digest = hashlib.sha256()
        lines_written = 0
        model_version = None

        buffer = io.BytesIO()
        with gzip.GzipFile(fileobj=buffer, mode="wb") as out:
            page = 1
            while True:
                data = self.client.get_encodings_page(chunk["set_id"], page, ENCODINGS_PAGE_SIZE)
                for item in data["results"]:
                    model_version = item.get("model_version") or model_version
                    status_code = str(item.get("status_code", ""))
                    status_counts[status_code] = status_counts.get(status_code, 0) + 1
                    line = json.dumps(
                        {
                            "individual_id": item["reference_pk"],
                            "filename": item.get("filename"),
                            "embedding": item.get("embedding"),
                            "status_code": item.get("status_code"),
                            "model_version": item.get("model_version"),
                        }
                    )
                    out.write(line.encode() + b"\n")
                    digest.update(line.encode())
                    lines_written += 1
                if not data.get("next"):
                    break
                page += 1

        # The file lands in storage atomically only after all pages were fetched.
        self._save_to_storage(f"{output_prefix}/{file_name}", buffer.getvalue())
        chunk["collected"] = True
        chunk["status_counts"] = status_counts
        chunk["embeddings_file"] = file_name
        chunk["embeddings_sha256"] = digest.hexdigest()
        chunk["model_version"] = model_version
        self._save_state()
        self.stdout.write(
            f"  {chunk['reference_id']}: collected {lines_written} encodings -> {output_prefix}/{file_name}"
        )

    def _maybe_write_manifest(self, output_prefix: str) -> None:
        chunks = self.state["chunks"]
        pending = [
            chunk for chunk in chunks if not chunk["collected"] and (chunk["engine_state"] or "") not in FAILED_STATES
        ]
        if pending:
            self.stdout.write(f"{len(pending)} chunk(s) not yet collected; manifest not written. Re-run later.")
            return

        totals: dict[str, int] = {}
        for chunk in chunks:
            for code, count in chunk["status_counts"].items():
                totals[code] = totals.get(code, 0) + count
        manifest = {
            "run_id": self.state["run_id"],
            "business_areas": self.state["business_areas"],
            "chunk_size": self.state["chunk_size"],
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "model_versions": sorted({c["model_version"] for c in chunks if c.get("model_version")}),
            "total_images": sum(chunk["image_count"] for chunk in chunks),
            "status_counts": totals,
            "missing_files_count": sum(len(chunk["missing_files"]) for chunk in chunks),
            "files": [
                {
                    "name": chunk["embeddings_file"],
                    "sha256": chunk["embeddings_sha256"],
                    "business_area": chunk["business_area"],
                    "reference_id": chunk["reference_id"],
                    "status_counts": chunk["status_counts"],
                }
                for chunk in chunks
                if chunk["collected"]
            ],
            "failed_chunks": [chunk["reference_id"] for chunk in chunks if not chunk["collected"]],
        }
        manifest_key = f"{output_prefix}/manifest.json"
        self._save_to_storage(manifest_key, json.dumps(manifest, indent=2).encode())
        self.stdout.write(self.style.SUCCESS(f"Manifest written to {manifest_key}"))

    # ----- helpers -----

    def _require_chunks(self) -> None:
        if not self.state.get("chunks"):
            raise CommandError("State file has no submitted chunks; run submit mode first.")

    def _print_summary(self) -> None:
        by_area: dict[str, dict[str, int]] = {}
        for chunk in self.state.get("chunks", []):
            area_stats = by_area.setdefault(chunk["business_area"], {})
            if chunk["collected"]:
                status = "collected"
            elif chunk["step"] != "processed":
                status = f"submit:{chunk['step']}"
            else:
                status = chunk["engine_state"] or "unknown"
            area_stats[status] = area_stats.get(status, 0) + 1
        self.stdout.write("Summary:")
        for area, stats in sorted(by_area.items()):
            parts = ", ".join(f"{status}={count}" for status, count in sorted(stats.items()))
            self.stdout.write(f"  {area}: {parts}")
