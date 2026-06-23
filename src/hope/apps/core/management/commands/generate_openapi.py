import json
from pathlib import Path
from typing import Any

from django.core.management import BaseCommand, call_command
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

from hope.apps.core.api.views import ChoicesViewSet

DEFAULT_OUTPUT_DIR = Path("src/frontend/data")


class Command(BaseCommand):
    help = (
        "Generate the OpenAPI schema and the ChoicesViewSet runtime values consumed by the "
        "frontend type generator (bun run generate-rest-api-types-camelcase), without a running server."
    )

    def add_arguments(self, parser: Any) -> None:
        parser.add_argument(
            "--output-dir",
            default=str(DEFAULT_OUTPUT_DIR),
            help=f"Directory to write openapi.yml and choices.json into (default: {DEFAULT_OUTPUT_DIR}).",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        output_dir = Path(options["output_dir"])
        output_dir.mkdir(parents=True, exist_ok=True)

        schema_path = output_dir / "openapi.yml"
        choices_path = output_dir / "choices.json"

        self.stdout.write("Generating OpenAPI schema...")
        call_command("spectacular", file=str(schema_path), validate=True)
        self.stdout.write(self.style.SUCCESS(f"  wrote {schema_path}"))

        self.stdout.write("Collecting ChoicesViewSet runtime values...")
        choices = self._collect_choices()
        choices_path.write_text(json.dumps(choices, indent=2, ensure_ascii=False))
        self.stdout.write(self.style.SUCCESS(f"  wrote {choices_path} ({len(choices)} choice endpoints)"))

    def _collect_choices(self) -> dict[str, Any]:
        viewset = ChoicesViewSet()
        viewset.request = Request(APIRequestFactory().get("/"))
        viewset.format_kwarg = None

        result: dict[str, Any] = {}

        for action in ChoicesViewSet.get_extra_actions():
            if action.detail or "get" not in action.mapping:
                continue
            response = getattr(viewset, action.__name__)(viewset.request)
            result[action.url_path] = response.data
            self.stdout.write(f"  + {action.url_path} ({len(response.data)} choices)")

        return result
