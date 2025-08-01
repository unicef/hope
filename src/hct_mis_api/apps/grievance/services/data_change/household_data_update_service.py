from datetime import date, datetime
from typing import Any

from django.contrib.auth.models import AbstractUser
from django.shortcuts import get_object_or_404

from django_countries.fields import Country

from hct_mis_api.apps.activity_log.models import log_create
from hct_mis_api.apps.activity_log.utils import copy_model_object
from hct_mis_api.apps.core.utils import to_snake_case
from hct_mis_api.apps.geo import models as geo_models
from hct_mis_api.apps.geo.models import Area
from hct_mis_api.apps.grievance.models import (
    GrievanceTicket,
    TicketHouseholdDataUpdateDetails,
)
from hct_mis_api.apps.grievance.services.data_change.data_change_service import (
    DataChangeService,
)
from hct_mis_api.apps.grievance.services.data_change.utils import (
    cast_flex_fields,
    handle_role,
    is_approved,
    to_date_string,
    verify_flex_fields,
)
from hct_mis_api.apps.household.models import Household, Individual
from hct_mis_api.apps.household.services.household_recalculate_data import (
    recalculate_data,
)


def _prepare_roles_with_approve_status(roles_data: list[dict[Any, Any]]) -> list[dict[str, Any]]:
    roles_with_approve_status = []
    for role in roles_data:
        individual = role["individual"]
        roles_with_approve_status.append(
            {
                "value": role["new_role"],
                "approve_status": False,
                "previous_value": individual.role,
                "individual_id": str(individual.pk),
                "full_name": individual.full_name,
                "unicef_id": individual.unicef_id,
            }
        )
    return roles_with_approve_status


