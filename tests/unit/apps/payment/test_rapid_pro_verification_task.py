from decimal import Decimal
from typing import Any, Dict, List, Optional
from unittest.mock import MagicMock, patch
import uuid

import pytest
import requests
from requests import HTTPError

from extras.test_utils.factories import (
    BusinessAreaFactory,
    EntitlementCardFactory,
    HouseholdFactory,
    PaymentFactory,
    PaymentPlanFactory,
    PaymentVerificationFactory,
    PaymentVerificationPlanFactory,
    PaymentVerificationSummaryFactory,
    ProgramCycleFactory,
    ProgramFactory,
    RegistrationDataImportFactory,
    UserFactory,
)
from hope.apps.core.services.rapid_pro.api import RapidProAPI
from hope.apps.payment.celery_tasks import CheckRapidProVerificationTask
from hope.apps.utils.phone import is_valid_phone_number
from hope.models import PaymentVerification, PaymentVerificationPlan

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


def make_dummy_response(
    status_code: int = 200,
    payload: Optional[dict] = None,
    raise_http_error: bool = False,
) -> MagicMock:
    response = MagicMock()
    response.status_code = status_code
    response._payload = payload or {}
    response._raise_http_error = raise_http_error
    response.ok = 200 <= status_code < 400
    response.url = "http://example.com/"

    def raise_for_status() -> None:
        if response._raise_http_error:
            raise requests.exceptions.HTTPError("boom", response=response)  # type: ignore

    response.raise_for_status = raise_for_status
    response.json = lambda: response._payload
    return response


@pytest.fixture
def business_area() -> Any:
    return BusinessAreaFactory(name="Afghanistan")


@pytest.fixture
def rapidpro_task_setup(business_area: Any) -> dict[str, Any]:
    user = UserFactory()

    program = ProgramFactory(business_area=business_area)
    cycle = ProgramCycleFactory(program=program, title="Cycle RapidPro")

    payment_plan = PaymentPlanFactory(
        program_cycle=cycle,
        business_area=business_area,
        created_by=user,
    )
    PaymentVerificationSummaryFactory(payment_plan=payment_plan)
    payment_verification_plan = PaymentVerificationPlanFactory(
        status=PaymentVerificationPlan.STATUS_ACTIVE,
        verification_channel=PaymentVerificationPlan.VERIFICATION_CHANNEL_RAPIDPRO,
        payment_plan=payment_plan,
    )

    individuals = []
    for index in range(2):
        registration_data_import = RegistrationDataImportFactory(imported_by=user, business_area=business_area)
        household = HouseholdFactory(
            business_area=business_area,
            program=program,
            registration_data_import=registration_data_import,
        )
        head = household.head_of_household
        head.phone_no = f"+380 637 541 34{index}"
        head.save(update_fields=["phone_no"])
        individuals.append(head)

        payment = PaymentFactory(
            parent=payment_plan,
            household=household,
            head_of_household=household.head_of_household,
            delivered_quantity=Decimal(200),
            delivered_quantity_usd=200,
            currency="PLN",
        )

        PaymentVerificationFactory(
            payment_verification_plan=payment_verification_plan,
            payment=payment,
            status=PaymentVerification.STATUS_PENDING,
        )
        EntitlementCardFactory(household=household)

    return {
        "payment_plan": payment_plan,
        "verification": payment_plan.payment_verification_plans.first(),
        "individuals": individuals,
    }


@patch("hope.apps.core.services.rapid_pro.api.RapidProAPI.__init__")
def test_filtering_by_start_id(mock_parent_init: Any, rapidpro_task_setup: dict[str, Any]) -> None:
    mock_parent_init.return_value = None
    verification = rapidpro_task_setup["verification"]
    payment_record_verification_obj = verification.payment_record_verifications.first()

    response = ORIGINAL_RAPIDPRO_RUNS_RESPONSE.copy()
    response[0] = {**response[0], "contact": {**response[0]["contact"]}}
    response[0]["contact"]["urn"] = f"tel:{payment_record_verification_obj.payment.head_of_household.phone_no}"

    mock = MagicMock(return_value=response)
    with patch("hope.apps.core.services.rapid_pro.api.RapidProAPI.get_flow_runs", mock):
        api = RapidProAPI("afghanistan", RapidProAPI.MODE_VERIFICATION)
        mapped_dict = api.get_mapped_flow_runs([str(uuid.uuid4())])
        assert mapped_dict == []


@patch("hope.apps.core.services.rapid_pro.api.RapidProAPI.__init__")
def test_mapping(mock_parent_init: Any, rapidpro_task_setup: dict[str, Any]) -> None:
    mock_parent_init.return_value = None
    verification = rapidpro_task_setup["verification"]
    payment_record_verification_obj = verification.payment_record_verifications.first()

    response = ORIGINAL_RAPIDPRO_RUNS_RESPONSE.copy()
    response[0] = {**response[0], "contact": {**response[0]["contact"]}}
    response[0]["contact"]["urn"] = f"tel:{payment_record_verification_obj.payment.head_of_household.phone_no}"

    mock = MagicMock(return_value=response)
    with patch("hope.apps.core.services.rapid_pro.api.RapidProAPI.get_flow_runs", mock):
        api = RapidProAPI("afghanistan", RapidProAPI.MODE_VERIFICATION)
        mapped_dict = api.get_mapped_flow_runs([START_UUID])
        assert mapped_dict == [
            {
                "phone_number": str(payment_record_verification_obj.payment.head_of_household.phone_no),
                "received": True,
                "received_amount": Decimal(200),
            }
        ]


