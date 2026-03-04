import re
from typing import Any

from django.core.exceptions import ValidationError
from django.http import QueryDict
import pytest
from rest_framework.exceptions import ValidationError as DRFValidationError

from extras.test_utils.factories import (
    BusinessAreaFactory,
    DeliveryMechanismFactory,
    FinancialServiceProviderFactory,
    FinancialServiceProviderXlsxTemplateFactory,
    GrievanceTicketFactory,
    UserFactory,
)
from hope.admin.fsp import FspXlsxTemplatePerDeliveryMechanismForm
from hope.apps.grievance.models import GrievanceTicket
from hope.apps.grievance.validators import DataChangeValidator
from hope.models import FinancialServiceProvider

pytestmark = pytest.mark.django_db


@pytest.fixture
def user() -> Any:
    return UserFactory()


@pytest.fixture
def business_area() -> Any:
    return BusinessAreaFactory(slug="afghanistan")


@pytest.fixture
def base_model_data(user: Any, business_area: Any) -> dict[str, Any]:
    return {
        "status": GrievanceTicket.STATUS_NEW,
        "description": "test description",
        "area": "test area",
        "language": "english",
        "consent": True,
        "business_area": business_area,
        "assigned_to": user,
        "created_by": user,
    }


@pytest.fixture
def transfer_to_account_delivery_mechanism() -> Any:
    return DeliveryMechanismFactory(
        code="transfer_to_account",
        name="Transfer to Account",
    )


@pytest.fixture
def fsp_xlsx_template() -> Any:
    return FinancialServiceProviderXlsxTemplateFactory()


@pytest.fixture
def fsp() -> Any:
    return FinancialServiceProviderFactory(
        name="Test FSP",
        vision_vendor_number="123",
        communication_channel=FinancialServiceProvider.COMMUNICATION_CHANNEL_API,
    )


@pytest.mark.parametrize(
    ("category", "issue_type"),
    [
        (
            GrievanceTicket.CATEGORY_DATA_CHANGE,
            GrievanceTicket.ISSUE_TYPE_INDIVIDUAL_DATA_CHANGE_DATA_UPDATE,
        ),
        (
            GrievanceTicket.CATEGORY_POSITIVE_FEEDBACK,
            None,
        ),
    ],
)
def test_valid_issue_types(base_model_data: dict[str, Any], category: int, issue_type: int | None) -> None:
    grievance_ticket = GrievanceTicket(**base_model_data, category=category, issue_type=issue_type)
    grievance_ticket.save()
    assert grievance_ticket.issue_type == issue_type


@pytest.mark.parametrize(
    ("category", "issue_type"),
    [
        (
            GrievanceTicket.CATEGORY_DATA_CHANGE,
            None,
        ),
        (
            GrievanceTicket.CATEGORY_POSITIVE_FEEDBACK,
            GrievanceTicket.ISSUE_TYPE_INDIVIDUAL_DATA_CHANGE_DATA_UPDATE,
        ),
    ],
)
def test_invalid_issue_types(base_model_data: dict[str, Any], category: int, issue_type: int | None) -> None:
    grievance_ticket = GrievanceTicket(**base_model_data, category=category, issue_type=issue_type)
    with pytest.raises(ValidationError, match="Invalid issue type for selected category"):
        grievance_ticket.save()


def test_admin_form_clean_standalone_valid(
    fsp_xlsx_template: Any,
    fsp: Any,
    transfer_to_account_delivery_mechanism: Any,
) -> None:
    fsp.delivery_mechanisms.add(transfer_to_account_delivery_mechanism)
    form_data = QueryDict(mutable=True)
    form_data["financial_service_provider"] = str(fsp.id)
    form_data["delivery_mechanism"] = str(transfer_to_account_delivery_mechanism.id)
    form_data["xlsx_template"] = str(fsp_xlsx_template.id)

    form = FspXlsxTemplatePerDeliveryMechanismForm(data=form_data)
    assert form.is_valid()
    form.clean()


