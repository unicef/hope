import logging
import os
from typing import Any

from django.core.files.base import ContentFile

from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.grievance.models import GrievanceDocument
from hct_mis_api.apps.household.models import Document, Household, Individual

logger = logging.getLogger(__name__)

BATCH_SIZE = 500


def migrate_files_to_representations() -> None:
    for business_area in BusinessArea.objects.all():
        logger.info(f"Migrating files for business area: {business_area.name}")
        migrate_files_to_representations_per_business_area(business_area)


def migrate_files_to_representations_per_business_area(business_area: BusinessArea) -> None:
    migrate_grievance_document_files(business_area)
    migrate_document_files(business_area)
    migrate_individual_files(business_area)
    migrate_household_files(business_area)


def copy_file(instance: Any, file_field: str) -> None:
    try:
        name_and_extension = os.path.splitext(getattr(instance, file_field).name)
        new_file = ContentFile(getattr(instance, file_field).read())
        new_file.name = f"{name_and_extension[0]}{instance.id}{name_and_extension[1]}"
        setattr(instance, file_field, new_file)
        instance.save()
    except Exception:
        logger.info(f"Failed to copy file for {instance.__class__.__name__}: {instance.id}")


def migrate_grievance_document_files(business_area: BusinessArea) -> None:
    logger.info(f"Migrating grievance document files for business area: {business_area.name}")
    grievance_document_ids = list(
        GrievanceDocument.objects.filter(
            grievance_ticket__is_original=False,
            grievance_ticket__business_area=business_area,
        )
        .exclude(file="")
        .values_list("id", flat=True)
    )
    for batch_start in range(0, len(grievance_document_ids), BATCH_SIZE):
        batch_end = batch_start + BATCH_SIZE
        logging.info(
            f"{business_area.name}: Grievance document batch {batch_start}-{batch_end}/{len(grievance_document_ids)}"
        )
        batched_ids = grievance_document_ids[batch_start:batch_end]
        grievance_documents = list(GrievanceDocument.objects.filter(id__in=batched_ids))
        for grievance_document in grievance_documents:
            copy_file(grievance_document, "file")


def migrate_document_files(business_area: BusinessArea) -> None:
    logger.info(f"Migrating document files for business area: {business_area.name}")
    document_ids = list(
        Document.original_and_repr_objects.filter(
            individual__business_area=business_area,
            copied_from__isnull=False,
        )
        .exclude(photo="")
        .values_list("id", flat=True)
    )
    for batch_start in range(0, len(document_ids), BATCH_SIZE):
        batch_end = batch_start + BATCH_SIZE
        logging.info(f"{business_area.name}: Document batch {batch_start}-{batch_end}/{len(document_ids)}")
        batched_ids = document_ids[batch_start:batch_end]
        documents = list(Document.original_and_repr_objects.filter(id__in=batched_ids))
        for document in documents:
            copy_file(document, "photo")


def migrate_individual_files(business_area: BusinessArea) -> None:
    logger.info(f"Migrating individual files for business area: {business_area.name}")
    individual_ids = list(
        Individual.original_and_repr_objects.filter(
            is_original=False,
            business_area=business_area,
        )
        .exclude(photo="", disability_certificate_picture="")
        .values_list("id", flat=True)
    )
    for batch_start in range(0, len(individual_ids), BATCH_SIZE):
        batch_end = batch_start + BATCH_SIZE
        logging.info(f"{business_area.name}: Individual batch {batch_start}-{batch_end}/{len(individual_ids)}")
        batched_ids = individual_ids[batch_start:batch_end]
        individuals = list(Individual.original_and_repr_objects.filter(id__in=batched_ids))
        for individual in individuals:
            if individual.photo:
                copy_file(individual, "photo")
            if individual.disability_certificate_picture:
                copy_file(individual, "disability_certificate_picture")


def migrate_household_files(business_area: BusinessArea) -> None:
    logger.info(f"Migrating household files for business area: {business_area.name}")
    household_ids = list(
        Household.original_and_repr_objects.filter(
            is_original=False,
            business_area=business_area,
        )
        .exclude(consent_sign="")
        .values_list("id", flat=True)
    )
    for batch_start in range(0, len(household_ids), BATCH_SIZE):
        batch_end = batch_start + BATCH_SIZE
        logging.info(f"{business_area.name}: Household batch {batch_start}-{batch_end}/{len(household_ids)}")
        batched_ids = household_ids[batch_start:batch_end]
        households = list(Household.original_and_repr_objects.filter(id__in=batched_ids))
        for household in households:
            copy_file(household, "consent_sign")
