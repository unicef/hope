from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from hct_mis_api.apps.household.models import Individual
from hct_mis_api.apps.household.serializers import IndividualSerializer
from rest_framework.response import Response

class IndividualView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):       
        # TODO
        return Response(IndividualSerializer(Individual.objects.first(), many=False).data, status=200)
