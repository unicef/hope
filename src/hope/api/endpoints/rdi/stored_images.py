from functools import cache
from pathlib import PurePosixPath
import posixpath
import re
from typing import Any

from django.core.exceptions import ImproperlyConfigured, SuspiciousOperation
from django.core.files.storage import default_storage
from django.core.files.utils import validate_file_name
from django.core.validators import get_available_image_extensions
from django.db.models import Model
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

STORED_IMAGE_PREFIX_CONTEXT_KEY = "stored_image_prefix"


@cache
def _get_image_extensions() -> frozenset[str]:
    return frozenset(get_available_image_extensions())


def get_stored_image_prefix(business_area_code: str, program_code: str) -> str:
    """Return the directory CW writes the images of a program to: ``{business area code}/{program code}/``.

    The codes are sanitized the same way as in CW, the two have to stay in sync.
    """

    def sanitize(value: str) -> str:
        return re.sub(r"[^A-Za-z0-9._-]", "_", value.strip())

    return f"{sanitize(business_area_code)}/{sanitize(program_code)}/"


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


def _get_file_name_error(file_name: str, prefix: str, max_length: int) -> str | None:
    if len(file_name) > max_length:
        return f"File name must have no more than {max_length} characters."
    if not _is_safe_file_name(file_name):
        return f"Invalid file name '{file_name}'."
    if not file_name.startswith(prefix):
        return f"File name must start with '{prefix}'."
    if PurePosixPath(file_name).suffix[1:].lower() not in _get_image_extensions():
        return f"File '{file_name}' is not a supported image type."
    return None


def get_stored_image_error(file_name: str, prefix: str, max_length: int) -> str | None:
    """Return why ``file_name`` can't be used as a reference to an image in the media storage, None if it can.

    The name has to be a plain relative path inside ``prefix``: backends resolve names differently (Azure
    rewrites ``a/../b`` to ``b``), so the name that was checked has to be the one that is stored. The storage
    is asked only after the name is known to be inside ``prefix``, so a client can't probe for other files.
    """
    if error := _get_file_name_error(file_name, prefix, max_length):
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
    allowed directory under ``stored_image_prefix``.
    """

    def __init__(self, *, model_field: tuple[type[Model], str], **kwargs: Any) -> None:
        model, field_name = model_field
        max_length = getattr(model._meta.get_field(field_name), "max_length", None)
        if max_length is None:
            raise ImproperlyConfigured(f"{model.__name__}.{field_name} has no max_length to validate names against.")
        self.file_name_max_length = max_length
        kwargs.setdefault(
            "help_text",
            "Name of an image in the media storage, relative to the container root and starting with "
            "'{business area code}/{program code}/'.",
        )
        super().__init__(**kwargs)

    def to_internal_value(self, data: Any) -> str:
        file_name = normalize_stored_image_name(super().to_internal_value(data))
        if error := get_stored_image_error(
            file_name, self.context[STORED_IMAGE_PREFIX_CONTEXT_KEY], self.file_name_max_length
        ):
            raise ValidationError(error)
        return file_name
