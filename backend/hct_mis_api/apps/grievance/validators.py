import logging

from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from graphql import GraphQLError

logger = logging.getLogger(__name__)


class DataChangeValidator:
    @classmethod
    def verify_approve_data(cls, approve_data):
        if not isinstance(approve_data, dict):
            logger.error("Fields must be a dictionary with field name as key and boolean as a value")
            raise GraphQLError("Fields must be a dictionary with field name as key and boolean as a value")

        if not all([isinstance(value, bool) for value in approve_data.values()]):
            logger.error("Values must be booleans")
            raise GraphQLError("Values must be booleans")

    @classmethod
    def verify_approve_data_against_object_data(cls, object_data, approve_data):
        error = "Provided fields are not the same as provided in the object approve data"
        if approve_data and not isinstance(object_data, dict):
            logger.error(error)
            raise GraphQLError(error)

        approve_data_names = set(approve_data.keys())
        object_data_names = set(object_data.keys())
        if not approve_data_names.issubset(object_data_names):
            logger.error(error)
            raise GraphQLError(error)


def validate_file(file):
    if file.content_type in settings.GRIEVANCE_UPLOAD_CONTENT_TYPES:
        if file.size > settings.GRIEVANCE_ONE_UPLOAD_MAX_MEMORY_SIZE:
            raise GraphQLError(_(f"File {file.name} of size {file.size} is above max size limit"))
    else:
        raise GraphQLError(_("File type not supported"))


def validate_files_size(files):
    if sum(file.size for file in files) > settings.FILE_UPLOAD_MAX_MEMORY_SIZE:
        raise GraphQLError("Total size of files can not be larger than 25mb.")
