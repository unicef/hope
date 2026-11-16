from functools import cache
from pathlib import PurePosixPath
import posixpath
import re
from typing import TYPE_CHECKING, Any

from django.core.exceptions import ImproperlyConfigured, SuspiciousOperation
from django.core.files.storage import default_storage
from django.core.files.utils import validate_file_name
from django.core.validators import get_available_image_extensions
from django.db.models import Model
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from hope.apps.core.upload_paths import build_upload_path

if TYPE_CHECKING:
    from collections.abc import Iterable

STORED_IMAGE_DIRECTORY_CONTEXT_KEY = "stored_image_directory"
# Azure blob name limit, flex fields are stored in a JSON column
FLEX_FIELD_FILE_NAME_MAX_LENGTH = 1024


@cache
def _get_image_extensions() -> frozenset[str]:
    return frozenset(get_available_image_extensions())


_YEAR_SEGMENT = re.compile(r"\d{4}/")


def get_stored_image_directory(business_area_slug: str, program_code: str) -> str:
    """Return ``<business area slug>/<program code>/``, the part of an image name that identifies its program.

    Images are stored as ``<year>/<business area slug>/<program code>/<file name>``, the layout of the files HOPE
    stores itself (see ``hope.apps.core.upload_paths``). The year is not part of the directory: it comes from the
    program start date, which can be edited after images were written. The segments are cleaned like HOPE
    cleans them when it builds the path.
    """
    return build_upload_path("", business_area_slug=business_area_slug, program_code=program_code).partition("/")[2]


def normalize_stored_image_name(file_name: str) -> str:
    return file_name.strip().lstrip("/")


def _is_safe_file_name(file_name: str) -> bool:
    if "\\" in file_name or "\x00" in file_name or posixpath.normpath(file_name) != file_name:
        return False
    try:
        validate_file_name(file_name, allow_relative_path=True)
    except SuspiciousOperation:
        return False
    return True


def _get_file_name_error(file_name: str, directory: str, max_length: int) -> str | None:
    if len(file_name) > max_length:
        return f"File name must have no more than {max_length} characters."
    if not _is_safe_file_name(file_name):
        return f"Invalid file name '{file_name}'."
    year = _YEAR_SEGMENT.match(file_name)
    if not year or not file_name.startswith(directory, year.end()):
        return f"File name must start with '<year>/{directory}'."
    if PurePosixPath(file_name).suffix[1:].lower() not in _get_image_extensions():
        return f"File '{file_name}' is not a supported image type."
    return None


def get_stored_image_error(file_name: str, directory: str, max_length: int) -> str | None:
    """Return why ``file_name`` can't be used as a reference to an image in the media storage, None if it can.

    The name has to be a plain relative path ``<year>/<directory>/<file name>``: backends resolve names
    differently (Azure rewrites ``a/../b`` to ``b``), so the name that was checked has to be the one that is
    stored. The storage is asked only after the name is known to belong to ``directory``, so a client can't probe
    for files of other business areas or programs.
    """
    if error := _get_file_name_error(file_name, directory, max_length):
        return error
    try:
        exists = default_storage.exists(file_name)
    except (SuspiciousOperation, ValueError):
        return f"Invalid file name '{file_name}'."
    return None if exists else f"File '{file_name}' does not exist in storage."


class StoredImageField(serializers.CharField):
    """Name of an image CW has already written to the media storage.

    The validated name is returned as a string, ready to be assigned to the model file field given in
    ``model_field``, whose ``max_length`` limits the name. The serializer context has to provide the
    allowed directory under ``stored_image_directory``.
    """

    def __init__(self, *, model_field: tuple[type[Model], str], **kwargs: Any) -> None:
        model, field_name = model_field
        max_length = getattr(model._meta.get_field(field_name), "max_length", None)
        if max_length is None:
            raise ImproperlyConfigured(f"{model.__name__}.{field_name} has no max_length to validate names against.")
        self.file_name_max_length = max_length
        kwargs.setdefault(
            "help_text",
            "Name of an image in the media storage, relative to the container root, as "
            "'<year>/<business area slug>/<program code>/<file name>'.",
        )
        super().__init__(**kwargs)

    def to_internal_value(self, data: Any) -> str:
        file_name = normalize_stored_image_name(super().to_internal_value(data))
        if error := get_stored_image_error(
            file_name, self.context[STORED_IMAGE_DIRECTORY_CONTEXT_KEY], self.file_name_max_length
        ):
            raise ValidationError(error)
        return file_name


def clean_image_flex_fields(
    flex_fields: dict | None, image_field_names: "Iterable[str]", directory: str
) -> dict[str, list[str]]:
    """Normalize IMAGE type flex fields in place and return errors keyed by flex field name."""
    if not flex_fields:
        return {}

    errors: dict[str, list[str]] = {}
    for field_name in image_field_names:
        value = flex_fields.get(field_name)
        if not value:
            continue
        if not isinstance(value, str):
            errors[field_name] = ["Expected a file name."]
            continue
        file_name = normalize_stored_image_name(value)
        if error := get_stored_image_error(file_name, directory, FLEX_FIELD_FILE_NAME_MAX_LENGTH):
            errors[field_name] = [error]
        else:
            flex_fields[field_name] = file_name
    return errors


class ImageFlexFieldsValidationMixin:
    context: dict[str, Any]

    def validate_flex_fields(self, value: dict | None) -> dict | None:
        if not value:
            return value
        image_field_names = self.context["get_image_flex_fields"]() or ()
        if errors := clean_image_flex_fields(
            value, image_field_names, self.context[STORED_IMAGE_DIRECTORY_CONTEXT_KEY]
        ):
            raise ValidationError(errors)
        return value
