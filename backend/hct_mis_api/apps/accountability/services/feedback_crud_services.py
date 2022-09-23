from django.contrib.auth import get_user_model
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.core.utils import decode_id_string
from hct_mis_api.apps.accountability.models import Feedback
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.household.models import Household, Individual
from hct_mis_api.apps.geo.models import Area
from django.shortcuts import get_object_or_404

User = get_user_model()


class FeedbackCrudServices:
    @classmethod
    def create(cls, user: User, input_data: dict) -> Feedback:
        obj = Feedback(
            business_area=BusinessArea.objects.get(slug=input_data["business_area_slug"]),
            issue_type=input_data["issue_type"],
            description=input_data["description"],
        )
        if input_data.get("household_lookup"):
            obj.household_lookup = get_object_or_404(Household, id=decode_id_string(input_data["household_lookup"]))
        if input_data.get("individual_lookup"):
            obj.individual_lookup = get_object_or_404(Individual, id=decode_id_string(input_data["individual_lookup"]))
        if input_data.get("comments"):
            obj.comments = input_data["comments"]
        if input_data.get("admin2"):
            obj.admin2 = get_object_or_404(Area, id=decode_id_string(input_data["admin2"]))
        if input_data.get("area"):
            obj.area = input_data["area"]
        if input_data.get("language"):
            obj.language = input_data["language"]
        if input_data.get("consent"):
            obj.consent = input_data["consent"]
        if input_data.get("program"):
            obj.program = get_object_or_404(Program, id=decode_id_string(input_data["program"]))
        obj.save()
        return obj
