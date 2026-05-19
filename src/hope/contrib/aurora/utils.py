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


def _make_session(auth_token: str) -> requests.Session:
    session = requests.Session()
    session.headers["Authorization"] = f"Token {auth_token}"
    return session


def fetch_metadata(auth_token: str) -> list:
    session = _make_session(auth_token)
    schema = session.get(config.AURORA_SERVER).json()
    page = session.get(schema["organization"]).json()
    ret = []
    for data_org in page["results"]:
        ret.append(data_org)
        org, __ = Organization.objects.update_or_create(
            source_id=data_org["id"],
            defaults={
                "name": data_org["name"],
                "slug": data_org["slug"],
            },
        )
        prjs = session.get(data_org["projects"]).json()
        ret[-1]["projects"] = []
        for data_prj in prjs["results"]:
            prj, __ = Project.objects.update_or_create(
                source_id=data_prj["id"],
                defaults={
                    "organization": org,
                    "name": data_prj["name"],
                },
            )
            regs = session.get(data_prj["registrations"]).json()
            data_prj["registrations"] = []
            for data_reg in regs:
                try:
                    mt = session.get(data_reg["metadata"]).json()
                except (requests.exceptions.RequestException, ValueError) as e:
                    logger.exception(e)
                    mt = {}
                reg, __ = Registration.objects.update_or_create(
                    source_id=data_reg["id"],
                    defaults={
                        "project": prj,
                        "name": data_reg["name"],
                        "slug": data_reg["slug"],
                        "metadata": mt,
                    },
                )
                data_prj["registrations"].append(data_reg)
            ret[-1]["projects"].append(data_prj)
    return ret


def get_metadata(auth_token: str) -> dict:
    session = _make_session(auth_token)
    schema = session.get(config.AURORA_SERVER).json()
    rnd = timezone.now()
    return session.get(schema["record"] + f"metadata/?{rnd}").json()


def fetch_records(auth_token: str, overwrite: bool = False, **filters: Any) -> dict:
    session = _make_session(auth_token)
    schema = session.get(config.AURORA_SERVER).json()
    url = f"{schema['record']}?{urlencode(filters)}"
    opts: Options = Record._meta
    field_names = [f.name for f in opts.get_fields()]
    pages = records = updated = created = 0
    while url:
        page = session.get(url).json()
        pages += 1
        with atomic():
            for record in page["results"]:
                records += 1
                data = {x: v for x, v in record.items() if x in field_names}
                data.pop("id")
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
