import xml.etree.ElementTree as ET
from datetime import datetime, date
from typing import Union, Tuple, Any, Set, List, Iterable
from urllib.request import urlopen

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import QuerySet
from django.forms import model_to_dict
from django.utils.functional import cached_property

from core.countries import Countries
from sanction_list.models import (
    SanctionListIndividual,
    SanctionListIndividualDocument,
    SanctionListIndividualNationalities,
    SanctionListIndividualCountries,
)


class LoadSanctionListXMLTask:
    SANCTION_LIST_XML_URL = (
        "https://scsanctions.un.org/resources/xml/en/consolidated.xml"
    )

    INDIVIDUAL_TAG_PATH = "INDIVIDUALS/INDIVIDUAL"

    def __init__(self, file_path=None):
        self.file_path = file_path

        self.VALUES_PATHS = {
            "data_id": "DATAID",
            "version_num": "VERSIONNUM",
            "first_name": "FIRST_NAME",
            "second_name": "SECOND_NAME",
            "third_name": "THIRD_NAME",
            "un_list_type": "UN_LIST_TYPE",
            "reference_number": "REFERENCE_NUMBER",
            "listed_on": "LISTED_ON",
            "comments": "COMMENTS1",
            "nationality": self._get_nationalities,
            "list_type": "LIST_TYPE/VALUE",
            "quality": "INDIVIDUAL_ALIAS/QUALITY",
            "alias_name": "INDIVIDUAL_ALIAS/ALIAS_NAME",
            "country": self._get_countries,
            "street": "INDIVIDUAL_ADDRESS/STREET",
            "city": "INDIVIDUAL_ADDRESS/CITY",
            "state_province": "INDIVIDUAL_ADDRESS/STATE_PROVINCE",
            "address_note": "INDIVIDUAL_ADDRESS/NOTE",
            "date_of_birth": "INDIVIDUAL_DATE_OF_BIRTH/DATE",
            "year_of_birth": "INDIVIDUAL_DATE_OF_BIRTH/YEAR",
            "country_of_birth": self._get_country_of_birth,
            "designation": self._get_designation,
            "exact_date": self._get_exact_date,
        }

    @staticmethod
    def _get_text_from_path(individual_tag: ET.Element, path: str) -> str:
        tag = individual_tag.find(path)
        if isinstance(tag, ET.Element):
            return tag.text

    @staticmethod
    def _get_designation(individual_tag: ET.Element) -> Union[str, None]:
        designation_tag_name = "DESIGNATION"
        designation_tag = individual_tag.find(designation_tag_name)
        if isinstance(designation_tag, ET.Element):
            designations = [
                value_tag.text
                for value_tag in individual_tag.find(designation_tag_name)
            ]
            return " ".join(designations)
        return ""

    @staticmethod
    def _get_exact_date(individual_tag: ET.Element) -> Union[bool, None]:
        exact_date_tag_name = "INDIVIDUAL_DATE_OF_BIRTH/TYPE_OF_DATE"
        exact_date = individual_tag.find(exact_date_tag_name)
        if isinstance(exact_date, ET.Element):
            return True if exact_date == "EXACT" else False
        return True

    @staticmethod
    def _get_country_field(
        individual_tag: ET.Element, path: str
    ) -> Union[str, None, Set]:
        tags = individual_tag.findall(path)

        countries = set()
        for tag in tags:
            if isinstance(tag, ET.Element) and tag.text:
                alpha_2_code = Countries.get_country_value(tag.text)
                if alpha_2_code is not None:
                    countries.add(alpha_2_code)

        if countries:
            return countries
        else:
            return ""

    def _get_countries(self, individual_tag: ET.Element) -> str:
        path = "INDIVIDUAL_ADDRESS/COUNTRY"
        return self._get_country_field(individual_tag, path)

    def _get_country_of_birth(self, individual_tag: ET.Element) -> str:
        path = "INDIVIDUAL_PLACE_OF_BIRTH/COUNTRY"
        countries = self._get_country_field(individual_tag, path)
        if isinstance(countries, set):
            return countries.pop()
        else:
            return countries

    def _get_nationalities(self, individual_tag: ET.Element) -> Union[str, Set]:
        path = "NATIONALITY/VALUE"
        return self._get_country_field(individual_tag, path)

    def _get_documents(
        self, individual_tag: ET.Element, individual: SanctionListIndividual
    ) -> Set[SanctionListIndividualDocument]:
        document_tags = individual_tag.findall("INDIVIDUAL_DOCUMENT")
        documents = set()

        for document_tag in document_tags:
            document_number_tag = document_tag.find("NUMBER")
            type_of_document_tag = document_tag.find("TYPE_OF_DOCUMENT")
            issuing_country = self._get_country_field(
                document_tag, "ISSUING_COUNTRY"
            )
            if isinstance(issuing_country, set):
                issuing_country = issuing_country.pop()
            date_of_issue_tag = document_tag.find("DATE_OF_ISSUE")
            date_of_issue = None
            if isinstance(date_of_issue_tag, ET.Element):
                date_of_issue = self._cast_field_value_to_correct_type(
                    SanctionListIndividualDocument,
                    "date_of_issue",
                    date_of_issue_tag.text,
                )
            note_tag = document_tag.find("NOTE")
            note = ""
            if isinstance(note_tag, ET.Element):
                note = self._cast_field_value_to_correct_type(
                    SanctionListIndividualDocument,
                    "note",
                    document_tag.find("NOTE"),
                )
            if isinstance(document_number_tag, ET.Element) and isinstance(
                type_of_document_tag, ET.Element
            ):
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

    def _get_individual_data(
        self, individual_tag: ET.Element
    ) -> Tuple[
        SanctionListIndividual,
        Set[SanctionListIndividualDocument],
        Set[SanctionListIndividualNationalities],
        Set[SanctionListIndividualCountries],
    ]:
        individual = SanctionListIndividual()
        individual.active = True
        for field_name, path_or_func in self.VALUES_PATHS.items():
            if callable(path_or_func):
                value = path_or_func(individual_tag)
            else:
                raw_value = self._get_text_from_path(
                    individual_tag, path_or_func
                )
                value = self._cast_field_value_to_correct_type(
                    SanctionListIndividual, field_name, raw_value
                )
            if hasattr(individual, field_name):
                setattr(individual, field_name, value)

        nationalities_codes = self._get_nationalities(individual_tag)
        countries_codes = self._get_countries(individual_tag)
        nationalities = set()
        countries = set()
        if nationalities_codes:
            nationalities = set(
                SanctionListIndividualNationalities(
                    individual=self._get_individual_from_db_or_file(individual),
                    nationality=alpha2,
                )
                for alpha2 in nationalities_codes
            )
            countries = set(
                SanctionListIndividualCountries(
                    individual=self._get_individual_from_db_or_file(individual),
                    country=alpha2,
                )
                for alpha2 in countries_codes
            )
        documents = self._get_documents(individual_tag, individual)

        return individual, documents, nationalities, countries

    @cached_property
    def _get_individual_fields(self) -> List[str]:
        excluded_fields = {
            "id",
            "history",
            "documents",
            "nationalities",
            "countries",
            "created_at",
            "updated_at",
        }
        all_fields = SanctionListIndividual._meta.get_fields(
            include_parents=False
        )

        return [
            field.name
            for field in all_fields
            if field.name not in excluded_fields
        ]

    @staticmethod
    def _get_individual_from_db_or_file(
        individual: SanctionListIndividual,
    ) -> SanctionListIndividual:
        try:
            return SanctionListIndividual.all_objects.get(
                reference_number=individual.reference_number
            )
        except ObjectDoesNotExist:
            return individual

    @cached_property
    def _get_all_individuals_from_db(self) -> QuerySet:
        return SanctionListIndividual.all_objects.defer("documents")

    def _get_existing_individuals(
        self, individuals_reference_numbers: Set[str]
    ) -> QuerySet:
        return self._get_all_individuals_from_db.filter(
            reference_number__in=individuals_reference_numbers
        )

    def _get_individuals_to_create(
        self, individuals_from_file: Iterable[SanctionListIndividual]
    ) -> Set[SanctionListIndividual]:
        individuals_reference_numbers = self._get_reference_numbers_list(
            individuals_from_file
        )
        return {
            individual
            for individual in individuals_from_file
            if individual.reference_number
            not in self._get_existing_individuals(
                individuals_reference_numbers
            ).values_list("reference_number", flat=True)
        }

    def _get_individuals_to_update(
        self, individuals_from_file: Iterable[SanctionListIndividual]
    ) -> Set[SanctionListIndividual]:
        individuals_to_update = set()
        individuals_reference_numbers = self._get_reference_numbers_list(
            individuals_from_file
        )
        for individual in individuals_from_file:
            fields_dict = model_to_dict(
                individual, fields=self._get_individual_fields
            )
            exists = (
                self._get_existing_individuals(individuals_reference_numbers)
                .filter(**fields_dict)
                .exists()
            )
            if not exists:
                obj = SanctionListIndividual.all_objects.get(
                    reference_number=individual.reference_number
                )
                individual.id = obj.id
                individuals_to_update.add(individual)

        return individuals_to_update

    def _get_individuals_to_deactivate(
        self, individuals_from_file: Iterable[SanctionListIndividual]
    ) -> List[str]:
        individuals_reference_numbers = self._get_reference_numbers_list(
            individuals_from_file
        )
        ids = self._get_all_individuals_from_db.difference(
            self._get_existing_individuals(individuals_reference_numbers)
        ).values_list("id", flat=True)
        # need to return id's calling delete() on qs set all to inactive state
        return ids

    @staticmethod
    def _get_reference_numbers_list(
        individuals_from_file: Iterable[SanctionListIndividual],
    ) -> Set[str]:
        return {i.reference_number for i in individuals_from_file}

    @staticmethod
    def _cast_field_value_to_correct_type(model, field_name: str, value: Any):
        field = model._meta.get_field(field_name)
        if not value:
            return field.default

        if field.get_internal_type() == "DateTimeField":
            year, month, day, *time = value.split("-")
            if time:
                hour, minute = time[0].split(":")
                return datetime(
                    year=int(year),
                    month=int(month),
                    day=int(day),
                    hour=int(hour),
                    minute=int(minute),
                )
        if field.get_internal_type() == "DateField":
            year, month, day, *time = value.split("-")
            return date(year=int(year), month=int(month), day=int(day))

        return field.to_python(value)

    def execute(self):
        if self.file_path is not None:
            tree = ET.parse(self.file_path)
        else:
            url = urlopen(self.SANCTION_LIST_XML_URL)
            tree = ET.parse(url)
        root = tree.getroot()

        individuals_from_file = set()
        documents_from_file = set()
        nationalities_from_file = set()
        countries_from_file = set()

        for individual_tag in root.findall(self.INDIVIDUAL_TAG_PATH):
            (
                individual,
                documents,
                nationalities,
                countries,
            ) = self._get_individual_data(individual_tag)
            individuals_from_file.add(individual)
            documents_from_file.update(documents)
            nationalities_from_file.update(nationalities)
            countries_from_file.update(countries)

        # SanctionListIndividual
        SanctionListIndividual.all_objects.bulk_create(
            self._get_individuals_to_create(individuals_from_file)
        )

        individuals_to_update = self._get_individuals_to_update(
            individuals_from_file
        )

        if individuals_to_update:
            SanctionListIndividual.all_objects.bulk_update(
                self._get_individuals_to_update(individuals_from_file),
                self._get_individual_fields,
                1000,
            )
        individuals_ids_to_delete = self._get_individuals_to_deactivate(
            individuals_from_file
        )
        SanctionListIndividual.objects.filter(
            id__in=individuals_ids_to_delete
        ).delete()

        # SanctionListIndividualDocument
        SanctionListIndividualDocument.objects.all().delete()
        SanctionListIndividualDocument.objects.bulk_create(documents_from_file)

        # SanctionListIndividualCountries
        SanctionListIndividualCountries.objects.all().delete()
        SanctionListIndividualCountries.objects.bulk_create(countries_from_file)

        # SanctionListIndividualNationalities
        SanctionListIndividualNationalities.objects.all().delete()
        SanctionListIndividualNationalities.objects.bulk_create(
            nationalities_from_file
        )
