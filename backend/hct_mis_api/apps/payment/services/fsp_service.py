from django.shortcuts import get_object_or_404

from hct_mis_api.apps.account.models import User
from hct_mis_api.apps.core.utils import decode_id_string
from hct_mis_api.apps.payment.models import (
    FinancialServiceProvider,
    FinancialServiceProviderXlsxTemplate,
)


class FSPService:
    @staticmethod
    def create(inputs: dict, user: User):
        fsp_xlsx_template_id = decode_id_string(inputs["fsp_xlsx_template_id"])
        fsp_xlsx_template = get_object_or_404(FinancialServiceProviderXlsxTemplate, id=fsp_xlsx_template_id)

        fsp = FinancialServiceProvider(
            name=inputs["name"],
            vision_vendor_number=inputs["vision_vendor_number"],
            distribution_limit=inputs["distribution_limit"],
            communication_channel=inputs["communication_channel"],
            fsp_xlsx_template=fsp_xlsx_template,
            created_by=user,
            delivery_mechanisms=inputs["delivery_mechanisms"],
        )
        fsp.save()

        return fsp

    @staticmethod
    def update(fsp_id: str, inputs: dict):
        fsp_xlsx_template_id = decode_id_string(inputs["fsp_xlsx_template_id"])

        fsp = get_object_or_404(FinancialServiceProvider, id=fsp_id)
        fsp_xlsx_template = get_object_or_404(FinancialServiceProviderXlsxTemplate, id=fsp_xlsx_template_id)

        fsp.name = inputs["name"]
        fsp.vision_vendor_number = inputs["vision_vendor_number"]
        fsp.distribution_limit = inputs["distribution_limit"]
        fsp.communication_channel = inputs["communication_channel"]
        fsp.fsp_xlsx_template = fsp_xlsx_template
        fsp.delivery_mechanisms = inputs["delivery_mechanisms"]
        fsp.save()

        return fsp
