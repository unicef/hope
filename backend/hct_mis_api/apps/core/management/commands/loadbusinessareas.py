import xml.etree.ElementTree as ET

from django.core.management import BaseCommand

from core.models import BusinessArea
import logging


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
            business_area = BusinessArea(
                code=business_area_tag.find("BUSINESS_AREA_CODE").text,
                name=business_area_tag.find("BUSINESS_AREA_NAME").text,
                long_name=business_area_tag.find(
                    "BUSINESS_AREA_LONG_NAME"
                ).text,
                region_code=business_area_tag.find("REGION_CODE").text,
                region_name=business_area_tag.find("REGION_NAME").text,
            )
            business_area.save()
        logger.debug(f"Imported business areas from {file}")
