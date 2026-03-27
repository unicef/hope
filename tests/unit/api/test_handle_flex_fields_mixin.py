import base64
from collections.abc import Callable
import contextlib
from pathlib import Path

from django.core.files.storage import default_storage
import pytest

from extras.test_utils.factories.core import FlexibleAttributeFactory
from hope.api.endpoints.rdi.lax import HandleFlexFieldsMixin
from hope.api.endpoints.rdi.mixin import PhotoMixin
from hope.models import FlexibleAttribute

pytestmark = pytest.mark.django_db


class ImageFlexFieldMixin(HandleFlexFieldsMixin, PhotoMixin):
    def __init__(self) -> None:
        self.saved_paths: list[str] = []


@pytest.fixture
def flex_mixin() -> HandleFlexFieldsMixin:
    return HandleFlexFieldsMixin()


@pytest.fixture
def individual_flex_field() -> FlexibleAttribute:
    return FlexibleAttributeFactory(
        name="custom_field_i_f",
        label={"English(EN)": "Custom Field"},
        type=FlexibleAttribute.STRING,
        associated_with=FlexibleAttribute.ASSOCIATED_WITH_INDIVIDUAL,
    )


@pytest.fixture
def household_flex_field() -> FlexibleAttribute:
    return FlexibleAttributeFactory(
        name="household_field_h_f",
        label={"English(EN)": "Household Field"},
        type=FlexibleAttribute.STRING,
        associated_with=FlexibleAttribute.ASSOCIATED_WITH_HOUSEHOLD,
    )


@pytest.fixture
def removed_flex_field() -> FlexibleAttribute:
    return FlexibleAttributeFactory(
        name="removed_field_i_f",
        label={"English(EN)": "Removed Field"},
        type=FlexibleAttribute.STRING,
        associated_with=FlexibleAttribute.ASSOCIATED_WITH_INDIVIDUAL,
        is_removed=True,
    )


def test_get_registered_flex_fields_individual(
    flex_mixin: HandleFlexFieldsMixin,
    individual_flex_field: FlexibleAttribute,
    removed_flex_field: FlexibleAttribute,
) -> None:
    flex_fields = flex_mixin.get_registered_flex_fields(FlexibleAttribute.ASSOCIATED_WITH_INDIVIDUAL)

    assert "custom_field" in flex_fields
    assert "removed_field" not in flex_fields
    assert len(flex_fields) == 1


def test_get_registered_flex_fields_household(
    flex_mixin: HandleFlexFieldsMixin,
    household_flex_field: FlexibleAttribute,
) -> None:
    flex_fields = flex_mixin.get_registered_flex_fields(FlexibleAttribute.ASSOCIATED_WITH_HOUSEHOLD)

    assert "household_field" in flex_fields
    assert len(flex_fields) == 1


@pytest.fixture
def create_additional_individual_flex_field() -> Callable[[], FlexibleAttribute]:
    def _create() -> FlexibleAttribute:
        return FlexibleAttributeFactory(
            name="new_field_i_f",
            label={"English(EN)": "New Field"},
            type=FlexibleAttribute.STRING,
            associated_with=FlexibleAttribute.ASSOCIATED_WITH_INDIVIDUAL,
        )

    return _create


def test_get_registered_flex_fields_caching(
    flex_mixin: HandleFlexFieldsMixin,
    individual_flex_field: FlexibleAttribute,
    create_additional_individual_flex_field: Callable[[], FlexibleAttribute],
) -> None:
    flex_fields_1 = flex_mixin.get_registered_flex_fields(FlexibleAttribute.ASSOCIATED_WITH_INDIVIDUAL)

    create_additional_individual_flex_field()

    flex_fields_2 = flex_mixin.get_registered_flex_fields(FlexibleAttribute.ASSOCIATED_WITH_INDIVIDUAL)

    assert flex_fields_1 == flex_fields_2
    assert "new_field" not in flex_fields_2


def test_get_matching_flex_fields(
    flex_mixin: HandleFlexFieldsMixin,
    individual_flex_field: FlexibleAttribute,
) -> None:
    candidates = {"custom_field", "unknown_field", "full_name"}

    matching = flex_mixin.get_matching_flex_fields(candidates, FlexibleAttribute.ASSOCIATED_WITH_INDIVIDUAL)

    assert matching == {"custom_field"}


