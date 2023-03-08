import logging

from django.conf import settings

import coreapi
from coreapi import codecs
from coreapi.exceptions import NoCodecAvailable

from hct_mis_api.aurora.models import Organization, Project, Registration

logger = logging.getLogger(__name__)


def fetch():
    decoders = [
        # codecs.CoreJSONCodec(),
        codecs.JSONCodec()
    ]
    auth = coreapi.auth.TokenAuthentication(scheme="Token", token=settings.AURORA_TOKEN)

    client = coreapi.Client(auth=auth, decoders=decoders)
    schema = client.get(settings.AURORA_SERVER)
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
