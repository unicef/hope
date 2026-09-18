from datetime import date, datetime
from typing import Any

from django.contrib.auth.models import AbstractUser
from django.db.models.fields.files import FieldFile
from django.shortcuts import get_object_or_404
from django_countries.fields import Country
from rest_framework.exceptions import ValidationError

from hope.apps.activity_log.utils import copy_model_object
from hope.apps.core.utils import to_snake_case
from hope.apps.grievance.models import GrievanceTicket, TicketHouseholdDataUpdateDetails
from hope.apps.grievance.services.data_change.data_change_service import (
    DataChangeService,
)
from hope.apps.grievance.services.data_change.utils import (
    cast_flex_fields,
    handle_image_field,
    handle_role,
    is_approved,
    to_date_string,
    verify_flex_fields,
)
from hope.apps.household.api.caches import invalidate_household_list_cache
from hope.apps.household.services.household_recalculate_data import (
    recalculate_data,
)
from hope.models import Area, Facility, Household, Individual, country as geo_models, log_create
from hope.models.currency import Currency


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


def _resolve_facility(household: Household, name: str | None, admin_area_p_code: str | None) -> Facility | None:
    if not name:
        return None
    facilities = Facility.objects.filter(name=name.upper(), business_area=household.business_area)
    if admin_area_p_code:
        facilities = facilities.filter(admin_area__p_code=admin_area_p_code)
    if len(facilities) != 1:
        scope = f" in admin area {admin_area_p_code}" if admin_area_p_code else ""
        raise ValidationError(f"Ticket cannot be closed, {name} does not match exactly one facility{scope}")
    return facilities[0]


def _facility_admin_area_p_code(household: Household) -> str | None:
    return household.facility.admin_area.p_code if household.facility else None