def test_admin_form_clean_inline_valid(
    fsp_xlsx_template: Any,
    fsp: Any,
    transfer_to_account_delivery_mechanism: Any,
) -> None:
    fsp.delivery_mechanisms.add(transfer_to_account_delivery_mechanism)
    form_data = QueryDict(mutable=True)
    form_data["financial_service_provider"] = str(fsp.id)
    form_data["delivery_mechanism"] = str(transfer_to_account_delivery_mechanism.id)
    form_data["xlsx_template"] = str(fsp_xlsx_template.id)
    form_data.setlist("delivery_mechanisms", [str(transfer_to_account_delivery_mechanism.id)])

    form = FspXlsxTemplatePerDeliveryMechanismForm(data=form_data)
    assert form.is_valid()
    form.clean()


def test_admin_form_clean_delivery_mechanism_not_supported(
    fsp_xlsx_template: Any,
    fsp: Any,
    transfer_to_account_delivery_mechanism: Any,
) -> None:
    form_data = QueryDict(mutable=True)
    form_data["financial_service_provider"] = str(fsp.id)
    form_data["delivery_mechanism"] = str(transfer_to_account_delivery_mechanism.id)
    form_data["xlsx_template"] = str(fsp_xlsx_template.id)

    form = FspXlsxTemplatePerDeliveryMechanismForm(data=form_data)
    assert not form.is_valid()

    error_message = (
        f"Delivery Mechanism {transfer_to_account_delivery_mechanism} is not supported by Financial Service Provider "
        f"{fsp}"
    )
    with pytest.raises(ValidationError, match=re.escape(error_message)):
        form.clean()


def test_admin_form_clean_inline_invalid_delivery_mechanisms(
    fsp_xlsx_template: Any,
    fsp: Any,
    transfer_to_account_delivery_mechanism: Any,
) -> None:
    form_data = QueryDict(mutable=True)
    form_data["financial_service_provider"] = str(fsp.id)
    form_data["delivery_mechanism"] = str(transfer_to_account_delivery_mechanism.id)
    form_data["xlsx_template"] = str(fsp_xlsx_template.id)
    form_data.setlist("delivery_mechanisms", ["12313213123"])

    form = FspXlsxTemplatePerDeliveryMechanismForm(data=form_data)
    assert not form.is_valid()

    error_message = (
        f"Delivery Mechanism {transfer_to_account_delivery_mechanism} is not supported by Financial Service Provider "
        f"{fsp}"
    )
    with pytest.raises(ValidationError, match=re.escape(error_message)):
        form.clean()


def test_non_dict_input_raises_graphql_error() -> None:
    with pytest.raises(DRFValidationError, match="Fields must be a dictionary"):
        DataChangeValidator.verify_approve_data("not a dict")  # type: ignore[arg-type]


def test_missing_individual_id_raises_graphql_error() -> None:
    data = {"roles": [{"approve_status": True}]}
    with pytest.raises(DRFValidationError, match="individual_id in role"):
        DataChangeValidator.verify_approve_data(data)


def test_missing_approve_status_raises_graphql_error() -> None:
    data = {"roles": [{"individual_id": "123"}]}
    with pytest.raises(DRFValidationError, match="approve_status in role"):
        DataChangeValidator.verify_approve_data(data)


def test_non_boolean_approve_status_raises_graphql_error() -> None:
    data = {"roles": [{"individual_id": "123", "approve_status": "yes"}]}
    with pytest.raises(DRFValidationError, match="approve_status must be boolean"):
        DataChangeValidator.verify_approve_data(data)


def test_non_boolean_top_level_field_raises_graphql_error() -> None:
    data = {
        "village": "yes",
        "roles": [{"individual_id": "123", "approve_status": True}],
    }
    with pytest.raises(DRFValidationError, match="Values must be booleans"):
        DataChangeValidator.verify_approve_data(data)


def test_can_change_status_beneficiary_ticket() -> None:
    ticket = GrievanceTicketFactory(
        category=GrievanceTicket.CATEGORY_BENEFICIARY,
        issue_type=None,
        status=GrievanceTicket.STATUS_NEW,
    )

    assert ticket.can_change_status(GrievanceTicket.STATUS_ASSIGNED) is True
    assert ticket.can_change_status(GrievanceTicket.STATUS_IN_PROGRESS) is False

    ticket.status = GrievanceTicket.STATUS_ASSIGNED
    assert ticket.can_change_status(GrievanceTicket.STATUS_IN_PROGRESS) is True

    ticket.status = GrievanceTicket.STATUS_IN_PROGRESS
    assert ticket.can_change_status(GrievanceTicket.STATUS_CLOSED) is True
