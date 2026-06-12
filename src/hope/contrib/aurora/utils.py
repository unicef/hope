"""Aurora API sync helpers.

These functions pull org / project / registration / record data from the Aurora
HTTP API into local Django models. The Aurora response shape is not part of our
codebase, so this module is the boundary where remote drift can break the sync.

Known failure modes guarded for here:

* **HTTP errors** — 4xx/5xx responses used to fall through silently because no one
  called ``raise_for_status()``. Now every fetch goes through ``_get_json`` which
  raises on non-2xx.
* **JSON decode** — ``Response.json()`` raises ``ValueError`` on non-JSON bodies
  (HTML error pages, gateway timeouts). Surfaced as a ``RequestException`` from
  ``_get_json`` so callers handle it the same way as network failures.
* **Missing keys / wrong shape** — every dict access is guarded with ``.get()``;
  malformed orgs / projects / registrations are skipped with a ``logger.warning``
  instead of crashing the whole sync.
* **Pagination shape drift** — ``_iter_results`` accepts either ``{"results": […]}``
  or a bare list. The registrations endpoint historically returned a bare list
  while orgs / projects paginate; if Aurora ever paginates registrations the
  same way, the loop now Just Works instead of iterating dict keys.

What is intentionally NOT changed:

* ``fetch_records`` still imports only the first page (the original
  ``# we want to import only a sample`` comment is preserved verbatim). Removing
  the cap is a feature decision, not a hardening one.
* The structure of the return value is unchanged — callers that expect the
  ``{"pages", "records", "created", "updated"}`` dict and the nested
  ``ret[-1]["projects"][i]["registrations"]`` list continue to work.
"""

import logging
from typing import TYPE_CHECKING, Any
from urllib.parse import urlencode

from constance import config
from django.db.transaction import atomic
from django.utils import timezone
import requests

from hope.contrib.aurora.models import Organization, Project, Record, Registration

if TYPE_CHECKING:
    from django.db.models.options import Options

logger = logging.getLogger(__name__)


def _get_session(auth_token: str) -> requests.Session:
    session = requests.Session()
    session.headers["Authorization"] = f"Token {auth_token}"
    return session


def _get_json(session: requests.Session, url: str) -> Any:
    """GET ``url`` and decode JSON. Raises ``RequestException`` on HTTP error."""
    response = session.get(url)
    response.raise_for_status()
    return response.json()


def _iter_results(payload: Any) -> list:
    """Return a list of items from a payload that may be paginated or a bare list.

    Aurora endpoints sometimes return ``{"results": [...]}`` and sometimes a
    bare list (notably the registrations endpoint, historically). This helper
    normalizes both shapes so the calling loop is the same.
    """
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        return payload.get("results") or []
    return []


def _sync_registration(session: requests.Session, data_reg: Any, prj: Project) -> bool:
    """Persist one registration and its metadata. Returns True if processed."""
    if not isinstance(data_reg, dict):
        logger.warning("Skipping non-dict registration payload: %s", data_reg)
        return False
    reg_source_id = data_reg.get("id")
    if not reg_source_id:
        logger.warning("Skipping registration with missing id: %s", data_reg)
        return False

    mt: dict = {}
    metadata_url = data_reg.get("metadata")
    if metadata_url:
        try:
            mt = _get_json(session, metadata_url)
        except (ValueError, requests.RequestException):
            logger.exception("Failed to fetch metadata for registration %s", reg_source_id)

    Registration.objects.update_or_create(
        source_id=reg_source_id,
        defaults={
            "project": prj,
            "name": data_reg.get("name", ""),
            "slug": data_reg.get("slug", ""),
            "metadata": mt,
        },
    )
    return True


