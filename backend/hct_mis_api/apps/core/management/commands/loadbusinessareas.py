import logging
import xml.etree.ElementTree as ET

from django.core.management import BaseCommand

from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.geo.models import Country

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "load_business_areas"

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            dest="file",
            action="store",
            nargs="?",
            default="./data/GetBusinessAreaList_XML.xml",
            type=str,
            help="file",
        )

    def handle(self, *args, **options):
        """
        <DocumentElement>
            <BusinessArea>
                <BUSINESS_AREA_CODE>8970</BUSINESS_AREA_CODE>
                <BUSINESS_AREA_NAME>Serbia</BUSINESS_AREA_NAME>
                <BUSINESS_AREA_LONG_NAME>THE REPUBLIC OF SERBIA</BUSINESS_AREA_LONG_NAME>
                <REGION_CODE>66</REGION_CODE>
                <REGION_NAME>ECAR</REGION_NAME>
            </BusinessArea>
        </DocumentElement>
        :param args:
        :param options:
        :return:
        """
        file = options["file"]
        tree = ET.parse(file)
        root = tree.getroot()

        for business_area_tag in root:
            business_area, _ = BusinessArea.objects.get_or_create(
                code=business_area_tag.find("BUSINESS_AREA_CODE").text,
                defaults=dict(
                    name=business_area_tag.find("BUSINESS_AREA_NAME").text,
                    long_name=business_area_tag.find("BUSINESS_AREA_LONG_NAME").text,
                    region_code=business_area_tag.find("REGION_CODE").text,
                    region_name=business_area_tag.find("REGION_NAME").text,
                    has_data_sharing_agreement=True,
                ),
            )

            if country := Country.objects.filter(name=business_area.name).first():
                business_area.countries.add(country)
        BusinessArea.objects.get_or_create(
            code="GLOBAL",
            defaults=dict(
                name="Global",
                long_name="Global Business Area",
                region_code="GLOBAL",
                region_name="GLOBAL",
                has_data_sharing_agreement=True,
            ),
        )
        logger.debug(f"Imported business areas from {file}")
