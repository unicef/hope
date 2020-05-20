import os

import requests


class KoboAPI:
    KPI_URL = "https://kobo.humanitarianresponse.info"

    def __init__(self, kpi_url: str = None):
        if kpi_url:
            self.KPI_URL = kpi_url

        self._get_token()

    def _get_url(self, endpoint: str):
        endpoint.strip("/")
        if endpoint != "token":
            endpoint = f"api/v2/{endpoint}"
        return f"{self.KPI_URL}/{endpoint}?format=json"

    def _get_token(self):
        username = os.getenv("KOBO_USERNAME")
        password = os.getenv("KOBO_PASSWORD")
        token_url = self._get_url("token")

        self._client = requests.session()

        response = self._client.get(url=token_url, auth=(username, password))
        response.raise_for_status()

        token = response.json().get("token")
        self._client.headers.update({"Authorization": f"token {token}"})

    def get_all_projects_data(self) -> list:
        projects_url = self._get_url("assets")

        response = self._client.get(url=projects_url)
        response.raise_for_status()

        data: dict = response.json()

        result: list = data["results"]

        while data["next"]:
            response = self._client.get(url=data["next"])
            response.raise_for_status()
            data = response.json()
            result.extend(data["results"])

        return result

    def get_single_project_data(self, uid: str) -> dict:
        projects_url = self._get_url(f"assets/{uid}")

        response = self._client.get(url=projects_url)
        response.raise_for_status()

        return response.json()
