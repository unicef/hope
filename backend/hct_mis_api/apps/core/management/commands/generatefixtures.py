from django.core.management import BaseCommand

from program.fixtures import CashPlanFactory


class Command(BaseCommand):
    help = "Generate fixtures data for project"

    def add_arguments(self, parser):
        parser.add_argument(
            "--objects-num",
            dest="amount",
            const=10,
            default=10,
            action="store",
            nargs="?",
            type=int,
            help="Creates provided amount of fixture objects.",
        )

    def handle(self, *args, **options):
        # TODO: should be changed in future to allow more options
        CashPlanFactory.create_batch(options["amount"])
