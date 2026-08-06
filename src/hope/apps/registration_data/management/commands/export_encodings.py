"""One-shot tool to encode CO images via the Deduplication Engine and export the embeddings.

Splits individuals of the given business areas into deterministic chunks, submits each
chunk as its own deduplication set group (so engine workers process chunks in parallel)
and runs encode-only processing. Once all chunks of a CO are encoded, the export mode
asks the engine to zip that CO's embeddings onto its dedicated Azure storage and stores
the resulting signed URL — the shareable deliverable — in the state file.

All progress is tracked in a JSON state file kept in Django default storage, so every
mode is idempotent and safe to re-run after a crash, interruption, or pod restart.

Export mode: POST /encodings_exports/ when the state file has no key for that CO+format;
GET /encodings_exports/status/?key=… when a key is already stored (poll / renew URL).

Full usage instructions: docs/guide-dev/export-encodings.md

Usage:

    manage.py export_encodings --mode submit --state-file encodings/run1.json \
        --business-areas afghanistan,ukraine --dedup-url https://... --dedup-token ...

    manage.py export_encodings --mode status --state-file encodings/run1.json \
        --dedup-url https://... --dedup-token ...

    manage.py export_encodings --mode export --state-file encodings/run1.json \
        --dedup-url https://... --dedup-token ...
"""

from argparse import ArgumentParser
from datetime import UTC, datetime
import json
import time
from typing import Any
import uuid

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q, QuerySet
import requests

from hope.models import BusinessArea, Individual

DEFAULT_UPLOAD_BATCH_SIZE = 5000
# Engine set states in which embeddings exist and the set can be exported.
EXPORTABLE_STATES = {"Encoded", "Deduplicated", "Approved"}
FAILED_STATES = {"Encoding failed", "Deduplication failed", "Failed"}
# A pending export older than this is assumed dead (task crashed before writing
# its error blob) and is re-requested under a fresh key.
EXPORT_PENDING_TIMEOUT_SECONDS = 2 * 60 * 60


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

    def create_export(self, reference_pk: str, set_ids: list[str], export_format: str) -> dict:
        response = self._request(
            "POST",
            "encodings_exports/",
            json={"reference_pk": reference_pk, "deduplication_set_ids": set_ids, "format": export_format},
        )
        return response.json()

    def export_status(self, key: str) -> dict:
        return self._request("GET", "encodings_exports/status/", params={"key": key}).json()


