import pytest

from hope.apps.registration_data.value_caster import SelectOneValueCaster


class TestSelectOneValueCaster:
    @pytest.fixture
    def caster(self):
        return SelectOneValueCaster()

    @pytest.fixture
    def field(self):
        return {
            "type": "SELECT_ONE",
            "xlsx_field": "test_field",
            "choices": [{"value": "A"}, {"value": "B"}],
        }

    def test_process_value_in_choices(self, caster, field):
        assert caster.process(field, "A") == "A"

    def test_process_value_not_in_choices_converts_to_int(self, caster, field):
        assert caster.process(field, "123") == 123

    def test_process_value_not_in_choices_returns_string(self, caster, field):
        assert caster.process(field, "not_a_number") == "not_a_number"

    def test_process_value_with_whitespace(self, caster, field):
        assert caster.process(field, "  A  ") == "A"

    def test_process_value_uppercase_match(self, caster, field):
        field["choices"] = [{"value": "VALID"}]
        assert caster.process(field, "valid") == "VALID"
