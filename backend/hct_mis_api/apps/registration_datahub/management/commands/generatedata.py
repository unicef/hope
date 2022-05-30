from django.core.management import BaseCommand
from django.db import transaction

from openpyxl.writer.excel import save_workbook

from hct_mis_api.apps.core.core_fields_attributes import (
    COLLECTORS_FIELDS,
    core_fields_to_separated_dict,
)
from hct_mis_api.apps.core.models import AdminArea
from hct_mis_api.apps.core.utils import serialize_flex_attributes
from hct_mis_api.apps.household.fixtures import (
    create_household_for_fixtures,
    create_individual_document,
)
from hct_mis_api.apps.household.models import (
    IDENTIFICATION_TYPE_BIRTH_CERTIFICATE,
    IDENTIFICATION_TYPE_DRIVERS_LICENSE,
    IDENTIFICATION_TYPE_ELECTORAL_CARD,
    IDENTIFICATION_TYPE_NATIONAL_ID,
    IDENTIFICATION_TYPE_NATIONAL_PASSPORT,
    IDENTIFICATION_TYPE_OTHER,
)
from hct_mis_api.apps.registration_datahub.template_generator import (
    TemplateFileGenerator,
)

document_fields = {
    "birth_certificate_no": {
        "type": IDENTIFICATION_TYPE_BIRTH_CERTIFICATE,
        "value": lambda arg: arg.document_number,
    },
    "drivers_license_no": {
        "type": IDENTIFICATION_TYPE_DRIVERS_LICENSE,
        "value": lambda arg: arg.document_number,
    },
    "national_id_no": {
        "type": IDENTIFICATION_TYPE_NATIONAL_ID,
        "value": lambda arg: arg.document_number,
    },
    "national_passport": {
        "type": IDENTIFICATION_TYPE_NATIONAL_PASSPORT,
        "value": lambda arg: arg.document_number,
    },
    "electoral_card_no": {
        "type": IDENTIFICATION_TYPE_ELECTORAL_CARD,
        "value": lambda arg: arg.document_number,
    },
    "other_id_no": {
        "type": IDENTIFICATION_TYPE_OTHER,
        "value": lambda arg: arg.document_number,
    },
    "birth_certificate_issuer": {
        "type": IDENTIFICATION_TYPE_BIRTH_CERTIFICATE,
        "value": lambda arg: arg.type.country.alpha3,
    },
    "drivers_license_issuer": {
        "type": IDENTIFICATION_TYPE_DRIVERS_LICENSE,
        "value": lambda arg: arg.type.country.alpha3,
    },
    "national_id_issuer": {"type": IDENTIFICATION_TYPE_NATIONAL_ID, "value": lambda arg: arg.type.country.alpha3},
    "national_passport_issuer": {
        "type": IDENTIFICATION_TYPE_NATIONAL_PASSPORT,
        "value": lambda arg: arg.type.country.alpha3,
    },
    "electoral_card_issuer": {"type": IDENTIFICATION_TYPE_ELECTORAL_CARD, "value": lambda arg: arg.type.country.alpha3},
    "other_id_issuer": {"type": IDENTIFICATION_TYPE_OTHER, "value": lambda arg: arg.type.country.alpha3},
}


class DataGenerator:
    household_defaults = {
        "collect_individual_data": "1",
        "country": "AFG",
        "country_origin": "AFG",
    }

    def __init__(self, number_of_households):
        self.number_of_households = number_of_households
        self._fetch_fields()
        self._create_initial_template()

    def _fetch_fields(self):
        core_fields = core_fields_to_separated_dict()
        flex_fields = serialize_flex_attributes()
        self.household_fields = list(core_fields["households"].values())[1:]
        self.household_fields += list(flex_fields["households"].values())
        self.individual_fields = list(core_fields["individuals"].values())[1:]
        self.individual_fields += list(COLLECTORS_FIELDS.values())
        self.individual_fields += list(flex_fields["individuals"].values())

    def _create_initial_template(self):
        self.wb = TemplateFileGenerator.get_template_file()
        self.ws_households = self.wb["Households"]
        self.ws_individuals = self.wb["Individuals"]

    def generate(self):
        with transaction.atomic():
            sid = transaction.savepoint()

            for household_id in range(1, self.number_of_households + 1):
                household, individuals = self._create_household_with_individuals()
                household_row = self._prepare_household_row(household, household_id)

                for index, individual in enumerate(individuals):
                    individual_row = self._prepare_individual_row(household_id, index, individual)
                    self.ws_individuals.append(individual_row)
                self.ws_households.append(household_row)
            save_workbook(self.wb, "imported_data.xlsx")
            transaction.savepoint_rollback(sid)

    def _create_household_with_individuals(self):
        household_args = {
            **self.household_defaults,
            "admin_area": AdminArea.objects.order_by("?")[0],
            "size": 4,
        }
        household, individuals = create_household_for_fixtures(household_args)
        for individual in individuals:
            [create_individual_document(individual) for _ in range(3)]
        return household, individuals

    def _prepare_individual_row(self, household_id, index, individual):
        individual_row = [household_id]
        for individual_field in self.individual_fields:
            fields = individual_field.get("name", "").split("__")
            value = ""
            if fields:
                value = individual
                for field in fields:
                    if value:
                        value = getattr(value, field, None) or ""
                    if (field == "primary_collector_id" and index == 0) or (
                        field == "alternate_collector_id" and index == 1
                    ):
                        value = household_id
                    elif field in document_fields:
                        document_type = document_fields[field]["type"]
                        get_value = document_fields[field]["value"]
                        document = individual.documents.filter(type__type=document_type).first()
                        value = document and get_value(document) or ""
            individual_row.append(str(value))
        return individual_row

    def _prepare_household_row(self, household, household_id):
        household_row = [household_id]
        for household_field in self.household_fields:
            fields = household_field.get("name", "").split("__")
            value = ""
            if fields:
                value = household
                for field in fields:
                    if value:
                        value = getattr(value, field, None) or ""
                    if field == "consent_sharing":
                        value = ",".join(value)
                    elif value and field in ["admin1", "admin2"]:
                        value = value.p_code
                    elif value and field in ["country", "country_origin"]:
                        value = value.alpha3
            household_row.append(str(value))
        return household_row


class Command(BaseCommand):
    help = "Generate data (household, individuals and documents)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--number",
            dest="number",
            default=100,
            action="store",
            nargs="?",
            type=int,
            help="Creates provided amount of household objects.",
        )

    def handle(self, *args, **options):
        print("Generating data - start")
        DataGenerator(options["number"]).generate()
        print("Generating data - stop")