class Command(BaseCommand):
    help = "Encode CO images via the Deduplication Engine (encode_only) and export embeddings as signed zip URLs."

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("--mode", required=True, choices=["submit", "status", "export"])
        parser.add_argument(
            "--state-file",
            required=True,
            help="Default-storage key of the JSON state file for this run (survives pod restarts).",
        )
        parser.add_argument(
            "--business-areas",
            help="Comma-separated business area slugs to encode (required for submit).",
        )
        parser.add_argument("--dedup-url")
        parser.add_argument("--dedup-token")
        parser.add_argument("--chunk-size", type=int, default=10000)
        parser.add_argument(
            "--upload-batch-size",
            type=int,
            default=DEFAULT_UPLOAD_BATCH_SIZE,
            help="Images per registration request.",
        )
        parser.add_argument(
            "--export-format",
            choices=["npy", "jsonl"],
            default="npy",
            help="Export zip format: npy (float32 matrix + index, ~4-5x smaller) or jsonl (self-describing).",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        if not options["dedup_url"] or not options["dedup_token"]:
            raise CommandError("Deduplication engine URL/token missing: pass --dedup-url and --dedup-token.")
        self.client = DedupEngineClient(options["dedup_url"], options["dedup_token"])
        self.state_key = options["state_file"]
        self.state = self._load_state()

        mode = options["mode"]
        if mode == "submit":
            self._run_submit(options)
        elif mode == "status":
            self._run_status()
        else:
            self._run_export(options["export_format"])

    # ----- state file (kept in Django default storage so it survives pod restarts) -----

    def _load_state(self) -> dict:
        if default_storage.exists(self.state_key):
            with default_storage.open(self.state_key, "rb") as f:
                return json.load(f)
        return {}

    def _save_state(self) -> None:
        data = json.dumps(self.state, indent=2).encode()
        # Storage.save() mangles existing names instead of overwriting, so delete first.
        if default_storage.exists(self.state_key):
            default_storage.delete(self.state_key)
        default_storage.save(self.state_key, ContentFile(data))

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

        if not self.state:
            self.state = {
                "run_id": uuid.uuid4().hex[:8],
                "chunk_size": options["chunk_size"],
                "upload_batch_size": options["upload_batch_size"],
                "business_areas": slugs,
                "chunks": [],
                "exports": {},
            }
            self._save_state()
        else:
            # Resume: pinned parameters must match, otherwise batch-offset resume would corrupt uploads.
            for key, value in (
                ("chunk_size", options["chunk_size"]),
                ("upload_batch_size", options["upload_batch_size"]),
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
                        "engine_state": None,
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
                items = [
                    {"reference_pk": str(individual.id), "filename": individual.photo.name} for individual in batch
                ]
                self.client.register_images(chunk["set_id"], items)
                chunk["image_count"] += len(items)
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

    # ----- status -----

    def _run_status(self) -> None:
        self._require_chunks()
        for chunk in self.state["chunks"]:
            if chunk["set_id"] and chunk["engine_state"] not in EXPORTABLE_STATES:
                chunk["engine_state"] = self.client.get_set(chunk["set_id"])["state"]
        self._save_state()
        self._print_summary()

    # ----- export -----

    def _run_export(self, export_format: str) -> None:
        self._require_chunks()
        exports = self.state.setdefault("exports", {})

        for slug in self.state["business_areas"]:
            chunks = [chunk for chunk in self.state["chunks"] if chunk["business_area"] == slug]
            not_ready = self._refresh_and_find_not_exportable(chunks)
            if not_ready:
                self.stdout.write(
                    f"{slug}: skipped, {len(not_ready)} chunk(s) not encoded yet "
                    f"(e.g. {not_ready[0]['reference_id']}: {not_ready[0]['engine_state'] or not_ready[0]['step']})"
                )
                continue

            # One export slot per CO and format: both npy and jsonl can coexist for a CO.
            export = exports.get(f"{slug}:{export_format}")
            if not export or not export.get("key"):
                self._request_export(slug, chunks, export_format)
            else:
                self._poll_export(slug, export, export_format)

        self._print_summary()

    def _refresh_and_find_not_exportable(self, chunks: list[dict]) -> list[dict]:
        not_ready = []
        for chunk in chunks:
            if chunk["step"] != "processed":
                not_ready.append(chunk)
                continue
            if chunk["engine_state"] not in EXPORTABLE_STATES:
                chunk["engine_state"] = self.client.get_set(chunk["set_id"])["state"]
                self._save_state()
            if chunk["engine_state"] not in EXPORTABLE_STATES:
                not_ready.append(chunk)
        return not_ready

    def _request_export(self, slug: str, chunks: list[dict], export_format: str) -> None:
        set_ids = [chunk["set_id"] for chunk in sorted(chunks, key=lambda c: c["index"])]
        response = self.client.create_export(reference_pk=slug, set_ids=set_ids, export_format=export_format)
        self.state["exports"][f"{slug}:{export_format}"] = {
            "key": response["key"],
            "format": export_format,
            "state": "pending",
            "requested_at": datetime.now(UTC).isoformat(),
        }
        self._save_state()
        self.stdout.write(f"{slug}: export requested ({export_format}), key {response['key']}")

    def _poll_export(self, slug: str, export: dict, export_format: str) -> None:
        status = self.client.export_status(export["key"])
        if status["state"] == "ready":
            # Re-polling a ready export renews the signed URL (the engine re-signs on every call).
            export.update(state="ready", url=status["url"], expires_at=status.get("expires_at"))
            self._save_state()
            self.stdout.write(self.style.SUCCESS(f"{slug}: export ready, url valid until {export['expires_at']}"))
        elif status["state"] == "failed":
            self.stdout.write(
                self.style.ERROR(f"{slug}: export failed ({status.get('error')}); key cleared, re-run export to retry.")
            )
            export.update(key=None, state="failed", error=status.get("error"))
            self._save_state()
        else:  # pending
            requested_at = datetime.fromisoformat(export["requested_at"])
            age = (datetime.now(UTC) - requested_at).total_seconds()
            if age > EXPORT_PENDING_TIMEOUT_SECONDS:
                self.stdout.write(f"{slug}: export pending for {age / 3600:.1f}h, assuming dead; re-requesting.")
                chunks = [chunk for chunk in self.state["chunks"] if chunk["business_area"] == slug]
                self._request_export(slug, chunks, export_format)
            else:
                self.stdout.write(f"{slug}: export still pending (key {export['key']}); re-run later.")

    # ----- helpers -----

    def _require_chunks(self) -> None:
        if not self.state.get("chunks"):
            raise CommandError("State file has no submitted chunks; run submit mode first.")

    def _print_summary(self) -> None:
        by_area: dict[str, dict[str, int]] = {}
        for chunk in self.state.get("chunks", []):
            area_stats = by_area.setdefault(chunk["business_area"], {})
            if chunk["step"] != "processed":
                status = f"submit:{chunk['step']}"
            else:
                status = chunk["engine_state"] or "unknown"
            area_stats[status] = area_stats.get(status, 0) + 1
        self.stdout.write("Summary:")
        for area, stats in sorted(by_area.items()):
            parts = ", ".join(f"{status}={count}" for status, count in sorted(stats.items()))
            export_infos = [
                f"export {export['format']}: {export['state']}"
                for entry_key, export in sorted(self.state.get("exports", {}).items())
                if entry_key.startswith(f"{area}:")
            ]
            export_info = f"; {', '.join(export_infos)}" if export_infos else ""
            self.stdout.write(f"  {area}: {parts}{export_info}")