def _sync_project(session: requests.Session, data_prj: Any, org: Organization) -> dict | None:
    """Persist one project and its registrations. Returns the annotated project dict or None."""
    if not isinstance(data_prj, dict):
        logger.warning("Skipping non-dict project payload: %s", data_prj)
        return None
    prj_source_id = data_prj.get("id")
    regs_url = data_prj.get("registrations")
    if not prj_source_id or not regs_url:
        logger.warning("Skipping project with missing id/registrations: %s", data_prj)
        return None

    prj, __ = Project.objects.update_or_create(
        source_id=prj_source_id,
        defaults={"organization": org, "name": data_prj.get("name", "")},
    )

    try:
        regs = _get_json(session, regs_url)
    except requests.RequestException:
        logger.exception("Failed to fetch registrations for project %s", prj_source_id)
        data_prj["registrations"] = []
        return data_prj

    data_prj["registrations"] = []
    for data_reg in _iter_results(regs):
        if _sync_registration(session, data_reg, prj):
            data_prj["registrations"].append(data_reg)
    return data_prj


def _sync_organization(session: requests.Session, data_org: Any) -> dict | None:
    """Persist one organization and its projects. Returns the annotated org dict or None."""
    if not isinstance(data_org, dict):
        logger.warning("Skipping non-dict organization payload: %s", data_org)
        return None
    source_id = data_org.get("id")
    projects_url = data_org.get("projects")
    if not source_id or not projects_url:
        logger.warning("Skipping organization with missing id/projects: %s", data_org)
        return None

    org, __ = Organization.objects.update_or_create(
        source_id=source_id,
        defaults={"name": data_org.get("name", ""), "slug": data_org.get("slug", "")},
    )

    try:
        prjs = _get_json(session, projects_url)
    except requests.RequestException:
        logger.exception("Failed to fetch projects for organization %s", source_id)
        data_org["projects"] = []
        return data_org

    data_org["projects"] = []
    for data_prj in _iter_results(prjs):
        result = _sync_project(session, data_prj, org)
        if result is not None:
            data_org["projects"].append(result)
    return data_org


def fetch_metadata(auth_token: str) -> list:
    session = _get_session(auth_token)
    schema = _get_json(session, config.AURORA_SERVER)
    org_url = schema.get("organization")
    if not org_url:
        logger.error("Aurora schema is missing 'organization' endpoint")
        return []

    page = _get_json(session, org_url)
    ret: list = []
    for data_org in _iter_results(page):
        result = _sync_organization(session, data_org)
        if result is not None:
            ret.append(result)
    return ret


def get_metadata(auth_token: str) -> dict:
    session = _get_session(auth_token)
    schema = _get_json(session, config.AURORA_SERVER)
    record_url = schema.get("record")
    if not record_url:
        logger.error("Aurora schema is missing 'record' endpoint")
        return {}
    rnd = timezone.now()
    return _get_json(session, f"{record_url}metadata/?{rnd}")


def fetch_records(auth_token: str, overwrite: bool = False, **filters: Any) -> dict:
    session = _get_session(auth_token)
    schema = _get_json(session, config.AURORA_SERVER)
    record_url = schema.get("record")
    if not record_url:
        logger.error("Aurora schema is missing 'record' endpoint")
        return {"pages": 0, "records": 0, "created": 0, "updated": 0}

    url = f"{record_url}?{urlencode(filters)}"
    opts: Options = Record._meta
    field_names = [f.name for f in opts.get_fields()]
    pages = records = updated = created = 0
    while url:
        page = _get_json(session, url)
        pages += 1
        with atomic():
            for record in _iter_results(page):
                if not isinstance(record, dict) or "id" not in record:
                    logger.warning("Skipping record missing 'id': %s", record)
                    continue
                records += 1
                data = {x: v for x, v in record.items() if x in field_names}
                data.pop("id", None)
                __, cr = Record.objects.get_or_create(source_id=record["id"], defaults=data)
                if cr:
                    created += 1
        url = ""  # page["next"] we want to import only a sample
    return {
        "pages": pages,
        "records": records,
        "created": created,
        "updated": updated,
    }