def test_handle_individual_flex_fields_extracts_matching(
    flex_mixin: HandleFlexFieldsMixin,
    individual_flex_field: FlexibleAttribute,
) -> None:
    raw_data = {
        "full_name": "John Doe",
        "custom_field": "custom_value",
        "unknown_field": "unknown_value",
    }

    flex_mixin.handle_individual_flex_fields(raw_data)

    assert "custom_field" not in raw_data
    assert raw_data["flex_fields"] == {"custom_field": "custom_value"}
    assert "full_name" in raw_data
    assert "unknown_field" in raw_data


def test_handle_household_flex_fields_extracts_matching(
    flex_mixin: HandleFlexFieldsMixin,
    household_flex_field: FlexibleAttribute,
) -> None:
    raw_data = {
        "size": 5,
        "household_field": "household_value",
        "unknown_field": "unknown_value",
    }

    flex_mixin.handle_household_flex_fields(raw_data)

    assert "household_field" not in raw_data
    assert raw_data["flex_fields"] == {"household_field": "household_value"}
    assert "size" in raw_data
    assert "unknown_field" in raw_data


def test_handle_flex_fields_preserves_reserved_fields(
    flex_mixin: HandleFlexFieldsMixin,
    individual_flex_field: FlexibleAttribute,
) -> None:
    raw_data = {
        "full_name": "John Doe",
        "custom_field": "custom_value",
        "documents": [],
    }

    flex_mixin.handle_individual_flex_fields(raw_data, reserved_fields={"documents"})

    assert "documents" in raw_data
    assert raw_data["flex_fields"] == {"custom_field": "custom_value"}


def test_handle_flex_fields_skips_when_flex_fields_already_present(
    flex_mixin: HandleFlexFieldsMixin,
    individual_flex_field: FlexibleAttribute,
) -> None:
    raw_data = {
        "full_name": "John Doe",
        "custom_field": "custom_value",
        "flex_fields": {"existing_field": "existing_value"},
    }

    flex_mixin.handle_individual_flex_fields(raw_data)

    assert raw_data["flex_fields"] == {"existing_field": "existing_value"}
    assert "custom_field" in raw_data


def test_handle_flex_fields_empty_raw_data(
    flex_mixin: HandleFlexFieldsMixin,
) -> None:
    raw_data = {}

    flex_mixin.handle_individual_flex_fields(raw_data)

    assert raw_data["flex_fields"] == {}


@pytest.fixture
def base64_image_data() -> str:
    image = Path(__file__).parent / "logo.png"
    return base64.b64encode(image.read_bytes()).decode("utf-8")


@pytest.fixture
def image_flex_mixin() -> ImageFlexFieldMixin:
    mixin = ImageFlexFieldMixin()

    yield mixin

    for path in mixin.saved_paths:
        with contextlib.suppress(Exception):
            default_storage.delete(path)


@pytest.fixture
def image_flex_individual() -> FlexibleAttribute:
    return FlexibleAttributeFactory(
        name="custom_image_i_f",
        label={"English(EN)": "Custom Image"},
        type=FlexibleAttribute.IMAGE,
        associated_with=FlexibleAttribute.ASSOCIATED_WITH_INDIVIDUAL,
    )


@pytest.fixture
def string_flex_individual() -> FlexibleAttribute:
    return FlexibleAttributeFactory(
        name="custom_string_i_f",
        label={"English(EN)": "Custom String"},
        type=FlexibleAttribute.STRING,
        associated_with=FlexibleAttribute.ASSOCIATED_WITH_INDIVIDUAL,
    )


@pytest.fixture
def image_flex_household() -> FlexibleAttribute:
    return FlexibleAttributeFactory(
        name="household_image_h_f",
        label={"English(EN)": "Household Image"},
        type=FlexibleAttribute.IMAGE,
        associated_with=FlexibleAttribute.ASSOCIATED_WITH_HOUSEHOLD,
    )


def test_get_image_flex_fields_individual(
    image_flex_mixin: ImageFlexFieldMixin,
    image_flex_individual: FlexibleAttribute,
    string_flex_individual: FlexibleAttribute,
) -> None:
    image_fields = image_flex_mixin.get_image_flex_fields(FlexibleAttribute.ASSOCIATED_WITH_INDIVIDUAL)

    assert "custom_image" in image_fields
    assert "custom_string" not in image_fields


def test_get_image_flex_fields_household(
    image_flex_mixin: ImageFlexFieldMixin,
    image_flex_household: FlexibleAttribute,
    image_flex_individual: FlexibleAttribute,
) -> None:
    image_fields = image_flex_mixin.get_image_flex_fields(FlexibleAttribute.ASSOCIATED_WITH_HOUSEHOLD)

    assert "household_image" in image_fields
    assert "custom_image" not in image_fields


