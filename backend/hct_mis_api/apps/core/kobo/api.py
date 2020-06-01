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

    def _handle_paginated_results(self, url):
        data: dict = self._handle_request(url)

        results: list = data["results"]

        # if there will be more than 30000 results,
        # we need to make additional queries
        while data["next"]:
            data = self._handle_request(data["next"])
            results.extend(data["results"])

        return results

    def _get_url(self, endpoint: str):
        endpoint.strip("/")
        if endpoint != "token":
            endpoint = f"api/v2/{endpoint}"
        # According to the Kobo API documentation,
        # the maximum limit per page is 30000
        return f"{self.KPI_URL}/{endpoint}?limit=30000&format=json"

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

        return self._handle_paginated_results(projects_url)

    def get_single_project_data(self, uid: str) -> dict:
        projects_url = self._get_url(f"assets/{uid}")

        return self._handle_request(projects_url)

    def get_project_submissions(self, uid: str) -> list:
        submissions_url = self._get_url(f"assets/{uid}/data")

        return self._handle_paginated_results(submissions_url)
