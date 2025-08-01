from datetime import date, datetime

from rest_framework.exceptions import ValidationError

from hct_mis_api.apps.household.models import HEAD, ROLE_PRIMARY, ROLE_ALTERNATE


class BirthDateValidator:
    def __call__(self, value: date) -> None:
        if value >= datetime.today().date():
            raise ValidationError("Birth date must be in the past")


class HouseholdValidator:
    def __call__(self, value: Any) -> None:  # noqa
        head_of_household = None
        alternate_collector = None
        primary_collector = None
        members = value.get("members", [])
        errs = {}
        if not members:
            raise ValidationError({"members": "This field is required"})
        for data in members:
            rel = data.get("relationship", None)
            role = data.get("role", None)
            if rel == HEAD:
                if head_of_household:
                    errs["head_of_household"] = "Only one HoH allowed"
                head_of_household = data
            if role == ROLE_PRIMARY:
                if primary_collector:
                    errs["primary_collector"] = "Only one Primary Collector allowed"
                primary_collector = data
            elif role == ROLE_ALTERNATE:
                if alternate_collector:
                    errs["alternate_collector"] = "Only one Alternate Collector allowed"
                alternate_collector = data
        if not head_of_household:
            errs["head_of_household"] = "Missing Head Of Household"
        if not primary_collector:
            errs["primary_collector"] = "Missing Primary Collector"
        if errs:
            raise ValidationError(errs)
