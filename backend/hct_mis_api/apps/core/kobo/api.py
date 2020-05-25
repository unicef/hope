import os

import requests

from core.models import BusinessArea


class TokenNotProvided(Exception):
    pass


class TokenInvalid(Exception):
    pass


class KoboAPI:
    KPI_URL = "https://kobo.humanitarianresponse.info"

    def __init__(self, business_area_slug, kpi_url: str = None):
        if kpi_url:
            self.KPI_URL = kpi_url

        self._get_token(business_area_slug)

    def _get_url(self, endpoint: str):
        endpoint.strip("/")
        if endpoint != "token":
            endpoint = f"api/v2/{endpoint}"
        return f"{self.KPI_URL}/{endpoint}?format=json"

    def _get_token(self, business_area_slug):
        self._client = requests.session()

        business_area = BusinessArea.objects.get(slug=business_area_slug)
        token = business_area.kobo_token

        if not token:
            raise TokenNotProvided("Token is not set for this business area.")

        self._client.headers.update({"Authorization": f"token {token}"})

    def _handle_request(self, url) -> dict:
        response = self._client.get(url=url)
        response.raise_for_status()
        return response.json()

    def get_all_projects_data(self) -> list:
        projects_url = self._get_url("assets")

        data: dict = self._handle_request(projects_url)

        result: list = data["results"]

        while data["next"]:
            data = self._handle_request(data["next"])
            result.extend(data["results"])

        return result

    def get_single_project_data(self, uid: str) -> dict:
        projects_url = self._get_url(f"assets/{uid}")

        return self._handle_request(projects_url)
