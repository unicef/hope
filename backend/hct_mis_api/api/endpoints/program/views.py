from rest_framework.generics import ListAPIView

from hct_mis_api.api.endpoints.base import HOPEAPIView
from hct_mis_api.api.endpoints.program.serializers import ProgramGlobalSerializer
from hct_mis_api.apps.program.models import Program


class ProgramGlobalListView(HOPEAPIView, ListAPIView):
    serializer_class = ProgramGlobalSerializer
    queryset = Program.objects.all()
