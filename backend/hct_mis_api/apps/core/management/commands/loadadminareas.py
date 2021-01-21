from django.core.management import BaseCommand
from django.db.models import Q
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.account.models import Role, IncompatibleRoles


class Command(BaseCommand):
    help = "Generate roles"

    def add_arguments(self, parser):

        parser.add_argument(
            "--bussines_area",
            dest="file",
            action="store",
            nargs="?",
            type=str,
            help="bussines_area",
        )

    def handle(self, *args, **options):
