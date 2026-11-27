from collections.abc import Callable
from unittest.mock import MagicMock, patch

from django.core.exceptions import ImproperlyConfigured, SuspiciousOperation
import pytest
from rest_framework import serializers

from hope.api.endpoints.rdi.stored_images import (
    STORED_IMAGE_DIRECTORY_CONTEXT_KEY,
    StoredImageField,
    clean_image_flex_fields,
    get_stored_image_directory,
    get_stored_image_error,
    normalize_stored_image_name,
)
from hope.models import PendingIndividual

DIRECTORY = "afghanistan/ab12/"
PREFIX = f"2025/{DIRECTORY}"
CONTEXT = {STORED_IMAGE_DIRECTORY_CONTEXT_KEY: DIRECTORY}
MAX_LENGTH = 100
PHOTO_MAX_LENGTH = PendingIndividual._meta.get_field("photo").max_length


class PhotoSerializer(serializers.Serializer):
    photo = StoredImageField(model_field=(PendingIndividual, "photo"), allow_blank=True, allow_null=True)


def test_get_stored_image_directory_is_business_area_slug_and_program_code() -> None:
    assert get_stored_image_directory("afghanistan", "ab12") == "afghanistan/ab12/"


@pytest.mark.parametrize(
    ("business_area_slug", "program_code", "expected"),
    [
        ("south-sudan", "a-1_b", "south-sudan/a-1_b/"),
        ("a b/c", "x.y", "a_b_c/x_y/"),
    ],
)
def test_get_stored_image_directory_sanitizes_the_segments_like_hope_uploads(
    business_area_slug: str, program_code: str, expected: str
) -> None:
    assert get_stored_image_directory(business_area_slug, program_code) == expected


def test_normalize_stored_image_name_strips_whitespace_and_leading_slash() -> None:
    assert normalize_stored_image_name(" /2025/afghanistan/ab12/x.png ") == "2025/afghanistan/ab12/x.png"


def test_get_stored_image_error_existing_file(store_image: Callable[[str], str]) -> None:
    file_name = store_image(f"{PREFIX}CW_ind_1_photo.png")

    assert get_stored_image_error(file_name, DIRECTORY, MAX_LENGTH) is None


def test_get_stored_image_error_missing_file() -> None:
    file_name = f"{PREFIX}missing.png"

    assert get_stored_image_error(file_name, DIRECTORY, MAX_LENGTH) == f"File '{file_name}' does not exist in storage."


def test_get_stored_image_error_file_outside_the_directory_is_rejected_without_asking_the_storage(
    store_image: Callable[[str], str],
) -> None:
    file_name = store_image("2025/other-area/zz99/CW_ind_1_photo.png")

    with patch("hope.api.endpoints.rdi.stored_images.default_storage") as storage:
        error = get_stored_image_error(file_name, DIRECTORY, MAX_LENGTH)

    assert error == f"File name must start with '<year>/{DIRECTORY}'."
    storage.exists.assert_not_called()


@pytest.mark.parametrize("year", ["1999", "2025", "2031"])
def test_get_stored_image_error_accepts_any_year(store_image: Callable[[str], str], year: str) -> None:
    file_name = store_image(f"{year}/{DIRECTORY}CW_ind_1_photo.png")

    assert get_stored_image_error(file_name, DIRECTORY, MAX_LENGTH) is None


@pytest.mark.parametrize(
    "file_name",
    [
        f"{DIRECTORY}CW_ind_1_photo.png",
        f"abcd/{DIRECTORY}CW_ind_1_photo.png",
        f"20250/{DIRECTORY}CW_ind_1_photo.png",
        f"202/{DIRECTORY}CW_ind_1_photo.png",
        f"2025/x/{DIRECTORY}CW_ind_1_photo.png",
        "2025/afghanistan/ab123/CW_ind_1_photo.png",
    ],
)
def test_get_stored_image_error_requires_a_year_and_the_directory(file_name: str) -> None:
    with patch("hope.api.endpoints.rdi.stored_images.default_storage") as storage:
        error = get_stored_image_error(file_name, DIRECTORY, MAX_LENGTH)

    assert error == f"File name must start with '<year>/{DIRECTORY}'."
    storage.exists.assert_not_called()


