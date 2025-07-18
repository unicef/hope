import logging
from typing import Dict, Optional, Union

from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from hct_mis_api.apps.core.utils import IDENTIFICATION_TYPE_TO_KEY_MAPPING
from hct_mis_api.apps.household.filters import _prepare_kobo_asset_id_value
from hct_mis_api.apps.household.models import (
    IDENTIFICATION_TYPE_TAX_ID,
    Household,
    PendingDocument,
    PendingHousehold,
    PendingIndividual,
)
from hct_mis_api.apps.household.serializers import (
    serialize_by_household,
    serialize_by_individual,
)
from hct_mis_api.apps.utils.profiling import profiling

logger = logging.getLogger(__name__)


def get_individual(tax_id: str, business_area_code: Optional[str]) -> PendingIndividual:
    pending_documents = (
        PendingDocument.objects.all()
        if not business_area_code
        else PendingDocument.objects.filter(
            individual__household__registration_data_import__business_area__code=business_area_code
        )
    ).filter(type__key=IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_TAX_ID], document_number=tax_id)
    if pending_documents.count() > 1:
        raise ValidationError(f"Multiple imported documents ({pending_documents.count()}) with given tax_id found")
    if pending_documents.count() == 1:
        return pending_documents.first().individual
    raise NotFound(f"Document with given tax_id: {tax_id} not found")


def get_household(detail_id: str, business_area_code: Optional[str]) -> Union[PendingHousehold, Household]:
    kobo_asset_value = _prepare_kobo_asset_id_value(detail_id)

    households = Household.objects.filter(detail_id__endswith=kobo_asset_value)
    if business_area_code:
        households = households.filter(business_area__code=business_area_code)
    if households.count() > 1:
        raise ValidationError(f"Multiple households ({households.count()}) with given detail_id found")
    if households.count() == 1:
        return households.first()  # type: ignore

    imported_households = PendingHousehold.objects.filter(detail_id__endswith=kobo_asset_value)
    if business_area_code:
        imported_households = imported_households.filter(business_area__code=business_area_code)
    if imported_households.count() > 1:
        raise ValidationError(
            f"Multiple imported households ({imported_households.count()}) with given detail_id found"
        )
    if imported_households.count() == 1:
        return imported_households.first()

    raise NotFound(f"Household with given detail_id: {detail_id} not found")


def get_household_or_individual(
    tax_id: Optional[str], detail_id: Optional[str], business_area_code: Optional[str]
) -> Dict:
    if tax_id and detail_id:
        raise ValidationError("Tax id and detail_id are mutually exclusive")

    if tax_id:
        individual = get_individual(tax_id, business_area_code)
        return serialize_by_individual(individual, tax_id)

    if detail_id:
        household = get_household(detail_id, business_area_code)
        return serialize_by_household(household)

    raise ValidationError("tax_id or detail_id is required")


class HouseholdStatusView(APIView):
    permission_classes = (IsAuthenticated,)

    @profiling(name="Household status")
    def get(self, request: Request) -> Response:
        query_params = request.query_params

        tax_id = query_params.get("tax_id", None)
        detail_id = query_params.get("detail_id", None)
        business_area_code: Optional[str] = query_params.get("business_area_code")

        data = get_household_or_individual(tax_id, detail_id, business_area_code)

        return Response(data, status=200)
