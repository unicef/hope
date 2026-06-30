import json
from types import SimpleNamespace

from django.core.management import call_command
import pytest

from extras.test_utils.factories import CurrencyFactory

pytestmark = pytest.mark.xdist_group(name="generate_openapi")


@pytest.fixture(scope="module")
def generated(django_db_blocker, tmp_path_factory) -> SimpleNamespace:
    output_dir = tmp_path_factory.mktemp("generate_openapi") / "deep" / "nested" / "data"

    with django_db_blocker.unblock():
        currencies = [
            CurrencyFactory(code="PLN", name="Polish Zloty"),
            CurrencyFactory(code="OLD", name="Inactive Currency", active=False),
        ]
        call_command("generate_openapi", output_dir=str(output_dir))

    yield SimpleNamespace(
        output_dir=output_dir,
        schema_path=output_dir / "openapi.yml",
        choices_path=output_dir / "choices.json",
        choices=json.loads((output_dir / "choices.json").read_text()),
    )

    with django_db_blocker.unblock():
        for currency in currencies:
            currency.delete()


def test_writes_openapi_schema_and_choices_files(generated: SimpleNamespace) -> None:
    assert generated.schema_path.exists()
    assert "openapi:" in generated.schema_path.read_text()
    assert generated.choices_path.exists()


def test_choices_cover_all_viewset_actions(generated: SimpleNamespace) -> None:
    assert set(generated.choices) == {
        "countries",
        "currencies",
        "feedback-issue-type",
        "languages",
        "payment-plan-background-action-status",
        "payment-plan-status",
        "payment-plan-type",
        "payment-record-delivery-type",
        "payment-verification-plan-sampling",
        "payment-verification-plan-status",
        "payment-verification-status",
        "payment-verification-summary-status",
        "permissions",
    }


def test_every_choice_has_value_and_name(generated: SimpleNamespace) -> None:
    assert all(isinstance(data, list) for data in generated.choices.values())
    assert all("value" in choice and "name" in choice for data in generated.choices.values() for choice in data)


@pytest.mark.parametrize(
    "endpoint",
    [
        "feedback-issue-type",
        "languages",
        "payment-plan-background-action-status",
        "payment-plan-status",
        "payment-plan-type",
        "payment-verification-plan-sampling",
        "payment-verification-plan-status",
        "payment-verification-status",
        "payment-verification-summary-status",
        "permissions",
    ],
)
def test_enum_backed_endpoints_are_populated(generated: SimpleNamespace, endpoint: str) -> None:
    assert generated.choices[endpoint]


def test_static_choices_match_model_choices(generated: SimpleNamespace) -> None:
    assert {"value": "FULL_LIST", "name": "Full list"} in generated.choices["payment-verification-plan-sampling"]


def test_db_backed_choices_reflect_database(generated: SimpleNamespace) -> None:
    codes = {choice["value"] for choice in generated.choices["currencies"]}
    assert "PLN" in codes
    assert "OLD" not in codes  # only active currencies are exposed


def test_custom_output_dir_is_created(generated: SimpleNamespace) -> None:
    assert generated.output_dir.exists()
    assert generated.schema_path.exists()
    assert generated.choices_path.exists()
