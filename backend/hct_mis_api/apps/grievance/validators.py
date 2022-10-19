import logging

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from graphql import GraphQLError

from hct_mis_api.apps.core.utils import decode_id_string
from hct_mis_api.apps.grievance.models import GrievanceDocument
from hct_mis_api.apps.utils.exceptions import log_and_raise

logger = logging.getLogger(__name__)


class DataChangeValidator:
    @classmethod
    def verify_approve_data(cls, approve_data):
        if not isinstance(approve_data, dict):
            log_and_raise("Fields must be a dictionary with field name as key and boolean as a value")

        if not all([isinstance(value, bool) for value in approve_data.values()]):
            log_and_raise("Values must be booleans")

    @classmethod
    def verify_approve_data_against_object_data(cls, object_data, approve_data):
        error = "Provided fields are not the same as provided in the object approve data"
        if approve_data and not isinstance(object_data, dict):
            log_and_raise(error)

        approve_data_names = set(approve_data.keys())
        object_data_names = set(object_data.keys())
        if not approve_data_names.issubset(object_data_names):
            log_and_raise(error)


def validate_file(file):
    if file.content_type in settings.GRIEVANCE_UPLOAD_CONTENT_TYPES:
        if file.size > settings.GRIEVANCE_ONE_UPLOAD_MAX_MEMORY_SIZE:
            raise GraphQLError(_(f"File {file.name} of size {file.size} is above max size limit"))
    else:
        raise GraphQLError(_("File type not supported"))


def validate_files_size(files):
    if sum(file.size for file in files) > settings.FILE_UPLOAD_MAX_MEMORY_SIZE:
        raise GraphQLError("Total size of files can not be larger than 25mb.")


def validate_grievance_documents_size(ticket_id, new_documents, is_updated=False):
    grievance_documents = GrievanceDocument.objects.filter(grievance_ticket_id=ticket_id)

    if is_updated:
        current_documents_size = sum(
            (
                grievance_documents.exclude(
                    id__in=[decode_id_string(document["id"]) for document in new_documents]
                ).values_list("file_size", flat=True)
            )
        )
    else:
        current_documents_size = sum(grievance_documents.values_list("file_size", flat=True))

    new_documents_size = sum(document["file"].size for document in new_documents)

    if current_documents_size + new_documents_size > settings.FILE_UPLOAD_MAX_MEMORY_SIZE:
        raise GraphQLError("Adding/Updating of new files exceed 25mb maximum size of files")

    return current_documents_size + new_documents_size
