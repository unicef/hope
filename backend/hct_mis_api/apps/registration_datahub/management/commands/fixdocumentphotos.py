from django.core.management import BaseCommand
from django.db.models import F

from hct_mis_api.apps.household.models import Document
from hct_mis_api.apps.registration_datahub.models import ImportedDocument


def fix_document_photos() -> None:
    imported_documents = (
        ImportedDocument.objects.exclude(photo="")
        .annotate(hct_id=F("individual__registration_data_import__hct_id"))
        .values("document_number", "photo", "hct_id")
    )

    documents = []
    for imported_document in imported_documents:
        hct_id = imported_document.get("hct_id")
        document_number = imported_document.get("document_number")
        document_photo = imported_document.get("photo")

        document = Document.objects.filter(
            individual__registration_data_import__id=hct_id, document_number=document_number, photo=""
        ).first()

        if document:
            document.photo = document_photo
            documents.append(document)
    Document.objects.bulk_update(documents, ["photo"])


class Command(BaseCommand):
    help = "Fix document photos in existing data"

    def handle(self, *args, **options):
        fix_document_photos()
        self.stdout.write("Documents photos fixed")
