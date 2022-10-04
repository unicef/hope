from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.household.filters import _prepare_kobo_asset_id_value
from hct_mis_api.apps.household.models import (
    IDENTIFICATION_TYPE_TAX_ID,
    Document,
    Household,
)
from hct_mis_api.apps.household.serializers import (
    serialize_by_household,
    serialize_by_individual,
)
from hct_mis_api.apps.registration_datahub.models import (
    ImportedDocument,
    ImportedHousehold,
)
from hct_mis_api.apps.utils.profiling import profiling


def get_individual(tax_id, business_area_code):
    documents = (
        Document.objects.all()
        if not business_area_code
        else Document.objects.filter(individual__household__business_area__code=business_area_code)
    ).filter(type__type=IDENTIFICATION_TYPE_TAX_ID, document_number=tax_id)
    if documents.count() > 1:
        raise Exception(f"Multiple documents ({documents.count()}) with given tax_id found")
    if documents.count() == 1:
        return documents.first().individual

    imported_documents = (
        ImportedDocument.objects.all()
        if not business_area_code
        else ImportedDocument.objects.filter(
            individual__household__registration_data_import__business_area__code=business_area_code
        )
    ).filter(type__type=IDENTIFICATION_TYPE_TAX_ID, document_number=tax_id)
    if imported_documents.count() > 1:
        raise Exception(f"Multiple imported documents ({imported_documents.count()}) with given tax_id found")
    if imported_documents.count() == 1:
        return imported_documents.first().individual
    raise Exception("Document with given tax_id not found")


def get_household(registration_id, business_area_code):
    kobo_asset_value = _prepare_kobo_asset_id_value(registration_id)
    households = (
        Household.objects.all()
        if not business_area_code
        else Household.objects.filter(business_area__code=business_area_code)
    ).filter(kobo_asset_id__endswith=kobo_asset_value)
    if households.count() > 1:
        raise Exception(f"Multiple households ({households.count()}) with given registration_id found")
    if households.count() == 1:
        return households.first()

    if business_area_code is None:
        imported_households_by_business_area = ImportedHousehold.objects.all()
    else:
        business_areas = BusinessArea.objects.filter(code=business_area_code)
        if not business_areas:
            raise Exception(f"Business area with code {business_area_code} not found")
        business_area = business_areas.first()  # code is unique, so no need to worry here
        imported_households_by_business_area = ImportedHousehold.objects.filter(
            registration_data_import__business_area_slug=business_area.slug
        )

    imported_households = imported_households_by_business_area.filter(kobo_asset_id__endswith=kobo_asset_value)
    if imported_households.count() > 1:
        raise Exception(
            f"Multiple imported households ({imported_households.count()}) with given registration_id found"
        )
    if imported_households.count() == 1:
        return imported_households.first()
    raise Exception("Household with given registration_id not found")


def get_household_or_individual(tax_id, registration_id, business_area_code):
    if tax_id and registration_id:
        raise Exception("tax_id and registration_id are mutually exclusive")

    if not (tax_id or registration_id):
        raise Exception("tax_id or registration_id is required")

    if tax_id:
        individual = get_individual(tax_id, business_area_code)
        return serialize_by_individual(individual, tax_id)

    if registration_id:
        household = get_household(registration_id, business_area_code)
        return serialize_by_household(household)


class HouseholdStatusView(APIView):
    permission_classes = (IsAuthenticated,)

    @profiling(name="Household status")
    def get(self, request):
        query_params = request.query_params

        tax_id = query_params.get("tax_id", None)
        registration_id = query_params.get("registration_id", None)
        business_area_code = query_params.get("business_area_code", None)

        try:
            data = get_household_or_individual(tax_id, registration_id, business_area_code)
        except Exception as exception:
            return Response({"status": "not found", "error_message": str(exception)}, status=404)

        return Response(data, status=200)
