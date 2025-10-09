from decimal import Decimal
from typing import Any, Dict, List, Optional
from unittest.mock import MagicMock, patch
import uuid

from django.test import TestCase
import pytest
import requests
from requests import HTTPError

import requests
from extras.test_utils.factories.account import UserFactory
from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.household import (
    EntitlementCardFactory,
    create_household,
)
from extras.test_utils.factories.payment import (
    PaymentFactory,
    PaymentPlanFactory,
    PaymentVerificationFactory,
    PaymentVerificationPlanFactory,
    PaymentVerificationSummaryFactory,
)
from extras.test_utils.factories.program import ProgramFactory
from extras.test_utils.factories.registration_data import RegistrationDataImportFactory
from hope.apps.core.models import BusinessArea
from hope.apps.core.services.rapid_pro.api import RapidProAPI
from hope.apps.geo.models import Area
from hope.apps.payment.celery_tasks import CheckRapidProVerificationTask
from hope.apps.payment.models import PaymentVerification, PaymentVerificationPlan
from hope.apps.utils.phone import is_valid_phone_number


class TestRapidProVerificationTask(TestCase):
    START_UUID = "3d946aa7-af58-4838-8dfd-553786d9bb35"
    ORIGINAL_RAPIDPRO_RUNS_RESPONSE: List[Dict] = [
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
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        create_afghanistan()
        payment_record_amount = 10

        user = UserFactory()

        program = ProgramFactory(business_area=BusinessArea.objects.first())
        program.admin_areas.set(Area.objects.order_by("?")[:3])

        payment_plan = PaymentPlanFactory(
            program_cycle=program.cycles.first(),
            business_area=BusinessArea.objects.first(),
            created_by=user,
        )
        PaymentVerificationSummaryFactory(payment_plan=payment_plan)
        payment_verification_plan = PaymentVerificationPlanFactory(
            status=PaymentVerificationPlan.STATUS_ACTIVE,
            verification_channel=PaymentVerificationPlan.VERIFICATION_CHANNEL_RAPIDPRO,
            payment_plan=payment_plan,
        )
        cls.individuals = []
        for _ in range(payment_record_amount):
            registration_data_import = RegistrationDataImportFactory(
                imported_by=user, business_area=BusinessArea.objects.first()
            )
            household, individuals = create_household(
                {
                    "registration_data_import": registration_data_import,
                    "admin2": Area.objects.order_by("?").first(),
                    "program": program,
                },
                {"registration_data_import": registration_data_import},
            )
            cls.individuals.extend(individuals)

            payment = PaymentFactory(
                parent=payment_plan,
                household=household,
                head_of_household=household.head_of_household,
                delivered_quantity_usd=200,
                currency="PLN",
            )

            PaymentVerificationFactory(
                payment_verification_plan=payment_verification_plan,
                payment=payment,
                status=PaymentVerification.STATUS_PENDING,
            )
            EntitlementCardFactory(household=household)
        cls.payment_plan = payment_plan
        cls.verification = payment_plan.payment_verification_plans.first()

    @patch("hope.apps.core.services.rapid_pro.api.RapidProAPI.__init__")
    def test_filtering_by_start_id(self, mock_parent_init: Any) -> None:
        mock_parent_init.return_value = None
        payment_record_verification_obj = TestRapidProVerificationTask.verification.payment_record_verifications.first()
        TestRapidProVerificationTask.ORIGINAL_RAPIDPRO_RUNS_RESPONSE[0]["contact"]["urn"] = (
            f"tel:{payment_record_verification_obj.payment.head_of_household.phone_no}"
        )
        mock = MagicMock(return_value=TestRapidProVerificationTask.ORIGINAL_RAPIDPRO_RUNS_RESPONSE)
        with patch("hope.apps.core.services.rapid_pro.api.RapidProAPI.get_flow_runs", mock):
            api = RapidProAPI("afghanistan", RapidProAPI.MODE_VERIFICATION)
            mapped_dict = api.get_mapped_flow_runs([str(uuid.uuid4())])
            assert mapped_dict == []

    @patch("hope.apps.core.services.rapid_pro.api.RapidProAPI.__init__")
    def test_mapping(self, mock_parent_init: Any) -> None:
        mock_parent_init.return_value = None
        payment_record_verification_obj = TestRapidProVerificationTask.verification.payment_record_verifications.first()
        TestRapidProVerificationTask.ORIGINAL_RAPIDPRO_RUNS_RESPONSE[0]["contact"]["urn"] = (
            f"tel:{payment_record_verification_obj.payment.head_of_household.phone_no}"
        )
        mock = MagicMock(return_value=TestRapidProVerificationTask.ORIGINAL_RAPIDPRO_RUNS_RESPONSE)
        with patch("hope.apps.core.services.rapid_pro.api.RapidProAPI.get_flow_runs", mock):
            api = RapidProAPI("afghanistan", RapidProAPI.MODE_VERIFICATION)
            mapped_dict = api.get_mapped_flow_runs([TestRapidProVerificationTask.START_UUID])
            assert mapped_dict == [
                {
                    "phone_number": str(payment_record_verification_obj.payment.head_of_household.phone_no),
                    "received": True,
                    "received_amount": Decimal(200),
                }
            ]

    @patch("hope.apps.core.services.rapid_pro.api.RapidProAPI.__init__")
    def test_not_received(self, mock_parent_init: Any) -> None:
        mock_parent_init.return_value = None
        payment_record_verification = TestRapidProVerificationTask.verification.payment_record_verifications.order_by(
            "?"
        ).first()
        assert payment_record_verification.status == PaymentVerification.STATUS_PENDING

        fake_data_to_return_from_rapid_pro_api = [
            {
                "phone_number": str(payment_record_verification.payment.head_of_household.phone_no),
                "received": False,
            }
        ]
        assert is_valid_phone_number(payment_record_verification.payment.head_of_household.phone_no), (
            payment_record_verification.payment.head_of_household.phone_no
        )
        mock = MagicMock(return_value=fake_data_to_return_from_rapid_pro_api)
        with patch(
            "hope.apps.core.services.rapid_pro.api.RapidProAPI.get_mapped_flow_runs",
            mock,
        ):
            task = CheckRapidProVerificationTask()
            task.execute()
            mock.assert_called()
            payment_record_verification.refresh_from_db()
            assert payment_record_verification.status == PaymentVerification.STATUS_NOT_RECEIVED

    @patch("hope.apps.core.services.rapid_pro.api.RapidProAPI.__init__")
    def test_received_with_issues(self, mock_parent_init: Any) -> None:
        mock_parent_init.return_value = None
        payment_record_verification = TestRapidProVerificationTask.verification.payment_record_verifications.order_by(
            "?"
        ).first()
        assert payment_record_verification.status == PaymentVerification.STATUS_PENDING
        assert is_valid_phone_number(payment_record_verification.payment.head_of_household.phone_no), (
            payment_record_verification.payment.head_of_household.phone_no
        )
        fake_data_to_return_from_rapid_pro_api = [
            {
                "phone_number": str(payment_record_verification.payment.head_of_household.phone_no),
                "received": True,
                "received_amount": payment_record_verification.payment.delivered_quantity - 1,
            }
        ]
        mock = MagicMock(return_value=fake_data_to_return_from_rapid_pro_api)
        with patch(
            "hope.apps.core.services.rapid_pro.api.RapidProAPI.get_mapped_flow_runs",
            mock,
        ):
            task = CheckRapidProVerificationTask()
            task.execute()
            mock.assert_called()
            payment_record_verification.refresh_from_db()
            assert payment_record_verification.status == PaymentVerification.STATUS_RECEIVED_WITH_ISSUES
            assert (
                payment_record_verification.received_amount
                == payment_record_verification.payment.delivered_quantity - 1
            )

    @patch("hope.apps.core.services.rapid_pro.api.RapidProAPI.__init__")
    def test_received(self, mock_parent_init: Any) -> None:
        mock_parent_init.return_value = None
        payment_record_verification = TestRapidProVerificationTask.verification.payment_record_verifications.order_by(
            "?"
        ).first()
        assert payment_record_verification.status == PaymentVerification.STATUS_PENDING
        fake_data_to_return_from_rapid_pro_api = [
            {
                "phone_number": str(payment_record_verification.payment.head_of_household.phone_no),
                "received": True,
                "received_amount": payment_record_verification.payment.delivered_quantity,
            }
        ]
        assert is_valid_phone_number(payment_record_verification.payment.head_of_household.phone_no), (
            payment_record_verification.payment.head_of_household.phone_no
        )
        mock = MagicMock(return_value=fake_data_to_return_from_rapid_pro_api)
        with patch(
            "hope.apps.core.services.rapid_pro.api.RapidProAPI.get_mapped_flow_runs",
            mock,
        ):
            task = CheckRapidProVerificationTask()
            task.execute()
            mock.assert_called()
            payment_record_verification.refresh_from_db()
            assert payment_record_verification.status == PaymentVerification.STATUS_RECEIVED
            assert payment_record_verification.received_amount == payment_record_verification.payment.delivered_quantity

    @patch("hope.apps.core.services.rapid_pro.api.RapidProAPI.__init__")
    def test_wrong_phone_number(self, mock_parent_init: Any) -> None:
        mock_parent_init.return_value = None
        payment_record_verification = TestRapidProVerificationTask.verification.payment_record_verifications.order_by(
            "?"
        ).first()
        assert payment_record_verification.status == PaymentVerification.STATUS_PENDING
        fake_data_to_return_from_rapid_pro_api = [
            {
                "phone_number": "123-not-really-a-phone-number",
                "received": True,
                "received_amount": payment_record_verification.payment.delivered_quantity,
            }
        ]
        mock = MagicMock(return_value=fake_data_to_return_from_rapid_pro_api)
        with patch(
            "hope.apps.core.services.rapid_pro.api.RapidProAPI.get_mapped_flow_runs",
            mock,
        ):
            task = CheckRapidProVerificationTask()
            task.execute()
            mock.assert_called()

            payment_record_verification.refresh_from_db()
            # verification is still pending, so it was not considered within the verification plan
            assert payment_record_verification.status == PaymentVerification.STATUS_PENDING

    def test_recalculating_validity_on_number_change(self) -> None:
        ind = self.individuals[0]

        first_phone = "+380 637 541 345"
        ind.phone_no = first_phone
        ind.save()
        assert ind.phone_no_valid

        second_phone = "+380 637 541 X"
        ind.phone_no = second_phone
        ind.save()

        assert first_phone != second_phone
        assert not ind.phone_no_valid

    @patch("hope.apps.core.services.rapid_pro.api.RapidProAPI.__init__")
    def test_requests(self, mock_parent_init: Any) -> None:
        mock_parent_init.return_value = None
        api = RapidProAPI("afghanistan", RapidProAPI.MODE_VERIFICATION)
        api.url = ""
        api._timeout = 10

        api._client = MagicMock()

        class DummyResponse:
            def __init__(
                self, status_code: int = 200, payload: Optional[dict] = None, raise_http_error: bool = False
            ) -> None:
                self.status_code = status_code
                self._payload = payload or {}
                self._raise_http_error = raise_http_error
                self.ok = 200 <= status_code < 400
                self.url = "http://example.com/"

            def raise_for_status(self) -> None:
                if self._raise_http_error:
                    e = requests.exceptions.HTTPError("boom", response=self)  # type: ignore
                    raise e

            def json(self) -> dict:
                return self._payload

        api._client.get = MagicMock(
            return_value=DummyResponse(status_code=200, payload={"a": 1}, raise_http_error=False)
        )
        assert api._handle_get_request("/endpoint") == {"a": 1}

        api._client.get = MagicMock(return_value=DummyResponse(status_code=400, raise_http_error=True))
        with pytest.raises(HTTPError):
            api._handle_get_request("/endpoint")

        api._client.post = MagicMock(
            return_value=DummyResponse(status_code=200, payload={"a": 1}, raise_http_error=False)
        )
        assert api._handle_post_request("/endpoint", {"b": 2}) == {"a": 1}

        api._client.post = MagicMock(return_value=DummyResponse(status_code=400, raise_http_error=True))
        with pytest.raises(HTTPError):
            api._handle_post_request("/endpoint", {"b": 2})

    def test_parse_json_urns_error(self) -> None:
        ba = BusinessArea.objects.get(slug="afghanistan")
        ba.rapid_pro_payment_verification_token = "TEST_TOKEN"
        ba.rapid_pro_host = "http://rapidpro.local"
        ba.save(update_fields=["rapid_pro_payment_verification_token", "rapid_pro_host"])

        with patch.object(requests.Session, "mount", autospec=True):
            api = RapidProAPI("afghanistan", RapidProAPI.MODE_VERIFICATION)
            assert api._parse_json_urns_error(None, []) is None

            e = MagicMock()
            e.response = MagicMock()
            e.response.status_code = 400
            e.response.json.return_value = {"urns": {0: "a", 1: "b"}}

            assert api._parse_json_urns_error(e, ["a", "b"]) == {
                "phone_numbers": ["a - phone number is incorrect", "b - phone number is incorrect"]
            }

            assert api._parse_json_urns_error(e, []) == {"phone_numbers": []}

            e.response.json.return_value = {"error": "error"}
            assert api._parse_json_urns_error(e, ["a", "b"]) == {"error": {"error": "error"}}

            e.response.json.side_effect = Exception("test")
            assert api._parse_json_urns_error(e, ["a", "b"]) is None


class TestPhoneNumberVerification(TestCase):
    def test_phone_numbers(self) -> None:
        assert not is_valid_phone_number("+40 032 215 789")
        assert is_valid_phone_number("+48 632 215 789")

        assert is_valid_phone_number("+48 123 234 345")
        assert not is_valid_phone_number("0048 123 234 345")

        assert not is_valid_phone_number("(201) 555-0123")
        assert is_valid_phone_number("+1 (201) 555-0123")

        assert not is_valid_phone_number("123-not-really-a-phone-number")

        assert not is_valid_phone_number("+38063754115")
        assert is_valid_phone_number("+380637541150")
        assert is_valid_phone_number("+380 637 541 345")
        assert is_valid_phone_number("+380 637 541 XXX")  # it's ok to have A-Z in number
        assert not is_valid_phone_number("+380 23 234 345")
