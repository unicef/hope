import requests
from django.conf import settings

from core.models import BusinessArea
from household.models import Individual
from payment.models import CashPlanPaymentVerification


class TokenNotProvided(Exception):
    pass


class RapidProAPI:
    FLOWS_ENDPOINT = "/flows.json"
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
            raise TokenNotProvided("Token is not set for this business area.")
        self.url = settings.RAPID_PRO_URL
        self._client.headers.update({"Authorization": f"Token {token}"})

    def _handle_get_request(self, url) -> dict:
        response = self._client.get(url=f"{self._get_url()}{url}")
        response.raise_for_status()
        return response.json()

    def _handle_post_request(self, url, data) -> dict:
        response = self._client.post(url=f"{self._get_url()}{url}", data=data)
        response.raise_for_status()
        return response.json()

    def _get_url(self):
        return f"{self.url}/api/v2"

    def get_flows(self):
        flows = self._handle_get_request(RapidProAPI.FLOWS_ENDPOINT)
        return flows["results"]

    def start_flow(self, flow_uuid, phone_numbers):
        urns = [f"tel:{x}" for x in phone_numbers]
        data = {"flow_uuid": flow_uuid, "urns": urns}
        print(data)
        # self._handle_post_request(
        #     RapidProAPI.FLOW_STARTS_ENDPOINT,
        #     data,
        # )

    def create_group(self, name):
        print(name)
        group = self._handle_post_request(
            RapidProAPI.GROUPS_ENDPOINT, {"name": name}
        )
        return group

    def create_contact(self, name, tel, group_uuid):
        print({"name": name, "groups": [group_uuid], "urns": [f"tel:{tel}"]})
        contact = self._handle_post_request(
            RapidProAPI.CONTACTS_ENDPOINT,
            {"name": name, "groups": [group_uuid], "urns": [f"tel:{tel}"]},
        )
        return contact

    def create_contacts_and_groups_for_verification(
        self, cash_plan_verification
    ):
        individuals = Individual.objects.filter(
            heading_household__payment_records__verifications__cash_plan_payment_verification=cash_plan_verification.id
        )
        group = self.create_group(f"Verify: {cash_plan_verification.id}")
        for individual in individuals:
            self.create_contact(
                f"{individual.unicef_id}", individual.phone_no, group["uuid"],
            )

        return group
