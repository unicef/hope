import uuid
from decimal import Decimal
from typing import Any, Dict, List
from unittest.mock import MagicMock, patch

from django.test import TestCase

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.services.rapid_pro.api import RapidProAPI
from hct_mis_api.apps.geo.models import Area
from hct_mis_api.apps.household.fixtures import EntitlementCardFactory, create_household
from hct_mis_api.apps.payment.fixtures import (
    CashPlanFactory,
    PaymentRecordFactory,
    PaymentVerificationFactory,
    PaymentVerificationPlanFactory,
)
from hct_mis_api.apps.payment.models import PaymentVerification, PaymentVerificationPlan
from hct_mis_api.apps.payment.tasks.CheckRapidProVerificationTask import (
    CheckRapidProVerificationTask,
)
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.registration_data.fixtures import RegistrationDataImportFactory
from hct_mis_api.apps.targeting.fixtures import (
    TargetingCriteriaFactory,
    TargetPopulationFactory,
)
from hct_mis_api.apps.utils.phone import is_valid_phone_number


class TestRapidProVerificationTask(TestCase):
    START_UUID = "3d946aa7-af58-4838-8dfd-553786d9bb35"
    ORIGINAL_RAPIDPRO_RUNS_RESPONSE: List[Dict] = [
        {
            "id": 1202235952,
            "uuid": "5b6f30ee-010b-4bd5-a510-e78f062af448",
            "flow": {"uuid": "0331293b-9e47-4766-9b78-37a9a702fd95", "name": "Payment Verification"},
            "contact": {
                "uuid": "875cf5d1-ab56-48f4-97e5-1d757d75a06a",
                "urn": "telegram:1241420989",
                "name": "Sumit Chachra",
            },
            "start": {"uuid": START_UUID},
            "responded": True,
            "path": [
                {"node": "f511ccc6-b380-453a-9901-d8cb9c672d72", "time": "2020-08-10T13:24:37.813876Z"},
                {"node": "2b541238-e1fb-4d75-aa83-6e5946382734", "time": "2020-08-10T13:24:37.813947Z"},
                {"node": "0532a470-e128-48a6-aa9f-c5bdffd0f61a", "time": "2020-08-10T14:51:18.515192Z"},
                {"node": "8952391d-89fc-404a-8c34-4569aa5fb947", "time": "2020-08-10T14:51:18.515221Z"},
                {"node": "d4af6004-268a-468d-897a-c4f93cff34fc", "time": "2020-08-10T14:51:22.493086Z"},
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
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        create_afghanistan()
        payment_record_amount = 10

        user = UserFactory()

        program = ProgramFactory(business_area=BusinessArea.objects.first())
        program.admin_areas.set(Area.objects.order_by("?")[:3])
        targeting_criteria = TargetingCriteriaFactory()

        target_population = TargetPopulationFactory(
            created_by=user,
            targeting_criteria=targeting_criteria,
            business_area=BusinessArea.objects.first(),
        )
        cash_plan = CashPlanFactory(
            program=program,
            business_area=BusinessArea.objects.first(),
        )
        cash_plan.save()
        payment_verification_plan = PaymentVerificationPlanFactory(
            status=PaymentVerificationPlan.STATUS_ACTIVE,
            verification_channel=PaymentVerificationPlan.VERIFICATION_CHANNEL_RAPIDPRO,
            payment_plan_obj=cash_plan,
        )
        cls.individuals = []
        for _ in range(payment_record_amount):
            registration_data_import = RegistrationDataImportFactory(
                imported_by=user, business_area=BusinessArea.objects.first()
            )
            household, individuals = create_household(
                {
                    "registration_data_import": registration_data_import,
                    "admin_area": Area.objects.order_by("?").first(),
                },
                {"registration_data_import": registration_data_import},
            )
            cls.individuals.extend(individuals)

            household.programs.add(program)

            payment_record = PaymentRecordFactory(
                parent=cash_plan,
                household=household,
                head_of_household=household.head_of_household,
                target_population=target_population,
                delivered_quantity_usd=200,
                currency="PLN",
            )

            PaymentVerificationFactory(
                payment_verification_plan=payment_verification_plan,
                payment_obj=payment_record,
                status=PaymentVerification.STATUS_PENDING,
            )
            EntitlementCardFactory(household=household)
        cls.cash_plan = cash_plan
        cls.verification = cash_plan.get_payment_verification_plans.first()

    @patch("hct_mis_api.apps.core.services.rapid_pro.api.RapidProAPI.__init__")
    def test_filtering_by_start_id(self, mock_parent_init: Any) -> None:
        mock_parent_init.return_value = None
        payment_record_verification_obj = TestRapidProVerificationTask.verification.payment_record_verifications.first()
        TestRapidProVerificationTask.ORIGINAL_RAPIDPRO_RUNS_RESPONSE[0]["contact"][
            "urn"
        ] = f"tel:{payment_record_verification_obj.payment_obj.head_of_household.phone_no}"
        mock = MagicMock(return_value=TestRapidProVerificationTask.ORIGINAL_RAPIDPRO_RUNS_RESPONSE)
        with patch("hct_mis_api.apps.core.services.rapid_pro.api.RapidProAPI.get_flow_runs", mock):
            api = RapidProAPI("afghanistan", RapidProAPI.MODE_VERIFICATION)
            mapped_dict = api.get_mapped_flow_runs([str(uuid.uuid4())])
            self.assertEqual(
                mapped_dict,
                [],
            )

    @patch("hct_mis_api.apps.core.services.rapid_pro.api.RapidProAPI.__init__")
    def test_mapping(self, mock_parent_init: Any) -> None:
        mock_parent_init.return_value = None
        payment_record_verification_obj = TestRapidProVerificationTask.verification.payment_record_verifications.first()
        TestRapidProVerificationTask.ORIGINAL_RAPIDPRO_RUNS_RESPONSE[0]["contact"][
            "urn"
        ] = f"tel:{payment_record_verification_obj.payment_obj.head_of_household.phone_no}"
        mock = MagicMock(return_value=TestRapidProVerificationTask.ORIGINAL_RAPIDPRO_RUNS_RESPONSE)
        with patch("hct_mis_api.apps.core.services.rapid_pro.api.RapidProAPI.get_flow_runs", mock):
            api = RapidProAPI("afghanistan", RapidProAPI.MODE_VERIFICATION)
            mapped_dict = api.get_mapped_flow_runs([TestRapidProVerificationTask.START_UUID])
            self.assertEqual(
                mapped_dict,
                [
                    {
                        "phone_number": str(payment_record_verification_obj.payment_obj.head_of_household.phone_no),
                        "received": True,
                        "received_amount": Decimal("200"),
                    }
                ],
            )

    @patch("hct_mis_api.apps.core.services.rapid_pro.api.RapidProAPI.__init__")
    def test_not_received(self, mock_parent_init: Any) -> None:
        mock_parent_init.return_value = None
        payment_record_verification = TestRapidProVerificationTask.verification.payment_record_verifications.order_by(
            "?"
        ).first()
        self.assertEqual(
            payment_record_verification.status,
            PaymentVerification.STATUS_PENDING,
        )

        fake_data_to_return_from_rapid_pro_api = [
            {
                "phone_number": str(payment_record_verification.payment_obj.head_of_household.phone_no),
                "received": False,
            }
        ]
        assert is_valid_phone_number(
            payment_record_verification.payment_obj.head_of_household.phone_no
        ), payment_record_verification.payment_obj.head_of_household.phone_no
        mock = MagicMock(return_value=fake_data_to_return_from_rapid_pro_api)
        with patch("hct_mis_api.apps.core.services.rapid_pro.api.RapidProAPI.get_mapped_flow_runs", mock):
            task = CheckRapidProVerificationTask()
            task.execute()
            mock.assert_called()
            payment_record_verification.refresh_from_db()
            self.assertEqual(
                payment_record_verification.status,
                PaymentVerification.STATUS_NOT_RECEIVED,
            )

    @patch("hct_mis_api.apps.core.services.rapid_pro.api.RapidProAPI.__init__")
    def test_received_with_issues(self, mock_parent_init: Any) -> None:
        mock_parent_init.return_value = None
        payment_record_verification = TestRapidProVerificationTask.verification.payment_record_verifications.order_by(
            "?"
        ).first()
        self.assertEqual(
            payment_record_verification.status,
            PaymentVerification.STATUS_PENDING,
        )
        assert is_valid_phone_number(
            payment_record_verification.payment_obj.head_of_household.phone_no
        ), payment_record_verification.payment_obj.head_of_household.phone_no
        fake_data_to_return_from_rapid_pro_api = [
            {
                "phone_number": str(payment_record_verification.payment_obj.head_of_household.phone_no),
                "received": True,
                "received_amount": payment_record_verification.payment_obj.delivered_quantity - 1,
            }
        ]
        mock = MagicMock(return_value=fake_data_to_return_from_rapid_pro_api)
        with patch("hct_mis_api.apps.core.services.rapid_pro.api.RapidProAPI.get_mapped_flow_runs", mock):
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
                payment_record_verification.payment_obj.delivered_quantity - 1,
            )

    @patch("hct_mis_api.apps.core.services.rapid_pro.api.RapidProAPI.__init__")
    def test_received(self, mock_parent_init: Any) -> None:
        mock_parent_init.return_value = None
        payment_record_verification = TestRapidProVerificationTask.verification.payment_record_verifications.order_by(
            "?"
        ).first()
        self.assertEqual(
            payment_record_verification.status,
            PaymentVerification.STATUS_PENDING,
        )
        fake_data_to_return_from_rapid_pro_api = [
            {
                "phone_number": str(payment_record_verification.payment_obj.head_of_household.phone_no),
                "received": True,
                "received_amount": payment_record_verification.payment_obj.delivered_quantity,
            }
        ]
        assert is_valid_phone_number(
            payment_record_verification.payment_obj.head_of_household.phone_no
        ), payment_record_verification.payment_obj.head_of_household.phone_no
        mock = MagicMock(return_value=fake_data_to_return_from_rapid_pro_api)
        with patch("hct_mis_api.apps.core.services.rapid_pro.api.RapidProAPI.get_mapped_flow_runs", mock):
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
                payment_record_verification.payment_obj.delivered_quantity,
            )

    @patch("hct_mis_api.apps.core.services.rapid_pro.api.RapidProAPI.__init__")
    def test_wrong_phone_number(self, mock_parent_init: Any) -> None:
        mock_parent_init.return_value = None
        payment_record_verification = TestRapidProVerificationTask.verification.payment_record_verifications.order_by(
            "?"
        ).first()
        self.assertEqual(
            payment_record_verification.status,
            PaymentVerification.STATUS_PENDING,
        )
        fake_data_to_return_from_rapid_pro_api = [
            {
                "phone_number": "123-not-really-a-phone-number",
                "received": True,
                "received_amount": payment_record_verification.payment_obj.delivered_quantity,
            }
        ]
        mock = MagicMock(return_value=fake_data_to_return_from_rapid_pro_api)
        with patch("hct_mis_api.apps.core.services.rapid_pro.api.RapidProAPI.get_mapped_flow_runs", mock):
            task = CheckRapidProVerificationTask()
            task.execute()
            mock.assert_called()

            payment_record_verification.refresh_from_db()
            # verification is still pending, so it was not considered within the verification plan
            self.assertEqual(
                payment_record_verification.status,
                PaymentVerification.STATUS_PENDING,
            )

    def test_recalculating_validity_on_number_change(self) -> None:
        ind = self.individuals[0]

        first_phone = "+380 637 541 345"
        ind.phone_no = first_phone
        ind.save()
        self.assertTrue(ind.phone_no_valid)

        second_phone = "+380 637 541 X"
        ind.phone_no = second_phone
        ind.save()

        self.assertNotEqual(first_phone, second_phone)
        self.assertFalse(ind.phone_no_valid)


class TestPhoneNumberVerification(TestCase):
    def test_phone_numbers(self) -> None:
        self.assertFalse(is_valid_phone_number("+40 032 215 789"))
        self.assertTrue(is_valid_phone_number("+48 632 215 789"))

        self.assertTrue(is_valid_phone_number("+48 123 234 345"))
        self.assertFalse(is_valid_phone_number("0048 123 234 345"))

        self.assertFalse(is_valid_phone_number("(201) 555-0123"))
        self.assertTrue(is_valid_phone_number("+1 (201) 555-0123"))

        self.assertFalse(is_valid_phone_number("123-not-really-a-phone-number"))

        self.assertFalse(is_valid_phone_number("+38063754115"))
        self.assertTrue(is_valid_phone_number("+380637541150"))
        self.assertTrue(is_valid_phone_number("+380 637 541 345"))
        self.assertTrue(is_valid_phone_number("+380 637 541 XXX"))  # it's ok to have A-Z in number
        self.assertFalse(is_valid_phone_number("+380 23 234 345"))