def test_process_image_flex_fields_saves_file_and_updates_value(
    image_flex_mixin: ImageFlexFieldMixin,
    image_flex_individual: FlexibleAttribute,
    string_flex_individual: FlexibleAttribute,
    base64_image_data: str,
) -> None:
    flex_fields = {
        "custom_image": base64_image_data,
        "custom_string": "some text",
    }

    saved_paths = image_flex_mixin.process_image_flex_fields(
        flex_fields,
        FlexibleAttribute.ASSOCIATED_WITH_INDIVIDUAL,
        "test_prefix",
    )
    image_flex_mixin.saved_paths.extend(saved_paths)

    assert len(saved_paths) == 1
    assert flex_fields["custom_image"] == saved_paths[0]
    assert not flex_fields["custom_image"].startswith(base64_image_data[:20])
    assert default_storage.exists(saved_paths[0])
    assert flex_fields["custom_string"] == "some text"


def test_process_image_flex_fields_empty_value_skipped(
    image_flex_mixin: ImageFlexFieldMixin,
    image_flex_individual: FlexibleAttribute,
    string_flex_individual: FlexibleAttribute,
) -> None:
    flex_fields = {
        "custom_image": "",
        "custom_string": "some text",
    }

    saved_paths = image_flex_mixin.process_image_flex_fields(
        flex_fields,
        FlexibleAttribute.ASSOCIATED_WITH_INDIVIDUAL,
        "test_prefix",
    )

    assert len(saved_paths) == 0
    assert flex_fields["custom_image"] == ""


def test_process_image_flex_fields_none_flex_fields(
    image_flex_mixin: ImageFlexFieldMixin,
    image_flex_individual: FlexibleAttribute,
) -> None:
    saved_paths = image_flex_mixin.process_image_flex_fields(
        None,
        FlexibleAttribute.ASSOCIATED_WITH_INDIVIDUAL,
        "test_prefix",
    )

    assert saved_paths == []


@pytest.fixture
def saved_image_path(
    image_flex_mixin: ImageFlexFieldMixin,
    image_flex_individual: FlexibleAttribute,
    base64_image_data: str,
) -> str:
    flex_fields = {"custom_image": base64_image_data}
    saved_paths = image_flex_mixin.process_image_flex_fields(
        flex_fields,
        FlexibleAttribute.ASSOCIATED_WITH_INDIVIDUAL,
        "test_prefix",
    )
    image_flex_mixin.saved_paths.extend(saved_paths)
    return saved_paths[0]


def test_cleanup_deletes_saved_files(
    saved_image_path: str,
) -> None:
    assert default_storage.exists(saved_image_path)

    default_storage.delete(saved_image_path)

    assert not default_storage.exists(saved_image_path)


def test_get_image_flex_fields_cache_reused(
    image_flex_mixin: ImageFlexFieldMixin,
    image_flex_individual: FlexibleAttribute,
) -> None:
    result1 = image_flex_mixin.get_image_flex_fields(FlexibleAttribute.ASSOCIATED_WITH_INDIVIDUAL)
    result2 = image_flex_mixin.get_image_flex_fields(FlexibleAttribute.ASSOCIATED_WITH_INDIVIDUAL)

    assert result1 is result2


def test_process_image_flex_fields_non_string_value_skipped(
    image_flex_mixin: ImageFlexFieldMixin,
    image_flex_individual: FlexibleAttribute,
) -> None:
    flex_fields = {
        "custom_image": 12345,
    }

    saved_paths = image_flex_mixin.process_image_flex_fields(
        flex_fields,
        FlexibleAttribute.ASSOCIATED_WITH_INDIVIDUAL,
        "test_prefix",
    )

    assert len(saved_paths) == 0
    assert flex_fields["custom_image"] == 12345


def test_process_image_flex_fields_get_photo_returns_none(
    image_flex_mixin: ImageFlexFieldMixin,
    image_flex_individual: FlexibleAttribute,
) -> None:
    empty_data_uri = "data:;base64,"
    flex_fields = {
        "custom_image": empty_data_uri,
    }

    saved_paths = image_flex_mixin.process_image_flex_fields(
        flex_fields,
        FlexibleAttribute.ASSOCIATED_WITH_INDIVIDUAL,
        "test_prefix",
    )

    assert len(saved_paths) == 0
    assert flex_fields["custom_image"] == empty_data_uri
