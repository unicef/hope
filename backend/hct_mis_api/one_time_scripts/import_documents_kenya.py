import csv
from django.db import transaction
from django.core.exceptions import ValidationError

from hct_mis_api.apps.geo.models import Country
from hct_mis_api.apps.household.models import Individual, DocumentType, Document


def import_csv(file_path):
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        document_type = DocumentType.objects.get(key='national_id')
        country = Country.objects.get(name='Kenya')
        if not document_type:
            raise ValidationError("No DocumentType found.")
        with transaction.atomic():  # Start an atomic transaction
            for row in reader:
                unicef_id = row.get('individual__unicef_id')
                national_id = row.get('national_id')
                if not unicef_id or not national_id:
                    continue
                individual = Individual.objects.get(unicef_id=unicef_id)
                print(individual, document_type, national_id)
                Document.objects.create(
                    document_number=national_id,
                    individual=individual,
                    type=document_type,
                    status=Document.STATUS_VALID,
                    country=country
                )


def remove_documents(file_path):
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        document_type = DocumentType.objects.get(key='national_id')
        if not document_type:
            raise ValidationError("No DocumentType found.")
        with transaction.atomic():  # Start an atomic transaction
            for row in reader:
                unicef_id = row.get('individual__unicef_id')
                national_id = row.get('national_id')
                if not unicef_id or not national_id:
                    continue
                individual = Individual.objects.get(unicef_id=unicef_id)
                print(individual, document_type, national_id)
                Document.objects.get(type=document_type, document_number=national_id,
                                     individual=individual).delete()
