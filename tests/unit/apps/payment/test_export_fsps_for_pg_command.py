import json
from pathlib import Path

from django.core.management import call_command
import pytest

from extras.test_utils.factories.core import BusinessAreaFactory
from extras.test_utils.factories.geo import CountryFactory
from extras.test_utils.factories.payment import (
    DeliveryMechanismFactory,
    FinancialInstitutionFactory,
    FinancialServiceProviderFactory,
)
from hope.models import DeliveryMechanismConfig, FinancialInstitutionMapping

pytestmark = pytest.mark.django_db


def test_export_fsps_for_pg_command_uses_model_field_names(tmp_path: Path) -> None:
    business_area = BusinessAreaFactory(slug="afghanistan", name="Afghanistan")
    country = CountryFactory(
        name="Afghanistan",
        short_name="Afghanistan",
        iso_code2="AF",
        iso_code3="AFG",
        iso_num="0004",
    )
    delivery_mechanism = DeliveryMechanismFactory(
        code="transfer",
        name="Transfer",
        payment_gateway_id="dm-transfer",
    )
    fsp = FinancialServiceProviderFactory(
        name="Test FSP",
        vision_vendor_number="VEN-0001",
        payment_gateway_id="pg-123",
        data_transfer_configuration={"api_key": "secret"},
        delivery_mechanisms=[delivery_mechanism],
    )
    fsp.allowed_business_areas.add(business_area)

    DeliveryMechanismConfig.objects.create(
        delivery_mechanism=delivery_mechanism,
        fsp=fsp,
        country=country,
        required_fields=["account_number"],
    )
    financial_institution = FinancialInstitutionFactory(name="Bank A")
    FinancialInstitutionMapping.objects.create(
        financial_service_provider=fsp,
        financial_institution=financial_institution,
        code="BANK_A",
    )

    output_path = tmp_path / "fsp_export.json"
    call_command("export_fsps_for_pg", "--output", str(output_path))

    payload = json.loads(output_path.read_text(encoding="utf-8"))

    assert "generated_at" in payload
    assert len(payload["fsps"]) == 1

    exported_fsp = payload["fsps"][0]
    assert exported_fsp["name"] == "Test FSP"
    assert exported_fsp["vision_vendor_number"] == "VEN-0001"
    assert exported_fsp["payment_gateway_id"] == "pg-123"

    assert exported_fsp["allowed_business_areas"] == [
        {
            "slug": "afghanistan",
            "name": "Afghanistan",
        }
    ]
    assert exported_fsp["delivery_mechanisms"] == [
        {
            "code": "transfer",
            "name": "Transfer",
        }
    ]
    assert exported_fsp["delivery_mechanism_configs"] == [
        {
            "delivery_mechanism": {
                "code": "transfer",
                "name": "Transfer",
            },
            "country": {
                "iso_code2": "AF",
                "iso_code3": "AFG",
                "name": "Afghanistan",
            },
            "required_fields": ["account_number"],
        }
    ]
    assert exported_fsp["financial_institution_mappings"] == [
        {
            "financial_institution": {
                "name": "Bank A",
            },
            "code": "BANK_A",
        }
    ]
