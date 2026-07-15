import pytest

from hope.apps.core.countries import Countries, SanctionListCountries

country_classes = pytest.mark.parametrize("country_class", [Countries, SanctionListCountries])


@country_classes
def test_get_choices_alpha2_returns_alpha2_values(country_class: type) -> None:
    choices = country_class.get_choices(output_code="alpha2")

    assert {"label": {"English(EN)": "Afghanistan"}, "value": "AF"} in choices


@country_classes
def test_get_choices_alpha3_returns_alpha3_values(country_class: type) -> None:
    choices = country_class.get_choices(output_code="alpha3")

    assert {"label": {"English(EN)": "Afghanistan"}, "value": "AFG"} in choices


@country_classes
def test_get_choices_invalid_output_code_raises_value_error(country_class: type) -> None:
    with pytest.raises(ValueError, match="output_code have to be one of: alpha2, alpha3"):
        country_class.get_choices(output_code="alpha4")


@country_classes
def test_is_valid_country_choice_known_returns_true(country_class: type) -> None:
    assert country_class.is_valid_country_choice("AFG") is True


@country_classes
def test_is_valid_country_choice_is_case_insensitive(country_class: type) -> None:
    assert country_class.is_valid_country_choice("afg") is True


@country_classes
def test_is_valid_country_choice_unknown_returns_false(country_class: type) -> None:
    assert country_class.is_valid_country_choice("XXX") is False


@country_classes
def test_get_country_value_name_output(country_class: type) -> None:
    assert country_class.get_country_value("AF", output_type="name") == "Afghanistan"


@country_classes
def test_get_country_value_alpha2_output(country_class: type) -> None:
    assert country_class.get_country_value("AFG", output_type="alpha2") == "AF"


@country_classes
def test_get_country_value_alpha3_output(country_class: type) -> None:
    assert country_class.get_country_value("AF", output_type="alpha3") == "AFG"


@country_classes
def test_get_country_value_invalid_output_type_raises_value_error(country_class: type) -> None:
    with pytest.raises(ValueError, match="output_type have to be one of: name, alpha2, alpha3"):
        country_class.get_country_value("AF", output_type="alpha4")


@country_classes
def test_get_country_value_unknown_input_returns_none(country_class: type) -> None:
    assert country_class.get_country_value("XXX", output_type="alpha2") is None
