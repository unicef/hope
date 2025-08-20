import logging
from typing import Any

from django.conf import settings
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError

from hope.apps.grievance.models import GrievanceDocument
from hope.apps.utils.exceptions import log_and_raise

logger = logging.getLogger(__name__)


class DataChangeValidator:
    @classmethod
    def verify_approve_data(cls, approve_data: dict) -> None:
        if not isinstance(approve_data, dict):
            log_and_raise("Fields must be a dictionary with field name as key and boolean as a value")
        # valid roles
        roles_data = approve_data.get("roles", [])
        for role in roles_data:
            if "individual_id" not in role:
                log_and_raise("Can't find individual_id in role")
            if "approve_status" not in role:
                log_and_raise("Can't find approve_status in role")
            if not (
                isinstance(role["approve_status"], bool)
                or (isinstance(role["approve_status"], str) and role["approve_status"].lower() in ["true", "false"])
            ):
                log_and_raise("Value for approve_status must be boolean or string")

        if not all(
            isinstance(v, bool) or (isinstance(v, str) and v.lower() in ["true", "false"])
            for k, v in approve_data.items()
            if k != "roles"
        ):
            log_and_raise("Values must be booleans")

    @classmethod
    def verify_approve_data_against_object_data(cls, object_data: dict, approve_data: dict) -> None:
        error = "Provided fields are not the same as provided in the object approve data"
        if approve_data and not isinstance(object_data, dict):
            log_and_raise(error)

        approve_data_names = set(approve_data.keys())
        object_data_names = set(object_data.keys())
        if not approve_data_names.issubset(object_data_names):
            log_and_raise(error)


def validate_file(file: Any) -> None:
    if file.content_type in settings.GRIEVANCE_UPLOAD_CONTENT_TYPES:
        file_size_MB = round(file.size / (1024 * 1024), 2)
        if file.size > settings.GRIEVANCE_ONE_UPLOAD_MAX_MEMORY_SIZE:
            raise ValidationError(_(f"File {file.name} of size {file_size_MB}MB is above max size limit"))
    else:
        raise ValidationError(_("File type not supported"))


def validate_files_size(files: list[Any]) -> None:
    if sum(file.size for file in files) > settings.FILE_UPLOAD_MAX_MEMORY_SIZE:
        raise ValidationError("Total size of files can not be larger than 25mb.")


def validate_grievance_documents_size(ticket_id: str, new_documents: list[dict], is_updated: bool = False) -> None:
    grievance_documents = GrievanceDocument.objects.filter(grievance_ticket_id=ticket_id)

    if is_updated:
        current_documents_size = sum(
            grievance_documents.exclude(id__in=[document["id"] for document in new_documents]).values_list(
                "file_size", flat=True
            )
        )
    else:
        current_documents_size = sum(grievance_documents.values_list("file_size", flat=True))

    new_documents_size = sum(document["file"].size for document in new_documents)

    if current_documents_size + new_documents_size > settings.FILE_UPLOAD_MAX_MEMORY_SIZE:
        raise ValidationError("Adding/Updating of new files exceed 25mb maximum size of files")
