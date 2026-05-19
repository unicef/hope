"""
Client for interacting with UNICEF's Inform API.

This module provides a thin wrapper around the Inform REST service.  It
mirrors the pattern used by the existing KoboAPI class to maintain a
consistent interface across data-collection platforms.  The implementation
relies on the `requests` library and uses environment settings defined in
``hope.config.fragments.inform``.  No additional dependencies are required.

Typical usage::

    from hope.apps.core.inform.api import InformAPI

    api = InformAPI()
    forms = api.get_forms()
    for form in forms:
        print(form["id"], form["title"])

    submissions = api.get_form_submissions(form_id="12345")

The class caches its session and sets the Authorization header using the
prefix and token provided via the Django settings.  If no base URL or
token is configured the API will still instantiate, but calls to the
remote service will likely fail with a connection or authorization error.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class InformAPIError(Exception):
    """Base exception for Inform API errors."""


class InformAPI:
    """Simple client for the Inform REST API.

    Parameters can be overridden when instantiating the client, but by
    default they are pulled from the Django settings module.  The
    Authorization header is constructed automatically using the provided
    prefix and token.
    """

    def __init__(
        self,
        base_url: str | None = None,
        token: str | None = None,
        auth_header_prefix: str | None = None,
        forms_endpoint: str | None = None,
        data_endpoint_template: str | None = None,
    ) -> None:
        self._base_url = base_url or getattr(settings, "INFORM_API_BASE_URL", "")
        self._token = token or getattr(settings, "INFORM_API_TOKEN", "")
        self._auth_header_prefix = auth_header_prefix or getattr(
            settings, "INFORM_API_AUTH_HEADER_PREFIX", "Token"
        )
        # Endpoint for listing forms (e.g. "/api/v1/forms")
        self._forms_endpoint = forms_endpoint or getattr(
            settings, "INFORM_FORMS_ENDPOINT", "/api/v1/forms"
        )
        # Template for retrieving submissions for a given form (e.g.
        # "/api/v1/data/{form_id}")
        self._data_endpoint_template = data_endpoint_template or getattr(
            settings,
            "INFORM_DATA_ENDPOINT_TEMPLATE",
            "/api/v1/data/{form_id}",
        )

        self._session = requests.Session()
        self._configure_session()

    def _configure_session(self) -> None:
        """Initialise the requests session with appropriate headers."""
        if self._token:
            authorization = f"{self._auth_header_prefix} {self._token}"
            self._session.headers.update({"Authorization": authorization})

    def _get(self, path: str) -> requests.Response:
        """Send a GET request to the given path and return the Response.

        Args:
            path: The path relative to the base URL.  Should not
                include the base URL itself.
        Returns:
            requests.Response: The HTTP response.
        Raises:
            InformAPIError: If the response status code indicates an error.
        """
        if not self._base_url:
            raise InformAPIError("INFORM_API_BASE_URL is not configured.")
        url = f"{self._base_url}{path}"
        try:
            response = self._session.get(url)
            response.raise_for_status()
        except requests.exceptions.HTTPError as exc:  # pragma: no cover
            logger.error("Inform API request failed: %s", exc)
            raise InformAPIError(str(exc))
        return response

    def get_forms(self) -> List[Dict[str, Any]]:
        """Retrieve a list of available forms from the Inform API.

        Returns:
            list[dict[str, Any]]: A list of form metadata dictionaries.  Each
                dictionary contains at minimum an "id" and "name" key if
                present in the response.  Additional keys are returned as
                provided by the Inform service.

        Raises:
            InformAPIError: If the request fails.
        """
        response = self._get(self._forms_endpoint)
        try:
            data = response.json()
        except ValueError as exc:  # pragma: no cover
            logger.error("Failed to parse Inform forms response: %s", exc)
            raise InformAPIError("Invalid JSON in Inform forms response")

        forms: List[Dict[str, Any]] = []
        # The API may return either a list of forms directly or wrap it in a
        # "results" key similar to Kobo.  We normalise the result into a list.
        if isinstance(data, list):
            raw_forms = data
        elif isinstance(data, dict) and "results" in data:
            raw_forms = data.get("results", [])
        else:
            raw_forms = []

        for item in raw_forms:
            # Copy all available metadata but ensure id/name keys exist
            form: Dict[str, Any] = {}
            # Use "id" or "pk" or "uid" whichever is present
            form_id = item.get("id") or item.get("uid") or item.get("pk")
            if form_id is None:
                # Skip invalid entries
                continue
            form["id"] = str(form_id)
            # Name may be under different keys; fall back to title if present
            form_name = item.get("name") or item.get("title") or item.get("form_id") or ""
            form["name"] = form_name
            # Include date modified if available
            if "date_modified" in item:
                form["date_modified"] = item.get("date_modified")
            forms.append(form)

        return forms

    def get_form_submissions(self, form_id: str) -> Any:
        """Retrieve submissions for a given form.

        Args:
            form_id: The ID of the form whose submissions should be pulled.
        Returns:
            Any: JSON parsed response containing submissions.

        Raises:
            InformAPIError: If the request fails.
        """
        if not form_id:
            raise InformAPIError("form_id must be provided")
        endpoint = self._data_endpoint_template.format(form_id=form_id)
        response = self._get(endpoint)
        try:
            return response.json()
        except ValueError as exc:  # pragma: no cover
            logger.error("Failed to parse Inform submissions response: %s", exc)
            raise InformAPIError("Invalid JSON in Inform submissions response")