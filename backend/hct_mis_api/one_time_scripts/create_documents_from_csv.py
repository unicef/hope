import csv
from django.db import transaction
from django.core.exceptions import ValidationError
from hct_mis_api.apps.household.models import Individual, Document, DocumentType


def create_documents(file_path):
    with open(file_path, "r") as file:
        reader = csv.DictReader(file)
        index = 1
        ids = []
        with transaction.atomic():  # Start an atomic transaction
            for row in reader:
                index += 1
                unicef_id = row.get("HeadOfHouseholdUnicefId")
                national_id = row.get("Id")
                if unicef_id in ids:
                    raise ValidationError(f"Duplicate unicef_id in CSV row {index}")
                ids.append(unicef_id)
                if not unicef_id or not national_id:
                    raise ValidationError("Missing values in CSV row.")

                # Find or create the Individual based on unicef_id
                individual = Individual.objects.get(unicef_id=unicef_id, business_area__slug="kenya")
                # Assuming there's a DocumentType you want to link to this Document, fetch it here.
                # Adjust this as needed.
                document_type = DocumentType.objects.filter(is_identity_document=True, key="national_id").first()
                if not document_type:
                    raise ValidationError("No DocumentType found.")
                if Document.objects.filter(individual=individual, type=document_type).count() == 1:
                    print(f"Document for {individual.unicef_id} already exists.")
                    document = Document.objects.get(individual=individual, type=document_type)
                    print(
                        f"Updating document for {individual.unicef_id} from {document.document_number} to {national_id}"
                    )
                    document.document_number = national_id
                    document.save()
                elif Document.objects.filter(individual=individual, type=document_type).count() > 1:
                    Document.objects.filter(individual=individual, type=document_type).update(
                        status=Document.STATUS_INVALID
                    )
                    print(f"Invalidated old documents, creating document for {individual.unicef_id}: {national_id}")
                    Document.objects.create(
                        document_number=national_id,
                        individual=individual,
                        type=document_type,
                        status=Document.STATUS_VALID,
                    )
                else:
                    print(f"Creating document for {individual.unicef_id}: {national_id}")
                    Document.objects.create(
                        document_number=national_id,
                        individual=individual,
                        type=document_type,
                        status=Document.STATUS_VALID,
                    )
