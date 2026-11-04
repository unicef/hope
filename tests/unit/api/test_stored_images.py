from collections.abc import Callable
from unittest.mock import MagicMock, patch

from django.core.exceptions import ImproperlyConfigured, SuspiciousOperation
import pytest
from rest_framework import serializers

from hope.api.endpoints.rdi.stored_images import (
    STORED_IMAGE_PREFIX_CONTEXT_KEY,
    StoredImageField,
    get_stored_image_error,
    get_stored_image_prefix,
    normalize_stored_image_name,
)
from hope.models import PendingIndividual

PREFIX = "AFG/ab12/"
MAX_LENGTH = 100
PHOTO_MAX_LENGTH = PendingIndividual._meta.get_field("photo").max_length


class PhotoSerializer(serializers.Serializer):
    photo = StoredImageField(model_field=(PendingIndividual, "photo"), allow_blank=True, allow_null=True)


def test_get_stored_image_prefix_joins_business_area_and_program_codes() -> None:
    assert get_stored_image_prefix("AFG", "ab12") == "AFG/ab12/"


@pytest.mark.parametrize(
    ("business_area_code", "program_code", "expected"),
    [
        ("A/F G", "a..b", "A_F_G/a..b/"),
        (" AFG ", " ab12 ", "AFG/ab12/"),
    ],
)
def test_get_stored_image_prefix_sanitizes_the_codes_like_cw(
    business_area_code: str, program_code: str, expected: str
) -> None:
    assert get_stored_image_prefix(business_area_code, program_code) == expected


def test_normalize_stored_image_name_strips_whitespace_and_leading_slash() -> None:
    assert normalize_stored_image_name(" /AFG/ab12/x.png ") == "AFG/ab12/x.png"


def test_get_stored_image_error_existing_file(store_image: Callable[[str], str]) -> None:
    file_name = store_image(f"{PREFIX}CW_ind_1_photo.png")

    assert get_stored_image_error(file_name, PREFIX, MAX_LENGTH) is None


def test_get_stored_image_error_missing_file() -> None:
    file_name = f"{PREFIX}missing.png"

    assert get_stored_image_error(file_name, PREFIX, MAX_LENGTH) == f"File '{file_name}' does not exist in storage."


def test_get_stored_image_error_file_outside_prefix_is_rejected_without_asking_the_storage(
    store_image: Callable[[str], str],
) -> None:
    file_name = store_image("OTH/zz99/CW_ind_1_photo.png")

    with patch("hope.api.endpoints.rdi.stored_images.default_storage") as storage:
        error = get_stored_image_error(file_name, PREFIX, MAX_LENGTH)

    assert error == f"File name must start with '{PREFIX}'."
    storage.exists.assert_not_called()


@pytest.mark.parametrize(
    "file_name",
    [
        "",
        "../AFG/ab12/x.png",
        "AFG/ab12/../ab12/x.png",
        "AFG/ab12/./x.png",
        "AFG/ab12//x.png",
        "AFG/ab12/x.png/",
        "AFG\\ab12\\x.png",
        "AFG/ab12/x\x00.png",
    ],
)
def test_get_stored_image_error_invalid_file_name(file_name: str) -> None:
    assert get_stored_image_error(file_name, PREFIX, MAX_LENGTH) == f"Invalid file name '{file_name}'."


def test_get_stored_image_error_not_an_image() -> None:
    assert (
        get_stored_image_error(f"{PREFIX}x.exe", PREFIX, MAX_LENGTH)
        == f"File '{PREFIX}x.exe' is not a supported image type."
    )


def test_get_stored_image_error_too_long() -> None:
    assert (
        get_stored_image_error(f"{PREFIX}x.png", PREFIX, max_length=10)
        == "File name must have no more than 10 characters."
    )


@pytest.mark.parametrize("storage_error", [SuspiciousOperation, ValueError])
@patch("hope.api.endpoints.rdi.stored_images.default_storage")
def test_get_stored_image_error_storage_rejects_name(mock_storage: MagicMock, storage_error: type[Exception]) -> None:
    mock_storage.exists.side_effect = storage_error
    file_name = f"{PREFIX}x.png"

    assert get_stored_image_error(file_name, PREFIX, MAX_LENGTH) == f"Invalid file name '{file_name}'."


def test_stored_image_field_normalizes_the_name(store_image: Callable[[str], str]) -> None:
    file_name = store_image(f"{PREFIX}CW_ind_1_photo.png")
    serializer = PhotoSerializer(data={"photo": f"/{file_name}"}, context={STORED_IMAGE_PREFIX_CONTEXT_KEY: PREFIX})

    assert serializer.is_valid()
    assert serializer.validated_data["photo"] == file_name


@pytest.mark.parametrize("empty_value", ["", None])
def test_stored_image_field_skips_empty_values(empty_value: str | None) -> None:
    serializer = PhotoSerializer(data={"photo": empty_value}, context={STORED_IMAGE_PREFIX_CONTEXT_KEY: PREFIX})

    assert serializer.is_valid()
    assert serializer.validated_data["photo"] == empty_value


def test_stored_image_field_uses_the_model_column_length() -> None:
    long_name = f"{PREFIX}{'a' * PHOTO_MAX_LENGTH}.png"
    serializer = PhotoSerializer(data={"photo": long_name}, context={STORED_IMAGE_PREFIX_CONTEXT_KEY: PREFIX})

    assert not serializer.is_valid()
    assert serializer.errors["photo"] == [f"File name must have no more than {PHOTO_MAX_LENGTH} characters."]


def test_stored_image_field_requires_the_prefix_in_the_context() -> None:
    serializer = PhotoSerializer(data={"photo": f"{PREFIX}x.png"})

    with pytest.raises(KeyError, match=STORED_IMAGE_PREFIX_CONTEXT_KEY):
        serializer.is_valid()


def test_stored_image_field_fails_fast_when_the_model_field_has_no_max_length() -> None:
    with pytest.raises(ImproperlyConfigured, match="PendingIndividual.flex_fields has no max_length"):
        StoredImageField(model_field=(PendingIndividual, "flex_fields"))
