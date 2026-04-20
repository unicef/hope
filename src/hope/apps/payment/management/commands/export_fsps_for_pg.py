from argparse import ArgumentParser
import json
from pathlib import Path
from typing import Any

from django.core.management import BaseCommand
from django.utils import timezone

from hope.models import (
    FinancialServiceProvider,
)


class Command(BaseCommand):
    help = "Export HOPE FSP data as a Python structure for Payment Gateway."

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            "--output",
            type=str,
            help="Optional file path to write the exported Python structure.",
        )

    @staticmethod
    def _serialize_country(country: Any) -> dict[str, str] | None:
        if not country:
            return None
        return {
            "iso_code2": country.iso_code2,
            "iso_code3": country.iso_code3,
            "name": country.name,
        }

    def _serialize_fsp(self, fsp: FinancialServiceProvider) -> dict[str, Any]:
        allowed_business_areas = sorted(
            fsp.allowed_business_areas.all(),
            key=lambda business_area: business_area.slug,
        )
        delivery_mechanisms = sorted(
            fsp.delivery_mechanisms.all(),
            key=lambda delivery_mechanism: delivery_mechanism.code,
        )
        names_mappings = sorted(
            fsp.names_mappings.all(),
            key=lambda mapping: (mapping.source, mapping.external_name),
        )

        return {
            "name": fsp.name,
            "vision_vendor_number": fsp.vision_vendor_number,
            "communication_channel": fsp.communication_channel,
            "distribution_limit": str(fsp.distribution_limit) if fsp.distribution_limit is not None else None,
            "payment_gateway_id": fsp.payment_gateway_id,
            "data_transfer_configuration": fsp.data_transfer_configuration,
            "allowed_business_areas": [
                {
                    "slug": business_area.slug,
                    "name": business_area.name,
                }
                for business_area in allowed_business_areas
            ],
            "delivery_mechanisms": [
                {
                    "code": delivery_mechanism.code,
                    "name": delivery_mechanism.name,
                }
                for delivery_mechanism in delivery_mechanisms
            ],
            "delivery_mechanism_configs": [
                {
                    "delivery_mechanism": {
                        "code": config.delivery_mechanism.code,
                        "name": config.delivery_mechanism.name,
                    },
                    "country": self._serialize_country(config.country),
                    "required_fields": list(config.required_fields),
                }
                for config in fsp.deliverymechanismconfig_set.all()
            ],
            "names_mappings": [
                {
                    "external_name": mapping.external_name,
                    "hope_name": mapping.hope_name,
                    "source": mapping.source,
                }
                for mapping in names_mappings
            ],
            "financial_institution_mappings": [
                {
                    "financial_institution": {
                        "name": mapping.financial_institution.name,
                    },
                    "code": mapping.code,
                }
                for mapping in fsp.financialinstitutionmapping_set.all()
            ],
        }

    def _get_export_payload(self) -> dict[str, Any]:
        fsps = FinancialServiceProvider.objects.prefetch_related(
            "allowed_business_areas",
            "delivery_mechanisms",
            "names_mappings",
            "deliverymechanismconfig_set",
            "financialinstitutionmapping_set",
        ).order_by("name")
        return {
            "generated_at": timezone.now().isoformat(),
            "fsps": [self._serialize_fsp(fsp) for fsp in fsps],
        }

    def handle(self, *args: Any, **options: Any) -> None:
        payload = self._get_export_payload()
        rendered_payload = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"

        if output_path := options.get("output"):
            Path(output_path).write_text(rendered_payload, encoding="utf-8")
            self.stdout.write(self.style.SUCCESS(f"FSP export written to {output_path}"))
            return