class HouseholdDataUpdateService(DataChangeService):
    def save(self) -> list[GrievanceTicket]:
        data_change_extras = self.extras.get("issue_type")
        household_data_update_issue_type_extras = data_change_extras.get("household_data_update_issue_type_extras")
        household = household_data_update_issue_type_extras.get("household")
        household_data = household_data_update_issue_type_extras.get("household_data", {})
        roles = household_data.pop("roles", [])
        to_date_string(household_data, "start")
        to_date_string(household_data, "end")
        handle_image_field(household_data, "consent_sign")
        flex_fields = {to_snake_case(field): value for field, value in household_data.pop("flex_fields", {}).items()}
        verify_flex_fields(flex_fields, "households")
        household_data_with_approve_status = {
            to_snake_case(field): {"value": value, "approve_status": False} for field, value in household_data.items()
        }
        for field, field_dict in household_data_with_approve_status.items():
            current_value = getattr(household, field, None)
            if isinstance(current_value, datetime | date):
                current_value = current_value.isoformat()
            if isinstance(current_value, Country):
                current_value = current_value.alpha3
            if isinstance(current_value, geo_models.Country):
                current_value = current_value.iso_code3
            if isinstance(current_value, Currency):
                current_value = current_value.code
            if isinstance(current_value, Facility):
                current_value = current_value.name
            if isinstance(current_value, FieldFile):
                current_value = current_value.name
            field_dict["previous_value"] = current_value

        if admin_area_title := household_data_with_approve_status.get("admin_area_title"):
            area = getattr(household, "admin_area", None)
            current_value = getattr(area, "p_code", None)

            if value := admin_area_title.get("value", None):
                admin_area_title["value"] = value
            admin_area_title["previous_value"] = current_value
            household_data_with_approve_status["admin_area_title"] = admin_area_title

        if facility_admin_area := household_data_with_approve_status.get("facility_admin_area"):
            facility_admin_area["previous_value"] = _facility_admin_area_p_code(household)

        flex_fields_with_approve_status = {
            field: {
                "value": value,
                "approve_status": False,
                "previous_value": household.flex_fields.get(field),
            }
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
        household_data_update_new_extras = self.extras.get("household_data_update_issue_type_extras")
        if not household_data_update_new_extras:
            # No data-change payload in the request: keep the stored request as it is.
            return self.grievance_ticket
        ticket_details = self.grievance_ticket.household_data_update_ticket_details
        household = ticket_details.household
        new_household_data = household_data_update_new_extras.get("household_data", {})
        to_date_string(new_household_data, "start")
        to_date_string(new_household_data, "end")
        handle_image_field(new_household_data, "consent_sign")
        roles = new_household_data.pop("roles", [])
        flex_fields = {
            to_snake_case(field): value for field, value in new_household_data.pop("flex_fields", {}).items()
        }
        verify_flex_fields(flex_fields, "households")
        household_data_with_approve_status = {
            to_snake_case(field): {"value": value, "approve_status": False}
            for field, value in new_household_data.items()
        }
        for field, field_dict in household_data_with_approve_status.items():
            current_value = getattr(household, field, None)
            if isinstance(current_value, datetime | date):
                current_value = current_value.isoformat()
            if isinstance(current_value, Country):
                current_value = current_value.alpha3
            if isinstance(current_value, geo_models.Country):
                current_value = current_value.iso_code3
            if isinstance(current_value, Currency):
                current_value = current_value.code
            if isinstance(current_value, Facility):
                current_value = current_value.name
            if isinstance(current_value, FieldFile):
                current_value = current_value.name
            field_dict["previous_value"] = current_value

        if admin_area_title := household_data_with_approve_status.get("admin_area_title"):
            area = getattr(household, "admin_area", None)
            current_value = getattr(area, "p_code", None)

            if value := admin_area_title.get("value", None):
                admin_area_title["value"] = value.split("-")[1].strip()
            admin_area_title["previous_value"] = current_value
            household_data_with_approve_status["admin_area_title"] = admin_area_title

        if facility_admin_area := household_data_with_approve_status.get("facility_admin_area"):
            facility_admin_area["previous_value"] = _facility_admin_area_p_code(household)

        flex_fields_with_approve_status = {
            field: {
                "value": value,
                "approve_status": False,
                "previous_value": household.flex_fields.get(field),
            }
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
            if isinstance(data, dict) and is_approved(data)
        }
        if country_origin.get("value") is not None:
            household_data["country_origin"]["value"] = geo_models.Country.objects.filter(  # type: ignore[index]
                iso_code3=country_origin.get("value")
            ).first()
        if country.get("value") is not None:
            household_data["country"]["value"] = geo_models.Country.objects.filter(  # type: ignore[index]
                iso_code3=country.get("value")
            ).first()
        currency = household_data.get("currency", {})
        if currency.get("value") is not None:
            household_data["currency"]["value"] = Currency.objects.filter(  # type: ignore[index]
                code=currency.get("value")
            ).first()
        facility = household_data.get("facility", {})
        facility_admin_area = household_data.pop("facility_admin_area", {})
        admin_area_p_code = facility_admin_area.get("value") if is_approved(facility_admin_area) else None
        if facility.get("value") is not None and is_approved(facility):
            household_data["facility"]["value"] = _resolve_facility(  # type: ignore[index]
                household, facility.get("value"), admin_area_p_code
            )
        elif admin_area_p_code:
            if household.facility is None:
                raise ValidationError("Ticket cannot be closed, the household has no facility to move")
            household_data["facility"] = {  # type: ignore[index]
                "value": _resolve_facility(household, household.facility.name, admin_area_p_code),
                "approve_status": True,
            }
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

        invalidate_household_list_cache(household.program_id)
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
                handle_role(household, individual, role.get("value"))

        new_household = Household.objects.select_for_update().get(id=household.id)
        recalculate_data(new_household)
        updated_household = Household.objects.get(id=household.id)  # refresh_from_db() doesn't work here
        log_create(
            Household.ACTIVITY_LOG_MAPPING,
            "business_area",
            user,
            self.grievance_ticket.programs.all(),
            old_object=old_household,
            new_object=updated_household,
        )
