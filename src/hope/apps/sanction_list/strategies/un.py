import contextlib
from datetime import date, datetime
import logging
import os
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urlparse
from urllib.request import urlopen
from xml.etree.ElementTree import Element

import dateutil.parser
from defusedxml import ElementTree
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import QuerySet
from django.forms import model_to_dict
from django.utils import timezone
from django.utils.functional import cached_property
from elasticsearch.exceptions import NotFoundError

from hope.apps.core.countries import SanctionListCountries as Countries
from hope.apps.sanction_list.tasks.check_against_sanction_list_pre_merge import (
    check_against_sanction_list_pre_merge,
)
from hope.models.country import Country
from hope.models.program import Program
from hope.models.sanction_list_individual import SanctionListIndividual
from hope.models.sanction_list_individual_alias_name import SanctionListIndividualAliasName
from hope.models.sanction_list_individual_countries import SanctionListIndividualCountries
from hope.models.sanction_list_individual_date_of_birth import SanctionListIndividualDateOfBirth
from hope.models.sanction_list_individual_document import SanctionListIndividualDocument
from hope.models.sanction_list_Individual_nationalities import SanctionListIndividualNationalities

from ._base import BaseSanctionList

logger = logging.getLogger(__name__)


class LoadSanctionListXMLTask:
    DEFAULT_URL = "https://scsanctions.un.org/resources/xml/en/consolidated.xml"

    INDIVIDUAL_TAG_PATH = "INDIVIDUALS/INDIVIDUAL"

    def __init__(self, sanction_list: "SanctionList", **kwargs: Any) -> None:
        self.sanction_list = sanction_list
        self.url = kwargs.get("url", self.DEFAULT_URL)
        self.VALUES_PATHS: dict[str, Any] = {
            "data_id": "DATAID",
            "version_num": "VERSIONNUM",
            "first_name": "FIRST_NAME",
            "second_name": "SECOND_NAME",
            "third_name": "THIRD_NAME",
            "fourth_name": "FOURTH_NAME",
            "un_list_type": "UN_LIST_TYPE",
            "reference_number": "REFERENCE_NUMBER",
            "listed_on": "LISTED_ON",
            "comments": "COMMENTS1",
            "nationalities": self._get_nationalities,
            "list_type": "LIST_TYPE/VALUE",
            "alias_names": self._get_alias_names,
            "countries": self._get_countries,
            "street": "INDIVIDUAL_ADDRESS/STREET",
            "city": "INDIVIDUAL_ADDRESS/CITY",
            "state_province": "INDIVIDUAL_ADDRESS/STATE_PROVINCE",
            "address_note": "INDIVIDUAL_ADDRESS/NOTE",
            "birth_dates": self._get_date_of_births,
            "country_of_birth": self._get_country_of_birth,
            "designation": self._get_designation,
            "documents": self._get_documents,
        }

    @staticmethod
    def _get_text_from_path(individual_tag: Element, path: str) -> str | None:
        tag = individual_tag.find(path)
        if isinstance(tag, Element):
            return tag.text
        return None

    @staticmethod
    def _get_designation(individual_tag: Element, *args: Any, **kwargs: Any) -> str | None:
        designation_tag_name = "DESIGNATION"
        designation_tag = individual_tag.find(designation_tag_name)
        if isinstance(designation_tag, Element):
            designations: list[str] = [value_tag.text for value_tag in individual_tag.find(designation_tag_name)]
            return " ".join(designations)
        return ""  # pragma: no cover

    def _get_date_of_births(
        self,
        individual_tag: Element,
        individual: "SanctionListIndividual",
        *args: Any,
        **kwargs: Any,
    ) -> "set[SanctionListIndividualDateOfBirth]":
        from hope.models.sanction_list import SanctionListIndividualDateOfBirth

        date_of_birth_tags = individual_tag.findall("INDIVIDUAL_DATE_OF_BIRTH")
        dates_of_birth = set()
        for date_of_birth_tag in date_of_birth_tags:
            type_of_date_tag = date_of_birth_tag.find("TYPE_OF_DATE")
            default_datetime = timezone.make_aware(datetime(year=2020, month=1, day=1))
            if isinstance(type_of_date_tag, Element) and type_of_date_tag.text:
                type_of_date = type_of_date_tag.text
                if type_of_date in ("EXACT", "APPROXIMATELY"):
                    date_tag = date_of_birth_tag.find("DATE")
                    year_tag = date_of_birth_tag.find("YEAR")
                    # this XML file is so weird that the date of birth
                    # can be placed in the NOTE tag
                    note_tag = date_of_birth_tag.find("NOTE")
                    value: str
                    if isinstance(date_tag, Element) and date_tag.text:
                        value = date_tag.text
                    elif isinstance(year_tag, Element) and year_tag.text:
                        value = year_tag.text
                    elif isinstance(note_tag, Element) and note_tag.text:
                        value = note_tag.text
                    try:
                        parsed_date = dateutil.parser.parse(value, default=default_datetime)
                        dates_of_birth.add(
                            SanctionListIndividualDateOfBirth(
                                individual=self._get_individual_from_db_or_file(individual),
                                date=parsed_date.date(),
                            )
                        )
                    except Exception:  # pragma: no cover
                        logger.log("Cannot parse date")
                elif type_of_date == "BETWEEN":
                    from_year: str = date_of_birth_tag.find("FROM_YEAR").text or ""
                    to_year: str = date_of_birth_tag.find("TO_YEAR").text or ""
                    years = {
                        SanctionListIndividualDateOfBirth(
                            individual=self._get_individual_from_db_or_file(individual),
                            date=date(year=year, month=1, day=1),
                        )
                        for year in range(int(from_year), int(to_year) + 1)
                    }
                    dates_of_birth.update(years)

        return dates_of_birth

    def _get_alias_names(
        self,
        individual_tag: Element,
        individual: "SanctionListIndividual",
        *args: Any,
        **kwargs: Any,
    ) -> "set[SanctionListIndividualAliasName]":
        from hope.models.sanction_list import SanctionListIndividualAliasName

        path = "INDIVIDUAL_ALIAS"
        alias_names_tags = individual_tag.findall(path)

        aliases = {}
        for tag in alias_names_tags:
            quality_tag = tag.find("QUALITY")
            alias_name_tag = tag.find("ALIAS_NAME")
            is_valid_quality_tag = isinstance(quality_tag, Element) and quality_tag.text
            is_valid_name_tag = isinstance(alias_name_tag, Element) and alias_name_tag.text
            if is_valid_quality_tag and is_valid_name_tag:
                individual_instance = self._get_individual_from_db_or_file(individual)
                unique_key = f"{alias_name_tag.text}-{str(individual_instance.id)}"
                if quality_tag.text.lower() in ("good", "a.k.a") and alias_name_tag.text:
                    aliases[unique_key] = SanctionListIndividualAliasName(
                        individual=individual_instance,
                        name=alias_name_tag.text,
                    )

        return set(aliases.values())

    @staticmethod
    def _get_country_field(individual_tag: Element, path: str, *args: Any, **kwargs: Any) -> str | None | set:
        tags = individual_tag.findall(path)

        countries = set()
        for tag in tags:
            if isinstance(tag, Element) and tag.text:
                alpha_2_code = Countries.get_country_value(tag.text)
                if not alpha_2_code:
                    continue
                if country := (Country.objects.get(iso_code2=alpha_2_code)):
                    countries.add(country)

        return countries or None

    def _get_countries(
        self,
        individual_tag: Element,
        individual: "SanctionListIndividual",
        *args: Any,
        **kwargs: Any,
    ) -> "set[SanctionListIndividualCountries]":
        from hope.models.sanction_list import SanctionListIndividualCountries

        path = "INDIVIDUAL_ADDRESS/COUNTRY"
        result = self._get_country_field(individual_tag, path)
        if result:
            return {
                SanctionListIndividualCountries(
                    individual=self._get_individual_from_db_or_file(individual),
                    country=country,
                )
                for country in result
            }
        return set()

    def _get_country_of_birth(self, individual_tag: Element, *args: Any, **kwargs: Any) -> str | None:
        path = "INDIVIDUAL_PLACE_OF_BIRTH/COUNTRY"
        countries = self._get_country_field(individual_tag, path)
        if isinstance(countries, set):
            return sorted(countries, key=lambda country: country.name).pop()
        return countries

    def _get_nationalities(
        self,
        individual_tag: Element,
        individual: "SanctionListIndividual",
        *args: Any,
        **kwargs: Any,
    ) -> "set[SanctionListIndividualNationalities]":
        from hope.models.sanction_list import SanctionListIndividualNationalities

        path = "NATIONALITY/VALUE"
        result = self._get_country_field(individual_tag, path)
        if result:
            return {
                SanctionListIndividualNationalities(
                    individual=self._get_individual_from_db_or_file(individual),
                    nationality=country,
                )
                for country in result
            }
        return set()

    def _get_documents(
        self,
        individual_tag: Element,
        individual: "SanctionListIndividual",
        *args: Any,
        **kwargs: Any,
    ) -> "set[SanctionListIndividualDocument]":
        from hope.models.sanction_list import SanctionListIndividualDocument

        document_tags = individual_tag.findall("INDIVIDUAL_DOCUMENT")
        documents = set()

        for document_tag in document_tags:
            document_number_tag = document_tag.find("NUMBER")
            type_of_document_tag = document_tag.find("TYPE_OF_DOCUMENT")
            issuing_country = self._get_country_field(document_tag, "ISSUING_COUNTRY")
            if isinstance(issuing_country, set):
                issuing_country = issuing_country.pop()
            date_of_issue_tag = document_tag.find("DATE_OF_ISSUE")
            date_of_issue = None
            if isinstance(date_of_issue_tag, Element):
                date_of_issue = self._cast_field_value_to_correct_type(
                    SanctionListIndividualDocument,
                    "date_of_issue",
                    date_of_issue_tag.text,
                )
            note_tag = document_tag.find("NOTE")
            note = ""
            if isinstance(note_tag, Element):
                note = self._cast_field_value_to_correct_type(
                    SanctionListIndividualDocument,
                    "note",
                    document_tag.find("NOTE"),
                )
            if isinstance(document_number_tag, Element) and isinstance(type_of_document_tag, Element):
                document = SanctionListIndividualDocument(
                    individual=self._get_individual_from_db_or_file(individual),
                    type_of_document=type_of_document_tag.text,
                    document_number=document_number_tag.text,
                    issuing_country=issuing_country,
                    date_of_issue=date_of_issue,
                    note=note,
                )
                documents.add(document)

        return documents

    def _get_individual_data(self, individual_tag: Element) -> dict:
        from hope.models.sanction_list import SanctionListIndividual

        individual_data_dict = {
            "individual": SanctionListIndividual(),
            "documents": None,
            "nationalities": None,
            "countries": None,
            "alias_names": None,
            "birth_dates": None,
        }
        individual = individual_data_dict["individual"]
        individual.active = True
        for field_name, path_or_func in self.VALUES_PATHS.items():
            if callable(path_or_func):
                value = path_or_func(individual_tag, individual)
            else:
                raw_value = self._get_text_from_path(individual_tag, path_or_func)
                value = self._cast_field_value_to_correct_type(SanctionListIndividual, field_name, raw_value)

            if hasattr(individual, field_name) and field_name not in individual_data_dict:
                setattr(individual, field_name, value)
            elif field_name in individual_data_dict:
                individual_data_dict[field_name] = value

        return individual_data_dict

    @cached_property
    def _get_individual_fields(self) -> list[str]:
        excluded_fields = {
            "id",
            "history",
            "documents",
            "nationalities",
            "countries",
            "alias_names",
            "dates_of_birth",
            "created_at",
            "updated_at",
        }
        all_fields = SanctionListIndividual._meta.get_fields(include_parents=False)
        return [field.name for field in all_fields if field.name not in excluded_fields and field.concrete is True]

    def _get_individual_from_db_or_file(
        self,
        individual: "SanctionListIndividual",
    ) -> "SanctionListIndividual":
        try:
            return SanctionListIndividual.all_objects.filter(sanction_list=self.sanction_list).get(
                reference_number=individual.reference_number
            )
        except ObjectDoesNotExist:
            return individual

    @cached_property
    def _get_all_individuals_from_db(self) -> QuerySet:
        return SanctionListIndividual.all_objects.filter(sanction_list=self.sanction_list).defer("documents")

    def _get_existing_individuals(self, individuals_reference_numbers: set[str]) -> QuerySet:
        return self._get_all_individuals_from_db.filter(reference_number__in=individuals_reference_numbers)

    def _get_individuals_to_create(
        self, individuals_from_file: "Iterable[SanctionListIndividual]"
    ) -> "set[SanctionListIndividual]":
        individuals_reference_numbers = self._get_reference_numbers_list(individuals_from_file)
        return {
            individual
            for individual in individuals_from_file
            if individual.reference_number
            not in self._get_existing_individuals(individuals_reference_numbers).values_list(
                "reference_number", flat=True
            )
        }

    def _get_individuals_to_update(self, individuals_from_file: Iterable) -> "set[SanctionListIndividual]":
        individuals_to_update = set()
        individuals_reference_numbers = self._get_reference_numbers_list(individuals_from_file)
        for individual in individuals_from_file:
            new_individual_data_dict = model_to_dict(individual, fields=self._get_individual_fields)
            old_individual = (
                self._get_existing_individuals(individuals_reference_numbers)
                .filter(reference_number=new_individual_data_dict["reference_number"])
                .first()
            )
            if old_individual:
                old_individual_data_dict = model_to_dict(old_individual, fields=self._get_individual_fields)
                if new_individual_data_dict != old_individual_data_dict:
                    obj = SanctionListIndividual.all_objects.get(reference_number=individual.reference_number)
                    individual.id = obj.id
                    individuals_to_update.add(individual)

        return individuals_to_update

    def _get_individuals_to_deactivate(self, individuals_from_file: "Iterable[SanctionListIndividual]") -> QuerySet:
        individuals_reference_numbers = self._get_reference_numbers_list(individuals_from_file)
        return self._get_all_individuals_from_db.difference(
            self._get_existing_individuals(individuals_reference_numbers)
        ).values_list("id", flat=True)
        # need to return id's calling delete() on qs set all to inactive state

    @staticmethod
    def _get_reference_numbers_list(
        individuals_from_file: "Iterable[SanctionListIndividual]",
    ) -> set[str]:
        return {i.reference_number for i in individuals_from_file}

    @staticmethod
    def _cast_field_value_to_correct_type(model: Any, field_name: str, value: Any) -> Any:
        field = model._meta.get_field(field_name)
        # silencing lxml warning
        with open(os.devnull, "w") as devnull, contextlib.redirect_stderr(devnull):
            if not value:
                return field.default
        if field.get_internal_type() == "DateTimeField":
            year, month, day, *time = value.split("-")
            return timezone.make_aware(
                datetime(
                    year=int(year),
                    month=int(month),
                    day=int(day),
                ),
            )

        correct_value = field.to_python(value)

        if isinstance(correct_value, str):
            correct_value = correct_value.strip()

        return correct_value

    def load_from_file(self, file_path: str | Path) -> None:
        tree = ElementTree.parse(str(file_path))
        root = tree.getroot()
        self.parse(root)

    def load_from_url(self) -> None:  # pragma: no cover
        parsed_url = urlparse(self.url)
        if parsed_url.scheme not in ["http", "https"]:
            raise ValueError("The URL scheme is not permitted. Only 'http' and 'https' are allowed.")
        url = urlopen(self.url)  # noqa: S310
        tree = ElementTree.parse(url)
        root = tree.getroot()
        self.parse(root)

    def execute(self) -> None:  # pragma: no cover
        raise DeprecationWarning()

    def parse(self, root: Element) -> None:
        individuals_from_file = set()
        documents_from_file = set()
        nationalities_from_file = set()
        countries_from_file = set()
        aliases_from_file = set()
        dob_from_file = set()

        for individual_tag in root.findall(self.INDIVIDUAL_TAG_PATH):
            individual_data_dict = self._get_individual_data(individual_tag)
            individual = individual_data_dict["individual"]
            individual.sanction_list = self.sanction_list
            individual.full_name = (
                (f"{individual.first_name} {individual.second_name} {individual.third_name} {individual.fourth_name}")
                .strip()
                .title()
            )
            individuals_from_file.add(individual)

            documents_from_file.update(individual_data_dict["documents"])
            nationalities_from_file.update(individual_data_dict["nationalities"])
            countries_from_file.update(individual_data_dict["countries"])
            aliases_from_file.update(individual_data_dict["alias_names"])
            dob_from_file.update(individual_data_dict["birth_dates"])

        individuals_to_create = self._get_individuals_to_create(individuals_from_file)
        SanctionListIndividual.all_objects.bulk_create(individuals_to_create)

        individuals_to_update = self._get_individuals_to_update(individuals_from_file)

        if individuals_to_update:
            SanctionListIndividual.all_objects.bulk_update(
                self._get_individuals_to_update(individuals_from_file),
                self._get_individual_fields,
                1000,
            )
        individuals_ids_to_delete = self._get_individuals_to_deactivate(individuals_from_file)
        SanctionListIndividual.objects.filter(
            sanction_list=self.sanction_list, id__in=individuals_ids_to_delete
        ).delete()

        # SanctionListIndividualDocument
        if documents_from_file:
            for single_doc in documents_from_file:
                SanctionListIndividualDocument.objects.get_or_create(
                    individual=single_doc.individual,
                    document_number=single_doc.document_number,
                    type_of_document=single_doc.type_of_document,
                    date_of_issue=single_doc.date_of_issue,
                    issuing_country=single_doc.issuing_country,
                    note=single_doc.note,
                )

        # SanctionListIndividualCountries
        SanctionListIndividualCountries.objects.filter(individual__sanction_list=self.sanction_list).delete()
        if countries_from_file:
            SanctionListIndividualCountries.objects.bulk_create(countries_from_file)

        # SanctionListIndividualNationalities

        SanctionListIndividualNationalities.objects.filter(individual__sanction_list=self.sanction_list).delete()
        if nationalities_from_file:
            SanctionListIndividualNationalities.objects.bulk_create(nationalities_from_file)

        # SanctionListIndividualAliasName
        SanctionListIndividualAliasName.objects.filter(individual__sanction_list=self.sanction_list).delete()
        if aliases_from_file:
            SanctionListIndividualAliasName.objects.bulk_create(aliases_from_file)

        # SanctionListIndividualDateOfBirth
        if dob_from_file:
            for single_dob in dob_from_file:
                SanctionListIndividualDateOfBirth.objects.get_or_create(
                    individual=single_dob.individual,
                    date=single_dob.date,
                )

        try:
            cls_un = UNSanctionList
            programs = Program.objects.filter(
                sanction_lists__strategy=f"{cls_un.__module__}.{cls_un.__qualname__}"
            )  # get programs which use sanction list which is using this strategy
            for program in programs:
                check_against_sanction_list_pre_merge(program_id=program.id)
        except NotFoundError:  # pragma: no cover
            pass


class UNSanctionList(BaseSanctionList):
    def refresh(self) -> None:  # pragma: no cover
        LoadSanctionListXMLTask(sanction_list=self.context, **self.context.config).load_from_url()
