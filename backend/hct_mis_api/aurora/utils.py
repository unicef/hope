import logging
from typing import Any, Dict, List
from urllib.parse import urlencode

from django.db.models.options import Options
from django.db.transaction import atomic
from django.utils import timezone

import coreapi
from constance import config
from coreapi import codecs
from coreapi.exceptions import NoCodecAvailable

from hct_mis_api.aurora.models import Organization, Project, Record, Registration

logger = logging.getLogger(__name__)


def fetch_metadata(auth_token: str) -> List:
    decoders = [
        # codecs.CoreJSONCodec(),
        codecs.JSONCodec()
    ]
    auth = coreapi.auth.TokenAuthentication(scheme="Token", token=auth_token)

    client = coreapi.Client(auth=auth, decoders=decoders)
    schema = client.get(config.AURORA_SERVER)
    page = client.get(schema["organization"])
    ret = []
    for dataOrg in page["results"]:
        ret.append(dataOrg)
        org, __ = Organization.objects.update_or_create(
            source_id=dataOrg["id"],
            defaults={
                "name": dataOrg["name"],
                "slug": dataOrg["slug"],
            },
        )
        prjs = client.get(dataOrg["projects"])
        ret[-1]["projects"] = []
        for dataPrj in prjs["results"]:
            prj, __ = Project.objects.update_or_create(
                source_id=dataPrj["id"],
                defaults={
                    "organization": org,
                    "name": dataPrj["name"],
                },
            )
            regs = client.get(dataPrj["registrations"])
            dataPrj["registrations"] = []
            for dataReg in regs:
                try:
                    mt = client.get(dataReg["metadata"])
                except NoCodecAvailable as e:
                    logger.exception(e)
                    mt = {}
                reg, __ = Registration.objects.update_or_create(
                    source_id=dataReg["id"],
                    defaults={
                        "project": prj,
                        "name": dataReg["name"],
                        "slug": dataReg["slug"],
                        "metadata": mt,
                    },
                )
                dataPrj["registrations"].append(dataReg)
            ret[-1]["projects"].append(dataPrj)
    return ret


def get_metadata(auth_token: str) -> Dict:
    auth = coreapi.auth.TokenAuthentication(scheme="Token", token=auth_token)

    client = coreapi.Client(auth=auth)
    schema = client.get(config.AURORA_SERVER)
    rnd = timezone.now()
    return client.get(schema["record"] + f"metadata/?{rnd}")


def fetch_records(auth_token: str, overwrite: bool = False, **filters: Any) -> Dict:
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
                __, c = Record.objects.get_or_create(source_id=record["id"], defaults=data)
                if c:
                    created += 1
        url = page["next"]
    return {
        "pages": pages,
        "records": records,
        "created": created,
        "updated": updated,
    }
