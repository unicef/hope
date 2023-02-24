import os
import shutil
from typing import Any

from django.conf import settings
from django.core.management import BaseCommand


class Command(BaseCommand):
    def handle(self, *args: Any, **options: Any) -> None:
        print("Clearing the `generated` dir")
        shutil.rmtree(os.path.join(settings.PROJECT_ROOT, "..", "generated"))
