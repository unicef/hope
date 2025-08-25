import datetime
import io
from collections import namedtuple
from decimal import Decimal
from typing import Tuple

import pytz
from extras.test_utils.factories.account import PartnerFactory, UserFactory
from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.household import (
    IndividualRoleInHouseholdFactory,
    create_household_and_individuals,
)
from extras.test_utils.factories.payment import (
    PaymentFactory,
    PaymentPlanFactory,
    PaymentVerificationFactory,
    PaymentVerificationPlanFactory,
    PaymentVerificationSummaryFactory,
    generate_delivery_mechanisms,
)
from extras.test_utils.factories.program import ProgramFactory
from extras.test_utils.factories.registration_data import RegistrationDataImportFactory
from parameterized import parameterized

from hope.apps.account.permissions import Permissions
from hope.apps.core.base_test_case import BaseTestCase
from hope.models.core import DataCollectingType
from hope.models.household import ROLE_PRIMARY
from hope.apps.payment.models import (
    Payment,
    PaymentPlan,
    PaymentVerification,
    PaymentVerificationPlan,
)
from hope.apps.payment.xlsx.xlsx_payment_plan_per_fsp_import_service import (
    XlsxPaymentPlanImportPerFspService,
)
from hope.models.program import Program


class TestPaymentPlanReconciliation(BaseTestCase):
    @classmethod
    def create_household_and_individual(cls, program: Program) -> Tuple["Household", "Individual"]:
        household, individuals = create_household_and_individuals(
            household_data={
                "registration_data_import": cls.registration_data_import,
                "business_area": cls.business_area,
                "program": program,
            },
            individuals_data=[{}],
        )
        IndividualRoleInHouseholdFactory(household=household, individual=individuals[0], role=ROLE_PRIMARY)
        return household, individuals[0]

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.business_area = create_afghanistan()
        partner = PartnerFactory(name="Partner")
        cls.user = UserFactory.create(partner=partner)
        cls.all_necessary_permissions = [
            Permissions.PM_CREATE,
            Permissions.PM_VIEW_DETAILS,
            Permissions.PM_VIEW_LIST,
            Permissions.PM_IMPORT_XLSX_WITH_ENTITLEMENTS,
            Permissions.PM_APPLY_RULE_ENGINE_FORMULA_WITH_ENTITLEMENTS,
            Permissions.PROGRAMME_CREATE,
            Permissions.PROGRAMME_UPDATE,
            Permissions.PROGRAMME_ACTIVATE,
            Permissions.PM_PROGRAMME_CYCLE_CREATE,
            Permissions.PM_PROGRAMME_CYCLE_UPDATE,
            Permissions.TARGETING_CREATE,
            Permissions.TARGETING_LOCK,
            Permissions.TARGETING_SEND,
            Permissions.PM_LOCK_AND_UNLOCK,
            Permissions.PM_LOCK_AND_UNLOCK_FSP,
            Permissions.PM_SEND_FOR_APPROVAL,
            Permissions.PM_ACCEPTANCE_PROCESS_APPROVE,
            Permissions.PM_ACCEPTANCE_PROCESS_AUTHORIZE,
            Permissions.PM_ACCEPTANCE_PROCESS_FINANCIAL_REVIEW,
            Permissions.PM_IMPORT_XLSX_WITH_RECONCILIATION,
            Permissions.PM_DOWNLOAD_FSP_AUTH_CODE,
        ]
        cls.create_user_role_with_permissions(
            cls.user,
            cls.all_necessary_permissions,
            cls.business_area,
            whole_business_area_access=True,
        )
        cls.program = ProgramFactory()
        cls.registration_data_import = RegistrationDataImportFactory(
            business_area=cls.business_area, program=cls.program
        )

        cls.household_1, cls.individual_1 = cls.create_household_and_individual(cls.program)
        cls.household_1.refresh_from_db()
        cls.household_2, cls.individual_2 = cls.create_household_and_individual(cls.program)
        cls.household_2.refresh_from_db()
        cls.household_3, cls.individual_3 = cls.create_household_and_individual(cls.program)
        cls.household_3.refresh_from_db()

        cls.data_collecting_type = DataCollectingType.objects.create(
            code="full",
            description="Full individual collected",
            active=True,
            type="STANDARD",
        )
        cls.data_collecting_type.limit_to.add(cls.business_area)
        generate_delivery_mechanisms()

    @parameterized.expand(
        [
            (-1, Decimal(f"{round(100.00, 2):.2f}"), None, Payment.STATUS_ERROR),
            (0, Decimal(0), Decimal(0), Payment.STATUS_NOT_DISTRIBUTED),
            (
                400.10,
                Decimal(f"{round(400.23, 2):.2f}"),
                Decimal(f"{round(400.10, 2):.2f}"),
                Payment.STATUS_DISTRIBUTION_PARTIAL,
            ),
            (
                400.23,
                Decimal(f"{round(400.23, 2):.2f}"),
                Decimal(f"{round(400.23, 2):.2f}"),
                Payment.STATUS_DISTRIBUTION_SUCCESS,
            ),
            (
                500.00,
                Decimal(f"{round(500.00, 2):.2f}"),
                Decimal(f"{round(500.00, 2):.2f}"),
                Payment.STATUS_DISTRIBUTION_SUCCESS,
            ),
            (
                500,
                Decimal(f"{round(500.00, 2):.2f}"),
                Decimal(f"{round(500.00, 2):.2f}"),
                Payment.STATUS_DISTRIBUTION_SUCCESS,
            ),
            (600.00, Decimal(f"{round(100.00, 2):.2f}"), None, None),
            ("-1", Decimal(f"{round(100.00, 2):.2f}"), None, Payment.STATUS_ERROR),
            ("0", Decimal(0), Decimal(0), Payment.STATUS_NOT_DISTRIBUTED),
            (
                "400.10",
                Decimal(f"{round(400.23, 2):.2f}"),
                Decimal(f"{round(400.10, 2):.2f}"),
                Payment.STATUS_DISTRIBUTION_PARTIAL,
            ),
            (
                "400.23",
                Decimal(f"{round(400.23, 2):.2f}"),
                Decimal(f"{round(400.23, 2):.2f}"),
                Payment.STATUS_DISTRIBUTION_SUCCESS,
            ),
            (
                "500",
                Decimal(f"{round(500.00, 2):.2f}"),
                Decimal(f"{round(500.00, 2):.2f}"),
                Payment.STATUS_DISTRIBUTION_SUCCESS,
            ),
            (
                "500.00",
                Decimal(f"{round(500.00, 2):.2f}"),
                Decimal(f"{round(500.00, 2):.2f}"),
                Payment.STATUS_DISTRIBUTION_SUCCESS,
            ),
        ]
    )
    def test_receiving_payment_reconciliations_status(
        self,
        delivered_quantity: float,
        entitlement_quantity: Decimal,
        expected_delivered_quantity: Decimal,
        expected_status: str,
    ) -> None:
        service = XlsxPaymentPlanImportPerFspService(PaymentPlanFactory(created_by=self.user), None)  # type: ignore

        if not expected_status:
            with self.assertRaisesMessage(
                service.XlsxPaymentPlanImportPerFspServiceError,
                f"Invalid delivered_quantity {delivered_quantity} provided for payment_id xx",
            ):
                service._get_delivered_quantity_status_and_value(delivered_quantity, entitlement_quantity, "xx")

        else:
            status, value = service._get_delivered_quantity_status_and_value(
                delivered_quantity, entitlement_quantity, "xx"
            )
            assert status == expected_status
            assert value == expected_delivered_quantity

    def test_xlsx_payment_plan_import_per_fsp_service_import_row(self) -> None:
        pp = PaymentPlanFactory(
            status=PaymentPlan.Status.FINISHED,
            created_by=self.user,
        )
        pp.refresh_from_db()
        pvs = PaymentVerificationSummaryFactory()
        pvs.payment_plan = pp
        pvs.save()
        pvp = PaymentVerificationPlanFactory(
            payment_plan=pp,
            verification_channel=PaymentVerificationPlan.VERIFICATION_CHANNEL_MANUAL,
            status=PaymentVerificationPlan.STATUS_ACTIVE,
        )

        payment_1 = PaymentFactory(
            parent=PaymentPlan.objects.get(id=pp.id),
            business_area=self.business_area,
            household=self.household_1,
            collector=self.individual_1,
            delivery_type=None,
            entitlement_quantity=1111,
            entitlement_quantity_usd=100,
            delivered_quantity=1000,
            delivered_quantity_usd=99,
            financial_service_provider=None,
            currency="PLN",
        )
        payment_2 = PaymentFactory(
            parent=PaymentPlan.objects.get(id=pp.id),
            business_area=self.business_area,
            household=self.household_2,
            collector=self.individual_2,
            delivery_type=None,
            entitlement_quantity=2222,
            entitlement_quantity_usd=100,
            delivered_quantity=2000,
            delivered_quantity_usd=500,
            financial_service_provider=None,
            currency="PLN",
        )
        payment_3 = PaymentFactory(
            parent=PaymentPlan.objects.get(id=pp.id),
            business_area=self.business_area,
            household=self.household_3,
            collector=self.individual_3,
            delivery_type=None,
            entitlement_quantity=3333,
            entitlement_quantity_usd=300,
            delivered_quantity=3000,
            delivered_quantity_usd=290,
            financial_service_provider=None,
            currency="PLN",
        )
        verification_1 = PaymentVerificationFactory(
            payment_verification_plan=pvp,
            payment=payment_1,
            status=PaymentVerification.STATUS_RECEIVED_WITH_ISSUES,
            received_amount=999,
        )
        verification_2 = PaymentVerificationFactory(
            payment_verification_plan=pvp,
            payment=payment_2,
            status=PaymentVerification.STATUS_RECEIVED,
            received_amount=500,
        )
        verification_3 = PaymentVerificationFactory(
            payment_verification_plan=pvp,
            payment=payment_3,
            status=PaymentVerification.STATUS_PENDING,
            received_amount=None,
        )
        import_xlsx_service = XlsxPaymentPlanImportPerFspService(pp, io.BytesIO())
        import_xlsx_service.xlsx_headers = [
            "payment_id",
            "delivered_quantity",
            "delivery_date",
        ]

        import_xlsx_service.payments_dict[str(payment_1.pk)] = payment_1
        import_xlsx_service.payments_dict[str(payment_2.pk)] = payment_2
        import_xlsx_service.payments_dict[str(payment_3.pk)] = payment_3
        row = namedtuple(
            "row",
            [
                "value",
            ],
        )

        import_xlsx_service._import_row(
            [
                row(str(payment_1.id)),
                row(999),
                row(pytz.utc.localize(datetime.datetime(2023, 5, 12))),
            ],
            1,
        )
        import_xlsx_service._import_row(
            [
                row(str(payment_2.id)),
                row(100),
                row(pytz.utc.localize(datetime.datetime(2022, 12, 14))),
            ],
            1,
        )
        import_xlsx_service._import_row(
            [
                row(str(payment_3.id)),
                row(2999),
                row(pytz.utc.localize(datetime.datetime(2021, 7, 25))),
            ],
            1,
        )
        payment_1.save()
        payment_2.save()
        payment_3.save()
        # Update payment Verification
        PaymentVerification.objects.bulk_update(
            import_xlsx_service.payment_verifications_to_save, ("status", "status_date")
        )
        payment_1.refresh_from_db()
        payment_2.refresh_from_db()
        payment_3.refresh_from_db()
        verification_1.refresh_from_db()
        verification_2.refresh_from_db()
        verification_3.refresh_from_db()

        assert payment_1.delivered_quantity == 999
        assert verification_1.received_amount == 999
        assert verification_1.status == PaymentVerification.STATUS_RECEIVED

        assert payment_2.delivered_quantity == 100
        assert verification_2.received_amount == 500
        assert verification_2.status == PaymentVerification.STATUS_RECEIVED_WITH_ISSUES

        assert payment_3.delivered_quantity == 2999
        assert verification_3.received_amount is None
        assert verification_3.status == PaymentVerification.STATUS_PENDING

    def test_payment_plan_is_fully_delivered(self) -> None:
        payment_plan = PaymentPlanFactory(
            status=PaymentPlan.Status.ACCEPTED,
            created_by=self.user,
        )
        for hh, ind in [
            (self.household_1, self.individual_1),
            (self.household_2, self.individual_2),
            (self.household_3, self.individual_3),
        ]:
            PaymentFactory(
                parent=payment_plan,
                business_area=self.business_area,
                household=hh,
                collector=ind,
                delivery_type=None,
                entitlement_quantity=999,
                entitlement_quantity_usd=10,
                delivered_quantity=999,
                delivered_quantity_usd=10,
                financial_service_provider=None,
                currency="PLN",
            )
        payment_plan.status_finished()
        payment_plan.save()
        payment_plan.refresh_from_db()
        assert all(
            payment.entitlement_quantity == payment.delivered_quantity for payment in payment_plan.eligible_payments
        )
