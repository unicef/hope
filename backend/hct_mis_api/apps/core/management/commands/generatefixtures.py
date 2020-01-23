from django.core.management import BaseCommand

from account.fixtures import UserFactory
from program.fixtures import CashPlanFactory, ProgramFactory


class Command(BaseCommand):
    help = "Generate fixtures data for project"

    def add_arguments(self, parser):
        parser.add_argument(
            "--program",
            dest="programs_amount",
            const=10,
            default=10,
            action="store",
            nargs="?",
            type=int,
            help="Creates provided amount of program objects.",
        )

        parser.add_argument(
            "--cash-plan",
            dest="cash_plans_amount",
            const=10,
            default=10,
            action="store",
            nargs="?",
            type=int,
            help="Creates provided amount of cash plans for one program.",
        )

    def handle(self, *args, **options):
        cash_plans_amount = options["cash_plans_amount"]
        programs_amount = options["programs_amount"]

        for program in range(programs_amount):
            user = UserFactory.create()
            program_obj = ProgramFactory()

            for cash_plan in range(cash_plans_amount):
                CashPlanFactory.create(program=program_obj, created_by=user)

        self.stdout.write(
            f"Generated {programs_amount} Programs "
            f" and {cash_plans_amount} Cash Plans for each Program"
            f" (total Cash Plans: {cash_plans_amount * programs_amount})"
        )
