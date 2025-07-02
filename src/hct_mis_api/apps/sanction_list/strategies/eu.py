import io
import logging
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import TYPE_CHECKING

import requests
from elasticsearch import NotFoundError

from ...geo.models import Country
from ...program.models import Program
from ..tasks.check_against_sanction_list_pre_merge import (
    check_against_sanction_list_pre_merge,
)
from ._base import BaseSanctionList

if TYPE_CHECKING:  # pragma: no cover
    from typing import Generator, TypedDict

    Alias = TypedDict(
        "Alias",
        {
            "first_name": str,
            "second_name": str,
            "third_name": str,
            "full_name": str,
            "reference_number": str,
            "data_id": str,
            "listed_on": str,
            "version_num": str,
            "country_of_birth": None,
        },
    )
    Entry = TypedDict(
        "Entry",
        {
            "id": int,
            "aliases": list[Alias],
            "birthdays": list[dict[str, str | None]],
            "citizenships": list[dict[str, str | None]],
            "identifications": list[dict[str, str | None]],
        },
    )

logger = logging.getLogger(__name__)


class EUParser:
    def __init__(self, root: ET.Element) -> None:
        self.root = root

    def __iter__(self) -> "Generator[Entry, None, None]":
        namespace = {"ns": "http://eu.europa.ec/fpi/fsd/export"}
        num = self.root.get("globalFileId", "")
        for _i, entity in enumerate(self.root.findall("ns:sanctionEntity", namespace), 1):
            subjectType = entity.findall("ns:subjectType", namespace)[0]
            if subjectType.get("classificationCode") != "P":
                continue
            aliases: list[Alias] = []
            for alias in entity.findall("ns:nameAlias", namespace):
                regulation = entity.find("ns:regulation", namespace) or {}
                dt = regulation.get("publicationDate", "")
                row_pk = f"{entity.get('logicalId').strip()}-{alias.get('logicalId').strip()}".lower().strip()
                aliases.append(
                    {
                        "first_name": alias.get("firstName", ""),
                        "second_name": alias.get("middleName", ""),
                        "third_name": alias.get("lastName", ""),
                        "full_name": alias.get("wholeName", ""),
                        "reference_number": row_pk,
                        "data_id": alias.get("logicalId", ""),
                        "listed_on": dt,
                        "version_num": num,
                        "country_of_birth": None,
                    }
                )
            birthdays = []
            for birthdate_element in entity.findall("ns:birthdate", namespace):
                birthdays.append(
                    {
                        "date": birthdate_element.get("birthdate"),
                    }
                )
            citizenships = []
            for citizenship_element in entity.findall("ns:citizenship", namespace):
                citizenships.append(
                    {
                        "region": citizenship_element.get("region"),
                        "iso_code2": citizenship_element.get("countryIso2Code"),
                        "country": citizenship_element.get("countryDescription"),
                    }
                )
            identifications = []
            for id_element in entity.findall("ns:identification", namespace):
                identifications.append(
                    {
                        "type_of_document": id_element.get("identificationTypeCode"),
                        "document_number": id_element.get("number"),
                        "date_of_issue": id_element.get("issueDate"),
                        "issuing_country__iso_code2": id_element.get("countryIso2Code"),
                    }
                )
            yield {
                "id": _i,
                "aliases": aliases,
                "birthdays": birthdays,
                "citizenships": citizenships,
                "identifications": identifications,
            }


class EUSanctionList(BaseSanctionList):
    def load_from_file(self, file_path: str | Path) -> None:
        tree = ET.parse(str(file_path))
        root = tree.getroot()
        self.parse(root)

    def load_from_url(self) -> None:
        response = requests.get(self.context.config["url"])
        tree = ET.parse(io.BytesIO(response.content))
        root = tree.getroot()
        self.parse(root)

    def parse(self, root: ET.Element) -> int:
        parser = EUParser(root)
        _i = 0
        for _i, entry in enumerate(parser):
            ind_data = entry["aliases"][0]
            ref_number = ind_data.pop("reference_number")
            ind, __ = self.context.entries.update_or_create(reference_number=ref_number, defaults=ind_data)
            for alias in entry["aliases"][1:]:
                ind.alias_names.get_or_create(name=alias["full_name"])

            for date in entry["birthdays"]:
                if date["date"]:
                    ind.dates_of_birth.get_or_create(**date)

            for doc in entry["identifications"]:
                ind.documents.get_or_create(**doc)

            for nationality in entry["citizenships"]:
                try:
                    country = Country.objects.get(iso_code2=nationality["iso_code2"])
                    ind.nationalities.get_or_create(nationality=country)
                except Country.DoesNotExist:  # pragma: no cover
                    logger.error(f"Unknown country: '{nationality['iso_code2']}'")

        try:
            cls_eu = self.__class__
            programs = Program.objects.filter(
                sanction_lists__strategy=f"{cls_eu.__module__}.{cls_eu.__qualname__}"
            )  # get programs which use sanction list which is using this strategy
            for program in programs:
                check_against_sanction_list_pre_merge(program_id=program.id)
        except NotFoundError:  # pragma: no cover
            pass
        return _i

    def refresh(self) -> None:
        self.load_from_url()