@patch("hope.apps.core.services.rapid_pro.api.RapidProAPI.__init__")
def test_not_received(mock_parent_init: Any, rapidpro_task_setup: dict[str, Any]) -> None:
    mock_parent_init.return_value = None
    verification = rapidpro_task_setup["verification"]
    payment_record_verification = verification.payment_record_verifications.order_by("?").first()
    assert payment_record_verification.status == PaymentVerification.STATUS_PENDING

    fake_data_to_return_from_rapid_pro_api = [
        {
            "phone_number": str(payment_record_verification.payment.head_of_household.phone_no),
            "received": False,
        }
    ]
    assert is_valid_phone_number(payment_record_verification.payment.head_of_household.phone_no)
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
def test_received_with_issues(mock_parent_init: Any, rapidpro_task_setup: dict[str, Any]) -> None:
    mock_parent_init.return_value = None
    verification = rapidpro_task_setup["verification"]
    payment_record_verification = verification.payment_record_verifications.order_by("?").first()
    assert payment_record_verification.status == PaymentVerification.STATUS_PENDING
    assert is_valid_phone_number(payment_record_verification.payment.head_of_household.phone_no)
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
        assert payment_record_verification.received_amount == payment_record_verification.payment.delivered_quantity - 1


@patch("hope.apps.core.services.rapid_pro.api.RapidProAPI.__init__")
def test_received(mock_parent_init: Any, rapidpro_task_setup: dict[str, Any]) -> None:
    mock_parent_init.return_value = None
    verification = rapidpro_task_setup["verification"]
    payment_record_verification = verification.payment_record_verifications.order_by("?").first()
    assert payment_record_verification.status == PaymentVerification.STATUS_PENDING
    fake_data_to_return_from_rapid_pro_api = [
        {
            "phone_number": str(payment_record_verification.payment.head_of_household.phone_no),
            "received": True,
            "received_amount": payment_record_verification.payment.delivered_quantity,
        }
    ]
    assert is_valid_phone_number(payment_record_verification.payment.head_of_household.phone_no)
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
def test_wrong_phone_number(mock_parent_init: Any, rapidpro_task_setup: dict[str, Any]) -> None:
    mock_parent_init.return_value = None
    verification = rapidpro_task_setup["verification"]
    payment_record_verification = verification.payment_record_verifications.order_by("?").first()
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
        assert payment_record_verification.status == PaymentVerification.STATUS_PENDING


def test_recalculating_validity_on_number_change(rapidpro_task_setup: dict[str, Any]) -> None:
    individuals = rapidpro_task_setup["individuals"]
    ind = individuals[0]

    first_phone = "+380 637 541 345"
    ind.phone_no = first_phone
    ind.save(update_fields=["phone_no"])
    assert ind.phone_no_valid

    second_phone = "+380 637 541 X"
    ind.phone_no = second_phone
    ind.save(update_fields=["phone_no"])

    assert first_phone != second_phone
    assert not ind.phone_no_valid


@patch("hope.apps.core.services.rapid_pro.api.RapidProAPI.__init__")
def test_requests(mock_parent_init: Any, rapidpro_task_setup: dict[str, Any]) -> None:
    mock_parent_init.return_value = None
    api = RapidProAPI("afghanistan", RapidProAPI.MODE_VERIFICATION)
    api.url = ""
    api._timeout = 10

    api._client = MagicMock()

    api._client.get = MagicMock(return_value=make_dummy_response(status_code=200, payload={"a": 1}))
    assert api._handle_get_request("/endpoint") == {"a": 1}

    api._client.get = MagicMock(return_value=make_dummy_response(status_code=400, raise_http_error=True))
    with pytest.raises(HTTPError):
        api._handle_get_request("/endpoint")

    api._client.post = MagicMock(return_value=make_dummy_response(status_code=200, payload={"a": 1}))
    assert api._handle_post_request("/endpoint", {"b": 2}) == {"a": 1}

    api._client.post = MagicMock(return_value=make_dummy_response(status_code=400, raise_http_error=True))
    with pytest.raises(HTTPError):
        api._handle_post_request("/endpoint", {"b": 2})


def test_parse_json_urns_error(business_area: Any) -> None:
    ba = business_area
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

        e.response.json.side_effect = AttributeError("test")
        assert api._parse_json_urns_error(e, ["a", "b"]) is None


def test_phone_numbers() -> None:
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
    assert is_valid_phone_number("+380 637 541 XXX")
    assert not is_valid_phone_number("+380 23 234 345")
