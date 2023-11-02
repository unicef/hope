import csv
from django.db import transaction
from django.core.exceptions import ValidationError
from hct_mis_api.apps.household.models import Individual, Document, DocumentType
from hct_mis_api.apps.utils.phone import calculate_phone_numbers_validity


def update_phone_from_csv(file_path):
    with open(file_path, "r") as file:
        reader = csv.DictReader(file)

        with transaction.atomic():  # Start an atomic transaction
            for row in reader:
                unicef_id = row.get("individual__unicef_id")
                phone_no = row.get("individual__phone_no")

                if not unicef_id or not phone_no:
                    raise ValidationError("Missing values in CSV row.")

                # Find or create the Individual based on unicef_id
                individual, _ = Individual.objects.get_or_create(unicef_id=unicef_id)
                print(f"Updating phone number for {individual.unicef_id} from {individual.phone_no} to {phone_no}")
                individual.phone_no = phone_no
                calculate_phone_numbers_validity(individual)
                if not individual.phone_no_valid:
                    raise ValidationError("Invalid phone number.")
                # individual.save()