class HouseholdDataUpdateService(DataChangeService):
    def save(self) -> list[GrievanceTicket]:
        data_change_extras = self.extras.get("issue_type")
        household_data_update_issue_type_extras = data_change_extras.get("household_data_update_issue_type_extras")
        household = household_data_update_issue_type_extras.get("household")
        household_data = household_data_update_issue_type_extras.get("household_data", {})
        roles = household_data.pop("roles", [])
        to_date_string(household_data, "start")
        to_date_string(household_data, "end")
        flex_fields = {to_snake_case(field): value for field, value in household_data.pop("flex_fields", {}).items()}
        verify_flex_fields(flex_fields, "households")
        household_data_with_approve_status = {
            to_snake_case(field): {"value": value, "approve_status": False} for field, value in household_data.items()
        }
        for field in household_data_with_approve_status:
            current_value = getattr(household, field, None)
            if isinstance(current_value, datetime | date):
                current_value = current_value.isoformat()
            if isinstance(current_value, Country):
                current_value = current_value.alpha3
            if isinstance(current_value, geo_models.Country):
                current_value = current_value.iso_code3
            household_data_with_approve_status[field]["previous_value"] = current_value

        if admin_area_title := household_data_with_approve_status.get("admin_area_title"):
            area = getattr(household, "admin_area", None)
            current_value = getattr(area, "p_code", None)

            if value := admin_area_title.get("value", None):
                admin_area_title["value"] = value
            admin_area_title["previous_value"] = current_value
            household_data_with_approve_status["admin_area_title"] = admin_area_title

        flex_fields_with_approve_status = {
            field: {"value": value, "approve_status": False, "previous_value": household.flex_fields.get(field)}
            for field, value in flex_fields.items()
        }
        household_data_with_approve_status["flex_fields"] = flex_fields_with_approve_status
        if roles:
            household_data_with_approve_status["roles"] = _prepare_roles_with_approve_status(roles)  # type: ignore

        ticket_individual_data_update_details = TicketHouseholdDataUpdateDetails(
            household_data=household_data_with_approve_status,
            household=household,
            ticket=self.grievance_ticket,
        )
        ticket_individual_data_update_details.save()
        self.grievance_ticket.refresh_from_db()
        return [self.grievance_ticket]

    def update(self) -> GrievanceTicket:
        ticket_details = self.grievance_ticket.household_data_update_ticket_details
        household_data_update_new_extras = self.extras.get("household_data_update_issue_type_extras")
        household = ticket_details.household
        new_household_data = household_data_update_new_extras.get("household_data", {})
        to_date_string(new_household_data, "start")
        to_date_string(new_household_data, "end")
        roles = new_household_data.pop("roles", [])
        flex_fields = {
            to_snake_case(field): value for field, value in new_household_data.pop("flex_fields", {}).items()
        }
        verify_flex_fields(flex_fields, "households")
        household_data_with_approve_status = {
            to_snake_case(field): {"value": value, "approve_status": False}
            for field, value in new_household_data.items()
        }
        for field in household_data_with_approve_status:
            current_value = getattr(household, field, None)
            if isinstance(current_value, datetime | date):
                current_value = current_value.isoformat()
            if isinstance(current_value, Country):
                current_value = current_value.alpha3
            if isinstance(current_value, geo_models.Country):
                current_value = current_value.iso_code3
            household_data_with_approve_status[field]["previous_value"] = current_value

        if admin_area_title := household_data_with_approve_status.get("admin_area_title"):
            area = getattr(household, "admin_area", None)
            current_value = getattr(area, "p_code", None)

            if value := admin_area_title.get("value", None):
                admin_area_title["value"] = value.split("-")[1].strip()
            admin_area_title["previous_value"] = current_value
            household_data_with_approve_status["admin_area_title"] = admin_area_title

        flex_fields_with_approve_status = {
            field: {"value": value, "approve_status": False, "previous_value": household.flex_fields.get(field)}
            for field, value in flex_fields.items()
        }
        household_data_with_approve_status["flex_fields"] = flex_fields_with_approve_status
        if roles:
            household_data_with_approve_status["roles"] = _prepare_roles_with_approve_status(roles)  # type: ignore
        ticket_details.household_data = household_data_with_approve_status
        ticket_details.save()
        self.grievance_ticket.refresh_from_db()
        return self.grievance_ticket

    def close(self, user: AbstractUser) -> None:
        ticket_details = self.grievance_ticket.household_data_update_ticket_details
        if not ticket_details:
            return
        details = self.grievance_ticket.household_data_update_ticket_details
        household = details.household
        old_household = copy_model_object(household)
        household_data = details.household_data
        country_origin = household_data.get("country_origin", {})
        country = household_data.get("country", {})
        admin_area_title = household_data.pop("admin_area_title", {})
        flex_fields_with_additional_data = household_data.pop("flex_fields", {})
        roles_data = sorted(household_data.pop("roles", []), key=lambda x: x["value"] != "PRIMARY")
        flex_fields = {
            field: data.get("value")
            for field, data in flex_fields_with_additional_data.items()
            if isinstance(data, dict) and data.get("approve_status") is True
        }
        if country_origin.get("value") is not None:
            household_data["country_origin"]["value"] = geo_models.Country.objects.filter(
                iso_code3=country_origin.get("value")
            ).first()
        if country.get("value") is not None:
            household_data["country"]["value"] = geo_models.Country.objects.filter(
                iso_code3=country.get("value")
            ).first()
        only_approved_data = {
            field: value_and_approve_status.get("value")
            for field, value_and_approve_status in household_data.items()
            if is_approved(value_and_approve_status)
        }
        merged_flex_fields = {}
        cast_flex_fields(flex_fields)
        if household.flex_fields is not None:
            merged_flex_fields.update(household.flex_fields)
        merged_flex_fields.update(flex_fields)

        Household.objects.filter(id=household.id).update(flex_fields=merged_flex_fields, **only_approved_data)
        updated_household = Household.objects.get(id=household.id)

        if admin_area_title.get("value") is not None and is_approved(admin_area_title):
            area = Area.objects.filter(p_code=admin_area_title.get("value")).first()
            updated_household.set_admin_areas(area)
        # update Roles
        for role in roles_data:
            # update only approved roles
            if role.get("approve_status") is True:
                individual_id = role["individual_id"]
                individual = get_object_or_404(Individual, id=individual_id)
                handle_role(role.get("value"), household, individual)

        new_household = Household.objects.select_for_update().get(id=household.id)
        recalculate_data(new_household)
        updated_household = Household.objects.get(id=household.id)  # refresh_from_db() doesn't work here
        log_create(
            Household.ACTIVITY_LOG_MAPPING,
            "business_area",
            user,
            self.grievance_ticket.programs.all(),
            old_household,
            updated_household,
        )
