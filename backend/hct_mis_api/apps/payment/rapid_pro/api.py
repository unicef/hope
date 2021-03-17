import logging
from decimal import Decimal

import requests
from constance import config
from django.conf import settings

from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.household.models import Individual

logger = logging.getLogger(__name__)


class TokenNotProvided(Exception):
    pass


class RapidProAPI:
    FLOWS_ENDPOINT = "/flows.json"
    FLOW_RUNS_ENDPOINT = "/runs.json"
    GROUPS_ENDPOINT = "/groups.json"
    CONTACTS_ENDPOINT = "/contacts.json"
    FLOW_STARTS_ENDPOINT = "/flow_starts.json"

    def __init__(self, business_area_slug):
        self._client = requests.session()
        self._init_token(business_area_slug)

    def _init_token(self, business_area_slug):

        business_area = BusinessArea.objects.get(slug=business_area_slug)
        token = business_area.rapid_pro_api_key
        self.url = business_area.rapid_pro_host
        if not self.url:
            self.url = settings.RAPID_PRO_URL
        if not token:
            logger.error(f"Token is not set for this business area, business_area={business_area.name}")
            raise TokenNotProvided("Token is not set for this business area.")
        self.url = settings.RAPID_PRO_URL
        self._client.headers.update({"Authorization": f"Token {token}"})

    def _handle_get_request(self, url, is_absolute_url=False) -> dict:
        if not is_absolute_url:
            url = f"{self._get_url()}{url}"
        response = self._client.get(url)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            logger.exception(e)
            raise
        return response.json()

    def _handle_post_request(self, url, data) -> dict:
        response = self._client.post(url=f"{self._get_url()}{url}", data=data)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            logger.exception(e)
            raise
        return response.json()

    def _get_url(self):
        return f"{self.url}/api/v2"

    def get_flows(self):
        flows = self._handle_get_request(RapidProAPI.FLOWS_ENDPOINT)
        return flows["results"]

    def start_flow(self, flow_uuid, phone_numbers):
        urns = [f"{config.RAPID_PRO_PROVIDER}:{x}" for x in phone_numbers]
        data = {"flow": flow_uuid, "urns": urns, "restart_participants": True}

        response = self._handle_post_request(
            RapidProAPI.FLOW_STARTS_ENDPOINT,
            data,
        )
        return response

    def get_flow_runs(self):
        return self._get_paginated_results(f"{RapidProAPI.FLOW_RUNS_ENDPOINT}?responded=true")

    def get_mapped_flow_runs(self, start_uuid):
        results = self.get_flow_runs()
        mapped_results = [
            self._map_to_internal_structure(x)
            for x in results
            if x.get("start") is not None and x.get("start").get("uuid") == start_uuid
        ]
        return mapped_results

    def _get_paginated_results(self, url) -> list:
        next_url = f"{self._get_url()}{url}"
        results: list = []
        while next_url:
            data = self._handle_get_request(next_url, is_absolute_url=True)
            next_url = data["next"]
            results.extend(data["results"])
        return results

    def _map_to_internal_structure(self, run):
        variable_received_name = "cash_received_text"
        variable_received_positive_string = "YES"
        variable_amount_name = "cash_received_amount"
        phone_number = run.get("contact").get("urn").split(":")[1]
        values = run.get("values")
        received = None
        received_amount = None
        if not values:
            return {"phone_number": phone_number, "received": None, "received_amount": None}
        received_variable = values.get(variable_received_name)
        if received_variable is not None:
            received = received_variable.get("value").upper() == variable_received_positive_string
        received_amount_variable = values.get(variable_amount_name)
        if received_variable is not None:
            received_amount = Decimal(received_amount_variable.get("value", 0))
        return {"phone_number": phone_number, "received": received, "received_amount": received_amount}

    def create_group(self, name):
        group = self._handle_post_request(RapidProAPI.GROUPS_ENDPOINT, {"name": name})
        return group

    def create_contact(self, name, tel, group_uuid):
        contact = self._handle_post_request(
            RapidProAPI.CONTACTS_ENDPOINT,
            {"name": name, "groups": [group_uuid], "urns": [f"{config.RAPID_PRO_PROVIDER}:{tel}"]},
        )
        return contact

    def create_contacts_and_groups_for_verification(self, cash_plan_verification):
        individuals = Individual.objects.filter(
            heading_household__payment_records__verifications__cash_plan_payment_verification=cash_plan_verification.id
        )
        group = self.create_group(f"Verify: {cash_plan_verification.id}")
        for individual in individuals:
            self.create_contact(
                f"{individual.unicef_id}",
                individual.phone_no,
                group["uuid"],
            )

        return group

    def test_connection_start_flow(self, flow_name, phone_number):
        # find flow by name, get its uuid and start it
        # if no flow with that name is found, return error
        try:
            all_flows = self.get_flows()
            test_flow = next((flow for flow in all_flows if flow["name"] == flow_name), None)
            if not test_flow:
                return (
                    f"Initial connection was successful but no flow with name '{flow_name}' was found in results list."
                ), None
            response = self.start_flow(test_flow["uuid"], [phone_number])
            return None, response
        except Exception as e:
            logger.exception(e)
            return str(e), None

    def test_connection_flow_run(self, flow_uuid, phone_number, timestamp=None):
        try:
            # getting start flow that was initiated during test, should be the most recent one with matching flow uuid
            flow_starts = self._handle_get_request(f"{RapidProAPI.FLOW_STARTS_ENDPOINT}")
            flow_start = [
                flow_start for flow_start in flow_starts["results"] if flow_start["flow"]["uuid"] == flow_uuid
            ]
            flow_start_status = None
            if flow_start:
                flow_start_status = flow_start[0]["status"]

            # get the flow run for the specified phone number
            flow_runs_url = f"{RapidProAPI.FLOW_RUNS_ENDPOINT}?flow={flow_uuid}"
            if timestamp:
                flow_runs_url += f"&after={timestamp}"
            flow_runs = self._get_paginated_results(flow_runs_url)
            results_for_contact = [
                flow_run
                for flow_run in flow_runs
                if flow_run.get("contact", {}).get("urn", "") == f"tel:{phone_number}"
            ]
            # format results for template
            responded = [result["values"] for result in results_for_contact if result["responded"]]
            not_responded_count = len([result for result in results_for_contact if not result["responded"]])
            return None, {
                "responded": responded,
                "not_responded": not_responded_count,
                "flow_start_status": flow_start_status,
            }
        except Exception as e:
            logger.exception(e)
            return str(e), None
