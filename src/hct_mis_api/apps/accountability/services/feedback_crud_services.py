from typing import Any

from django.contrib.auth.models import AbstractUser
from django.shortcuts import get_object_or_404

from hct_mis_api.apps.accountability.models import Feedback
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.utils import decode_id_string
from hct_mis_api.apps.geo.models import Area
from hct_mis_api.apps.household.models import Household, Individual
from hct_mis_api.apps.program.models import Program


class FeedbackCrudServices:
    @classmethod
    def validate_lookup(cls, feedback: Feedback) -> None:
        if feedback.household_lookup is not None and feedback.individual_lookup is not None:
            if feedback.household_lookup != feedback.individual_lookup.household:
                raise Exception("Household lookup does not match individual lookup")

    @classmethod
    def create(cls, user: AbstractUser, business_area: BusinessArea, input_data: dict) -> Feedback:
        def check(key: Any) -> bool:
            return key in input_data and input_data[key] is not None and input_data[key] != ""

        obj = Feedback(
            business_area=business_area,
            issue_type=input_data["issue_type"],
            description=input_data["description"],
        )
        if check("household_lookup"):
            obj.household_lookup = get_object_or_404(Household, id=decode_id_string(input_data["household_lookup"]))
        if check("individual_lookup"):
            obj.individual_lookup = get_object_or_404(Individual, id=decode_id_string(input_data["individual_lookup"]))
        if check("comments"):
            obj.comments = input_data["comments"]
        if check("admin2"):
            obj.admin2 = get_object_or_404(Area, id=decode_id_string(input_data["admin2"]))
        if check("area"):
            obj.area = input_data["area"]
        if check("language"):
            obj.language = input_data["language"]
        if check("consent"):
            obj.consent = input_data["consent"]

        if obj.household_lookup:
            obj.program = obj.household_lookup.program or obj.household_lookup.programs.first()

        if not obj.program and check("program"):
            obj.program = get_object_or_404(Program, id=decode_id_string(input_data["program"]))
        obj.created_by = user
        cls.validate_lookup(obj)
        obj.save()
        return obj

    @classmethod
    def update(cls, feedback: Feedback, input_data: dict) -> Feedback:
        def check(key: Any) -> bool:
            return key in input_data and input_data[key] is not None and input_data[key] != ""

        if check("issue_type"):
            feedback.issue_type = input_data["issue_type"]
        if check("description"):
            feedback.description = input_data["description"]
        if check("household_lookup"):
            feedback.household_lookup = get_object_or_404(
                Household, id=decode_id_string(input_data["household_lookup"])
            )
        if check("individual_lookup"):
            feedback.individual_lookup = get_object_or_404(
                Individual, id=decode_id_string(input_data["individual_lookup"])
            )
        if check("comments"):
            feedback.comments = input_data["comments"]
        if check("admin2"):
            feedback.admin2 = get_object_or_404(Area, id=decode_id_string(input_data["admin2"]))
        if check("area"):
            feedback.area = input_data["area"]
        if check("language"):
            feedback.language = input_data["language"]
        if check("consent"):
            feedback.consent = input_data["consent"]
        if check("program"):
            feedback.program = get_object_or_404(Program, id=decode_id_string(input_data["program"]))
        cls.validate_lookup(feedback)
        feedback.save()
        return feedback
