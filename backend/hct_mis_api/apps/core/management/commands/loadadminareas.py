from django.core.management import BaseCommand

from hct_mis_api.apps.core.datamart.api import DatamartAPI
from hct_mis_api.apps.core.models import BusinessArea


class Command(BaseCommand):
    help = "Load Admin Areas"

    def add_arguments(self, parser):

        parser.add_argument(
            "--business_area",
            dest="business_area",
            action="store",
            nargs=1,
            type=str,
            help="business_area",
        )

    def handle(self, *args, **options):
        business_area = BusinessArea.objects.filter(name=options["business_area"][0]).first()
        api = DatamartAPI()
        locations = api.get_locations_geo_data(business_area)
        admin_areas = api.generate_admin_areas(locations, business_area)