@pytest.mark.parametrize(
    "file_name",
    [
        "",
        "../2025/afghanistan/ab12/x.png",
        "2025/afghanistan/ab12/../ab12/x.png",
        "2025/afghanistan/ab12/./x.png",
        "2025/afghanistan/ab12//x.png",
        "2025/afghanistan/ab12/x.png/",
        "2025\\afghanistan\\ab12\\x.png",
        "2025/afghanistan/ab12/x\x00.png",
    ],
)
def test_get_stored_image_error_invalid_file_name(file_name: str) -> None:
    assert get_stored_image_error(file_name, DIRECTORY, MAX_LENGTH) == f"Invalid file name '{file_name}'."


def test_get_stored_image_error_not_an_image() -> None:
    assert (
        get_stored_image_error(f"{PREFIX}x.exe", DIRECTORY, MAX_LENGTH)
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

    assert get_stored_image_error(file_name, DIRECTORY, MAX_LENGTH) == f"Invalid file name '{file_name}'."


def test_stored_image_field_normalizes_the_name(store_image: Callable[[str], str]) -> None:
    file_name = store_image(f"{PREFIX}CW_ind_1_photo.png")
    serializer = PhotoSerializer(data={"photo": f"/{file_name}"}, context=CONTEXT)

    assert serializer.is_valid()
    assert serializer.validated_data["photo"] == file_name


@pytest.mark.parametrize("empty_value", ["", None])
def test_stored_image_field_skips_empty_values(empty_value: str | None) -> None:
    serializer = PhotoSerializer(data={"photo": empty_value}, context=CONTEXT)

    assert serializer.is_valid()
    assert serializer.validated_data["photo"] == empty_value


def test_stored_image_field_uses_the_model_column_length() -> None:
    long_name = f"{PREFIX}{'a' * PHOTO_MAX_LENGTH}.png"
    serializer = PhotoSerializer(data={"photo": long_name}, context=CONTEXT)

    assert not serializer.is_valid()
    assert serializer.errors["photo"] == [f"File name must have no more than {PHOTO_MAX_LENGTH} characters."]


def test_stored_image_field_requires_the_directory_in_the_context() -> None:
    serializer = PhotoSerializer(data={"photo": f"{PREFIX}x.png"})

    with pytest.raises(KeyError, match=STORED_IMAGE_DIRECTORY_CONTEXT_KEY):
        serializer.is_valid()


def test_stored_image_field_fails_fast_when_the_model_field_has_no_max_length() -> None:
    with pytest.raises(ImproperlyConfigured, match="PendingIndividual.flex_fields has no max_length"):
        StoredImageField(model_field=(PendingIndividual, "flex_fields"))


def test_clean_image_flex_fields_normalizes_valid_value(store_image: Callable[[str], str]) -> None:
    file_name = store_image(f"{PREFIX}CW_ind_1_photo.png")
    flex_fields = {"photo": f"/{file_name}", "note": "/not/an/image"}

    errors = clean_image_flex_fields(flex_fields, {"photo"}, DIRECTORY)

    assert errors == {}
    assert flex_fields == {"photo": file_name, "note": "/not/an/image"}


def test_clean_image_flex_fields_missing_file() -> None:
    flex_fields = {"photo": f"{PREFIX}missing.png"}

    errors = clean_image_flex_fields(flex_fields, {"photo"}, DIRECTORY)

    assert errors == {"photo": [f"File '{PREFIX}missing.png' does not exist in storage."]}
    assert flex_fields == {"photo": f"{PREFIX}missing.png"}


def test_clean_image_flex_fields_file_of_another_program(store_image: Callable[[str], str]) -> None:
    file_name = store_image("2025/other-area/zz99/CW_ind_1_photo.png")

    errors = clean_image_flex_fields({"photo": file_name}, {"photo"}, DIRECTORY)

    assert errors == {"photo": [f"File name must start with '<year>/{DIRECTORY}'."]}


def test_clean_image_flex_fields_name_longer_than_flex_field_limit() -> None:
    errors = clean_image_flex_fields({"photo": f"{PREFIX}{'a' * 1024}.png"}, {"photo"}, DIRECTORY)

    assert errors == {"photo": ["File name must have no more than 1024 characters."]}


def test_clean_image_flex_fields_non_string_value() -> None:
    assert clean_image_flex_fields({"photo": 12345}, {"photo"}, DIRECTORY) == {"photo": ["Expected a file name."]}


@pytest.mark.parametrize("flex_fields", [None, {}, {"photo": ""}, {"photo": None}, {"other": "x"}])
def test_clean_image_flex_fields_nothing_to_check(flex_fields: dict | None) -> None:
    assert clean_image_flex_fields(flex_fields, {"photo"}, DIRECTORY) == {}
