import logging
from typing import Any, TYPE_CHECKING
from urllib.parse import urlencode

from django.db.transaction import atomic
from django.utils import timezone

import coreapi
from constance import config
from coreapi import codecs
from coreapi.exceptions import NoCodecAvailable

from hope.contrib.aurora.models import (
    Organization,
    Project,
    Record,
    Registration,
)

if TYPE_CHECKING:
    from django.db.models.options import Options

logger = logging.getLogger(__name__)


def fetch_metadata(auth_token: str) -> list:
    decoders = [codecs.JSONCodec()]
    auth = coreapi.auth.TokenAuthentication(scheme="Token", token=auth_token)

    client = coreapi.Client(auth=auth, decoders=decoders)
    schema = client.get(config.AURORA_SERVER)
    page = client.get(schema["organization"])
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
        prjs = client.get(data_org["projects"])
        ret[-1]["projects"] = []
        for data_prj in prjs["results"]:
            prj, __ = Project.objects.update_or_create(
                source_id=data_prj["id"],
                defaults={
                    "organization": org,
                    "name": data_prj["name"],
                },
            )
            regs = client.get(data_prj["registrations"])
            data_prj["registrations"] = []
            for data_reg in regs:
                try:
                    mt = client.get(data_reg["metadata"])
                except NoCodecAvailable as e:
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
    auth = coreapi.auth.TokenAuthentication(scheme="Token", token=auth_token)

    client = coreapi.Client(auth=auth)
    schema = client.get(config.AURORA_SERVER)
    rnd = timezone.now()
    return client.get(schema["record"] + f"metadata/?{rnd}")


def fetch_records(auth_token: str, overwrite: bool = False, **filters: Any) -> dict:
    decoders = [codecs.JSONCodec()]
    auth = coreapi.auth.TokenAuthentication(scheme="Token", token=auth_token)

    client = coreapi.Client(auth=auth, decoders=decoders)
    schema = client.get(config.AURORA_SERVER)
    url = f"{schema['record']}?{urlencode(filters)}"
    opts: Options = Record._meta
    field_names = [f.name for f in opts.get_fields()]
    pages = records = updated = created = 0
    while url:
        page = client.get(url)
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
