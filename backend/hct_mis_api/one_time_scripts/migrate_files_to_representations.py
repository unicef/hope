import logging
import os
from typing import Any

from django.core.files.base import ContentFile

from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.grievance.models import GrievanceDocument
from hct_mis_api.apps.household.models import Document, Household, Individual

logger = logging.getLogger(__name__)


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
    for grievance_document in GrievanceDocument.objects.filter(
        grievance_ticket__is_original=False,
        grievance_ticket__business_area=business_area,
    ):
        if grievance_document.file:
            copy_file(grievance_document, "file")


def migrate_document_files(business_area: BusinessArea) -> None:
    logger.info(f"Migrating document files for business area: {business_area.name}")
    for document in Document.original_and_repr_objects.filter(
        individual__business_area=business_area,
        copied_from__isnull=False,
    ):
        if document.photo:
            copy_file(document, "photo")


def migrate_individual_files(business_area: BusinessArea) -> None:
    logger.info(f"Migrating individual files for business area: {business_area.name}")
    for individual in Individual.original_and_repr_objects.filter(
        is_original=False,
        business_area=business_area,
    ):
        if individual.photo:
            copy_file(individual, "photo")
        if individual.disability_certificate_picture:
            copy_file(individual, "disability_certificate_picture")


def migrate_household_files(business_area: BusinessArea) -> None:
    logger.info(f"Migrating household files for business area: {business_area.name}")
    for household in Household.original_and_repr_objects.filter(
        is_original=False,
        business_area=business_area,
    ):
        if household.consent_sign:
            copy_file(household, "consent_sign")
