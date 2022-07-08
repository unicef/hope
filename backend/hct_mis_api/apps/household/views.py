from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from hct_mis_api.apps.household.models import Individual, IDENTIFICATION_TYPE_TAX_ID, Document, Household
from hct_mis_api.apps.household.serializers import IndividualStatusSerializer, HouseholdStatusSerializer
from hct_mis_api.apps.household.filters import _prepare_kobo_asset_id_value
from rest_framework.response import Response


def get_individual(tax_id):
    documents = Document.objects.filter(type__type=IDENTIFICATION_TYPE_TAX_ID, document_number=tax_id).distinct()
    if documents.count() == 0:
        raise Exception("Document with given tax_id not found")
    if documents.count() > 1:
        raise Exception(f"Multiple documents ({documents.count()}) with given tax_id found")
    return documents.first().individual


def get_household(registration_id):
    kobo_asset_value = _prepare_kobo_asset_id_value(registration_id)
    households = Household.objects.filter(kobo_asset_id__endswith=kobo_asset_value).distinct()
    if households.count() == 0:
        raise Exception("Household with given registration_id not found")
    if households.count() > 1:
        raise Exception(f"Multiple households ({households.count()}) with given registration_id found")
    return households.first()


def get_household_or_individual(tax_id, registration_id):
    if tax_id and registration_id:
        raise Exception("tax_id and registration_id are mutually exclusive")

    if not (tax_id or registration_id):
        raise Exception("tax_id or registration_id is required")

    if tax_id:
        return {"individual": IndividualStatusSerializer(get_individual(tax_id), many=False).data}

    if registration_id:
        return {"household": HouseholdStatusSerializer(get_household(registration_id), many=False).data}


class DetailsView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        query_params = request.query_params

        tax_id = query_params.get("tax_id")
        registration_id = query_params.get("registration_id")

        try:
            data = get_household_or_individual(tax_id, registration_id)
        except Exception as exception:
            return Response({"error": str(exception)}, status=400)

        return Response(data, status=200)
