from typing import Any

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import AnonymousUser
from django.shortcuts import get_object_or_404

from hope.models import Area, BusinessArea, Feedback, Household, Individual, Program

_SIMPLE_FIELDS = ("comments", "area", "language", "consent")
_FK_FIELDS = {
    "household_lookup": Household,
    "individual_lookup": Individual,
    "admin2": Area,
}


class FeedbackCrudServices:
    @staticmethod
    def _has_value(input_data: dict, key: Any) -> bool:
        return key in input_data and input_data[key] is not None and input_data[key] != ""

    @classmethod
    def _apply_fields(cls, obj: Feedback, input_data: dict) -> None:
        for field in _SIMPLE_FIELDS:
            if cls._has_value(input_data, field):
                setattr(obj, field, input_data[field])
        for field, model in _FK_FIELDS.items():
            if cls._has_value(input_data, field):
                setattr(obj, field, get_object_or_404(model, id=input_data[field]))

    @classmethod
    def validate_lookup(cls, feedback: Feedback) -> None:
        if (
            feedback.household_lookup is not None
            and feedback.individual_lookup is not None
            and feedback.household_lookup != feedback.individual_lookup.household
        ):
            raise Exception("Household lookup does not match individual lookup")

    @classmethod
    def create(
        cls,
        user: AbstractBaseUser | AnonymousUser,
        business_area: BusinessArea,
        input_data: dict,
    ) -> Feedback:
        obj = Feedback(
            business_area=business_area,
            issue_type=input_data["issue_type"],
            description=input_data["description"],
        )
        cls._apply_fields(obj, input_data)

        if obj.household_lookup:
            obj.program = obj.household_lookup.program or obj.household_lookup.programs.first()

        if not obj.program and cls._has_value(input_data, "program"):
            obj.program = get_object_or_404(Program, id=input_data["program"])
        obj.created_by = user
        cls.validate_lookup(obj)
        obj.save()
        return obj

    @classmethod
    def update(cls, feedback: Feedback, input_data: dict) -> Feedback:
        for field in ("issue_type", "description"):
            if cls._has_value(input_data, field):
                setattr(feedback, field, input_data[field])
        cls._apply_fields(feedback, input_data)
        if cls._has_value(input_data, "program"):
            feedback.program = get_object_or_404(Program, id=input_data["program"])
        cls.validate_lookup(feedback)
        feedback.save()
        return feedback
