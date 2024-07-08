from rest_framework.generics import get_object_or_404

from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.utils import decode_id_string
from hct_mis_api.apps.program.models import Program


class BusinessAreaMixin:
    def get_business_area(self) -> BusinessArea:
        return get_object_or_404(BusinessArea, slug=self.kwargs.get("business_area"))


class ProgramMixin:
    def get_program(self) -> Program:
        return get_object_or_404(Program, id=decode_id_string(self.kwargs.get("program_id")))


class BusinessAreaProgramMixin(BusinessAreaMixin, ProgramMixin):
    pass


class ActionMixin:
    permission_classes_by_action = {}
    serializer_classes_by_action = {}

    def get_permissions(self):
        if self.action in self.permission_classes_by_action:
            return [permission() for permission in self.permission_classes_by_action[self.action]]
        else:
            return super().get_permissions()

    def get_serializer_class(self):
        if self.action in self.serializer_classes_by_action:
            return self.serializer_classes_by_action[self.action]
        else:
            return super().get_serializer_class()
