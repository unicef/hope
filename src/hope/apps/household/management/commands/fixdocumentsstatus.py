from typing import Any

from django.core.management import BaseCommand

from models.household import Document


def fix_documents_statuses() -> int:
    return Document.objects.filter(status=Document.STATUS_VALID, individual__withdrawn=True).update(
        status=Document.STATUS_NEED_INVESTIGATION
    )


class Command(BaseCommand):
    help = "Fix documents status"

    def handle(self, *args: Any, **options: Any) -> None:
        self.stdout.write("Start fixing")
        fixed_documents = fix_documents_statuses()
        self.stdout.write(f"Fixed {fixed_documents} documents")
