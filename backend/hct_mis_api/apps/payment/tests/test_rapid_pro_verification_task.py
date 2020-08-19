import io
import uuid
from unittest.mock import MagicMock, patch

from django.core.exceptions import ValidationError
from django.core.management import call_command
from openpyxl.writer.excel import save_virtual_workbook

from account.fixtures import UserFactory
from core.base_test_case import APITestCase
from core.models import BusinessArea, AdminArea
from household.fixtures import (
    create_household,
    EntitlementCardFactory,
)
from payment.fixtures import (
    PaymentRecordFactory,
    CashPlanPaymentVerificationFactory,
    PaymentVerificationFactory,
)
from payment.models import PaymentVerification, CashPlanPaymentVerification
from payment.rapid_pro.api import RapidProAPI
from payment.tasks.CheckRapidProVerificationTask import (
    CheckRapidProVerificationTask,
)
from payment.xlsx.XlsxVerificationExportService import (
    XlsxVerificationExportService,
)
from payment.xlsx.XlsxVerificationImportService import (
    XlsxVerificationImportService,
)
from program.fixtures import ProgramFactory, CashPlanFactory
from registration_data.fixtures import RegistrationDataImportFactory
from targeting.fixtures import TargetingCriteriaFactory, TargetPopulationFactory


class TestRapidProVerificationTask(APITestCase):
    verification = None
    START_UUID = "3d946aa7-af58-4838-8dfd-553786d9bb35"
    ORIGINAL_RAPIDPRO_RUNS_RESPONSE = [
        {
            "id": 1202235952,
            "uuid": "5b6f30ee-010b-4bd5-a510-e78f062af448",
            "flow": {
                "uuid": "0331293b-9e47-4766-9b78-37a9a702fd95",
                "name": "Payment Verification",
            },
            "contact": {
                "uuid": "875cf5d1-ab56-48f4-97e5-1d757d75a06a",
                "urn": "telegram:1241420989",
                "name": "Sumit Chachra",
            },
            "start": {"uuid": START_UUID},
            "responded": True,
            "path": [
                {
                    "node": "f511ccc6-b380-453a-9901-d8cb9c672d72",
                    "time": "2020-08-10T13:24:37.813876Z",
                },
                {
                    "node": "2b541238-e1fb-4d75-aa83-6e5946382734",
                    "time": "2020-08-10T13:24:37.813947Z",
                },
                {
                    "node": "0532a470-e128-48a6-aa9f-c5bdffd0f61a",
                    "time": "2020-08-10T14:51:18.515192Z",
                },
                {
                    "node": "8952391d-89fc-404a-8c34-4569aa5fb947",
                    "time": "2020-08-10T14:51:18.515221Z",
                },
                {
                    "node": "d4af6004-268a-468d-897a-c4f93cff34fc",
                    "time": "2020-08-10T14:51:22.493086Z",
                },
            ],
            "values": {
                "cash_received_amount": {
                    "value": "200",
                    "category": "Has Number",
                    "node": "8952391d-89fc-404a-8c34-4569aa5fb947",
                    "time": "2020-08-10T14:51:22.493065Z",
                    "input": "200",
                    "name": "Cash received amount",
                },
                "cash_received_text": {
                    "value": "Yes",
                    "category": "Yes",
                    "node": "2b541238-e1fb-4d75-aa83-6e5946382734",
                    "time": "2020-08-10T14:51:18.515178Z",
                    "input": "Yes",
                    "name": "Cash received text",
                },
            },
            "created_on": "2020-08-10T13:24:37.813857Z",
            "modified_on": "2020-08-10T14:51:22.493043Z",
            "exited_on": "2020-08-10T14:51:22.493130Z",
            "exit_type": "completed",
        },
    ]

    @classmethod
    def setUpTestData(cls):
        call_command("loadbusinessareas")
        payment_record_amount = 10

        user = UserFactory()

        program = ProgramFactory(business_area=BusinessArea.objects.first())
        program.admin_areas.set(AdminArea.objects.order_by("?")[:3])
        targeting_criteria = TargetingCriteriaFactory()

        target_population = TargetPopulationFactory(
            created_by=user,
            candidate_list_targeting_criteria=targeting_criteria,
            business_area=BusinessArea.objects.first(),
        )
        cash_plan = CashPlanFactory.build(
            program=program, business_area=BusinessArea.objects.first(),
        )
        cash_plan.save()
        cash_plan_payment_verification = CashPlanPaymentVerificationFactory(
            status=CashPlanPaymentVerification.STATUS_ACTIVE,
            verification_method=CashPlanPaymentVerification.VERIFICATION_METHOD_RAPIDPRO,
        )
        for _ in range(payment_record_amount):
            registration_data_import = RegistrationDataImportFactory(
                imported_by=user, business_area=BusinessArea.objects.first()
            )
            household, individuals = create_household(
                {
                    "registration_data_import": registration_data_import,
                    "admin_area": AdminArea.objects.order_by("?").first(),
                },
                {"registration_data_import": registration_data_import,},
            )

            household.programs.add(program)

            payment_record = PaymentRecordFactory(
                cash_plan=cash_plan,
                household=household,
                target_population=target_population,
            )

            PaymentVerificationFactory(
                cash_plan_payment_verification=cash_plan_payment_verification,
                payment_record=payment_record,
                status=PaymentVerification.STATUS_PENDING,
            )
            EntitlementCardFactory(household=household)
        cls.cash_plan = cash_plan
        cls.verification = cash_plan.verifications.first()

    @patch("payment.rapid_pro.api.RapidProAPI.__init__")
    def test_filtering_by_start_id(self, mock_parent_init):
        mock_parent_init.return_value = None
        payment_record_verification = TestRapidProVerificationTask.verification.payment_record_verifications.prefetch_related(
            "payment_record__household__head_of_household"
        ).first()
        TestRapidProVerificationTask.ORIGINAL_RAPIDPRO_RUNS_RESPONSE[0][
            "contact"
        ][
            "urn"
        ] = f"tel:{payment_record_verification.payment_record.household.head_of_household.phone_no}"
        mock = MagicMock(
            return_value=TestRapidProVerificationTask.ORIGINAL_RAPIDPRO_RUNS_RESPONSE
        )
        with patch("payment.rapid_pro.api.RapidProAPI.get_flow_runs", mock):
            api = RapidProAPI("afghanistan")
            mapped_dict = api.get_mapped_flow_runs(uuid.uuid4())
            self.assertEqual(
                mapped_dict, [],
            )

    @patch("payment.rapid_pro.api.RapidProAPI.__init__")
    def test_mapping(self, mock_parent_init):
        mock_parent_init.return_value = None
        payment_record_verification = TestRapidProVerificationTask.verification.payment_record_verifications.prefetch_related(
            "payment_record__household__head_of_household"
        ).first()
        TestRapidProVerificationTask.ORIGINAL_RAPIDPRO_RUNS_RESPONSE[0][
            "contact"
        ][
            "urn"
        ] = f"tel:{payment_record_verification.payment_record.household.head_of_household.phone_no}"
        mock = MagicMock(
            return_value=TestRapidProVerificationTask.ORIGINAL_RAPIDPRO_RUNS_RESPONSE
        )
        with patch("payment.rapid_pro.api.RapidProAPI.get_flow_runs", mock):
            api = RapidProAPI("afghanistan")
            mapped_dict = api.get_mapped_flow_runs(
                TestRapidProVerificationTask.START_UUID
            )
            self.assertEqual(
                mapped_dict,
                [
                    {
                        "phone_number": str(
                            payment_record_verification.payment_record.household.head_of_household.phone_no
                        ),
                        "received": True,
                        "received_amount": "200",
                    }
                ],
            )

    @patch("payment.rapid_pro.api.RapidProAPI.__init__")
    def test_not_received(self, mock_parent_init):
        mock_parent_init.return_value = None
        payment_record_verification = (
            TestRapidProVerificationTask.verification.payment_record_verifications.prefetch_related(
                "payment_record__household__head_of_household"
            )
            .order_by("?")
            .first()
        )
        self.assertEqual(
            payment_record_verification.status,
            PaymentVerification.STATUS_PENDING,
        )
        fake_data_to_return_from_rapid_pro_api = [
            {
                "phone_number": str(
                    payment_record_verification.payment_record.household.head_of_household.phone_no
                ),
                "received": False,
            }
        ]
        mock = MagicMock(return_value=fake_data_to_return_from_rapid_pro_api)
        with patch(
            "payment.rapid_pro.api.RapidProAPI.get_mapped_flow_runs", mock
        ):
            task = CheckRapidProVerificationTask()
            task.execute()
            mock.assert_called()
            payment_record_verification.refresh_from_db()
            self.assertEqual(
                payment_record_verification.status,
                PaymentVerification.STATUS_NOT_RECEIVED,
            )

    @patch("payment.rapid_pro.api.RapidProAPI.__init__")
    def test_received_with_issues(self, mock_parent_init):
        mock_parent_init.return_value = None
        payment_record_verification = (
            TestRapidProVerificationTask.verification.payment_record_verifications.prefetch_related(
                "payment_record__household__head_of_household"
            )
            .order_by("?")
            .first()
        )
        self.assertEqual(
            payment_record_verification.status,
            PaymentVerification.STATUS_PENDING,
        )
        fake_data_to_return_from_rapid_pro_api = [
            {
                "phone_number": str(
                    payment_record_verification.payment_record.household.head_of_household.phone_no
                ),
                "received": True,
                "received_amount": payment_record_verification.payment_record.delivered_quantity
                - 1,
            }
        ]
        mock = MagicMock(return_value=fake_data_to_return_from_rapid_pro_api)
        with patch(
            "payment.rapid_pro.api.RapidProAPI.get_mapped_flow_runs", mock
        ):
            task = CheckRapidProVerificationTask()
            task.execute()
            mock.assert_called()
            payment_record_verification.refresh_from_db()
            self.assertEqual(
                payment_record_verification.status,
                PaymentVerification.STATUS_RECEIVED_WITH_ISSUES,
            )
            self.assertEqual(
                payment_record_verification.received_amount,
                payment_record_verification.payment_record.delivered_quantity
                - 1,
            )

    @patch("payment.rapid_pro.api.RapidProAPI.__init__")
    def test_received(self, mock_parent_init):
        mock_parent_init.return_value = None
        payment_record_verification = (
            TestRapidProVerificationTask.verification.payment_record_verifications.prefetch_related(
                "payment_record__household__head_of_household"
            )
            .order_by("?")
            .first()
        )
        self.assertEqual(
            payment_record_verification.status,
            PaymentVerification.STATUS_PENDING,
        )
        fake_data_to_return_from_rapid_pro_api = [
            {
                "phone_number": str(
                    payment_record_verification.payment_record.household.head_of_household.phone_no
                ),
                "received": True,
                "received_amount": payment_record_verification.payment_record.delivered_quantity,
            }
        ]
        mock = MagicMock(return_value=fake_data_to_return_from_rapid_pro_api)
        with patch(
            "payment.rapid_pro.api.RapidProAPI.get_mapped_flow_runs", mock
        ):
            task = CheckRapidProVerificationTask()
            task.execute()
            mock.assert_called()
            payment_record_verification.refresh_from_db()
            self.assertEqual(
                payment_record_verification.status,
                PaymentVerification.STATUS_RECEIVED,
            )
            self.assertEqual(
                payment_record_verification.received_amount,
                payment_record_verification.payment_record.delivered_quantity,
            )
