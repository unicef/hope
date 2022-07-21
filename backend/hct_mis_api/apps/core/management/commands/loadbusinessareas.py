import logging
import xml.etree.ElementTree as ET

from django.core.management import BaseCommand

from hct_mis_api.apps.core.models import AdminAreaLevel, BusinessArea
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
        # Using xml.etree.ElementTree.parse to parse untrusted XML data is known to be vulnerable to XML attacks. Replace xml.etree.ElementTree.parse with its defusedxml equivalent function or make sure defusedxml.defuse_stdlib() is called
        tree = ET.parse(file)  # nosec
        root = tree.getroot()

        for business_area_tag in root:
            business_area, _ = BusinessArea.objects.get_or_create(
                code=business_area_tag.find("BUSINESS_AREA_CODE").text,
                defaults={
                    "name": business_area_tag.find("BUSINESS_AREA_NAME").text,
                    "long_name": business_area_tag.find("BUSINESS_AREA_LONG_NAME").text,
                    "region_code": business_area_tag.find("REGION_CODE").text,
                    "region_name": business_area_tag.find("REGION_NAME").text,
                    "has_data_sharing_agreement": True,
                },
            )

            country = AdminAreaLevel.objects.filter(admin_level=0, country_name=business_area.name).first()
            country_new = Country.objects.filter(name=business_area.name).first()
            if country:
                business_area.countries.add(country)
            if country_new:
                business_area.countries_new.add(country_new)
        BusinessArea.objects.get_or_create(
            code="GLOBAL",
            defaults={
                "name": "Global",
                "long_name": "Global Business Area",
                "region_code": "GLOBAL",
                "region_name": "GLOBAL",
                "has_data_sharing_agreement": True,
            },
        )
        logger.debug(f"Imported business areas from {file}")
