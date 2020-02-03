from django.core.management import BaseCommand

from account.fixtures import UserFactory
from core.models import BusinessArea
from payment.fixtures import PaymentRecordFactory
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

        parser.add_argument(
            "--payment-record",
            dest="payment_record_amount",
            const=10,
            default=10,
            action="store",
            nargs="?",
            type=int,
            help="Creates provided amount of payment records assigned to "
            "household and cash plan.",
        )

    def handle(self, *args, **options):
        cash_plans_amount = options["cash_plans_amount"]
        programs_amount = options["programs_amount"]
        payment_record_amount = options["payment_record_amount"]

        for _ in range(programs_amount):
            user = UserFactory.create()
            program = ProgramFactory(business_area=BusinessArea.objects.order_by('?').first())

            for _ in range(cash_plans_amount):
                cash_plan = CashPlanFactory.create(
                    program=program, created_by=user
                )
                for _ in range(payment_record_amount):
                    PaymentRecordFactory.create(cash_plan=cash_plan)

        self.stdout.write(
            f"Generated {programs_amount} Programs "
            f" {cash_plans_amount} Cash Plans for each Program"
            f" (total Cash Plans: {cash_plans_amount * programs_amount})"
            f" {payment_record_amount} Payment Records for each Cash Plan"
            f" (total Payment Record: "
            f"{(cash_plans_amount * programs_amount) * payment_record_amount})"
        )
