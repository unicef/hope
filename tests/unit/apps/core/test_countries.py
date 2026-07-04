import pytest

from hope.apps.core.countries import Countries, SanctionListCountries


def test_countries_get_choices_alpha2_returns_alpha2_values() -> None:
    choices = Countries.get_choices(output_code="alpha2")

    assert {"label": {"English(EN)": "Afghanistan"}, "value": "AF"} in choices


def test_countries_get_choices_alpha3_returns_alpha3_values() -> None:
    choices = Countries.get_choices(output_code="alpha3")

    assert {"label": {"English(EN)": "Afghanistan"}, "value": "AFG"} in choices


def test_countries_get_choices_invalid_output_code_raises_value_error() -> None:
    with pytest.raises(ValueError, match="output_code have to be one of: alpha2, alpha3"):
        Countries.get_choices(output_code="alpha4")


def test_countries_is_valid_country_choice_known_returns_true() -> None:
    assert Countries.is_valid_country_choice("AFG") is True


def test_countries_is_valid_country_choice_is_case_insensitive() -> None:
    assert Countries.is_valid_country_choice("afg") is True


def test_countries_is_valid_country_choice_unknown_returns_false() -> None:
    assert Countries.is_valid_country_choice("XXX") is False


def test_countries_get_country_value_name_output() -> None:
    assert Countries.get_country_value("AF", output_type="name") == "Afghanistan"


def test_countries_get_country_value_alpha2_output() -> None:
    assert Countries.get_country_value("AFG", output_type="alpha2") == "AF"


def test_countries_get_country_value_alpha3_output() -> None:
    assert Countries.get_country_value("AF", output_type="alpha3") == "AFG"


def test_countries_get_country_value_invalid_output_type_raises_value_error() -> None:
    with pytest.raises(ValueError, match="output_type have to be one of: name, alpha2, alpha3"):
        Countries.get_country_value("AF", output_type="alpha4")


def test_countries_get_country_value_unknown_input_returns_none() -> None:
    assert Countries.get_country_value("XXX", output_type="alpha2") is None


def test_sanction_list_countries_get_choices_alpha2_returns_alpha2_values() -> None:
    choices = SanctionListCountries.get_choices(output_code="alpha2")

    assert {"label": {"English(EN)": "Afghanistan"}, "value": "AF"} in choices


def test_sanction_list_countries_get_choices_alpha3_returns_alpha3_values() -> None:
    choices = SanctionListCountries.get_choices(output_code="alpha3")

    assert {"label": {"English(EN)": "Afghanistan"}, "value": "AFG"} in choices


def test_sanction_list_countries_get_choices_invalid_output_code_raises_value_error() -> None:
    with pytest.raises(ValueError, match="output_code have to be one of: alpha2, alpha3"):
        SanctionListCountries.get_choices(output_code="alpha4")


def test_sanction_list_countries_is_valid_country_choice_known_returns_true() -> None:
    assert SanctionListCountries.is_valid_country_choice("AFG") is True


def test_sanction_list_countries_is_valid_country_choice_is_case_insensitive() -> None:
    assert SanctionListCountries.is_valid_country_choice("afg") is True


def test_sanction_list_countries_is_valid_country_choice_unknown_returns_false() -> None:
    assert SanctionListCountries.is_valid_country_choice("XXX") is False


def test_sanction_list_countries_get_country_value_name_output() -> None:
    assert SanctionListCountries.get_country_value("AF", output_type="name") == "Afghanistan"


def test_sanction_list_countries_get_country_value_alpha2_output() -> None:
    assert SanctionListCountries.get_country_value("AFG", output_type="alpha2") == "AF"


def test_sanction_list_countries_get_country_value_alpha3_output() -> None:
    assert SanctionListCountries.get_country_value("AF", output_type="alpha3") == "AFG"


def test_sanction_list_countries_get_country_value_invalid_output_type_raises_value_error() -> None:
    with pytest.raises(ValueError, match="output_type have to be one of: name, alpha2, alpha3"):
        SanctionListCountries.get_country_value("AF", output_type="alpha4")


def test_sanction_list_countries_get_country_value_unknown_input_returns_none() -> None:
    assert SanctionListCountries.get_country_value("XXX", output_type="alpha2") is None
