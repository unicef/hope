import requests
from django.conf import settings


class AirflowApi:
    _BASE_URL = f"http://{settings.AIRFLOW_HOST}:8080/api/experimental"

    @classmethod
    def start_dag(
        cls, dag_id: str, context: dict = None, headers: dict = None
    ) -> requests.Response:
        default_headers = {
            "Cache-Control": "no-cache",
            "Content-Type": "application/json",
        }

        if headers is None:
            headers = {}

        if context is None:
            context = {}

        return requests.post(
            url=f"{cls._BASE_URL}/dags/{dag_id}/dag_runs",
            headers=default_headers.update(headers),
            json={"conf": context},
        )

    @classmethod
    def health_check(cls) -> requests.Response:
        return requests.get(url=f"{cls._BASE_URL}/test")
