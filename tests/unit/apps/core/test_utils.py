from decimal import Decimal

from django.test import TestCase
import pytest

from extras.test_utils.old_factories.core import create_afghanistan
from extras.test_utils.old_factories.household import HouseholdFactory, IndividualFactory
from extras.test_utils.old_factories.program import ProgramFactory
from hope.apps.core.utils import get_count_and_percentage, to_dict
from hope.apps.payment.utils import get_payment_delivered_quantity_status_and_value
from hope.models import Payment


class TestCoreUtils(TestCase):
    def test_get_count_and_percentage(self) -> None:
        assert get_count_and_percentage(1) == {"count": 1, "percentage": 100.0}
        assert get_count_and_percentage(0) == {"count": 0, "percentage": 0.0}
        assert get_count_and_percentage(5, 1) == {"count": 5, "percentage": 500.0}
        assert get_count_and_percentage(20, 20) == {"count": 20, "percentage": 100.0}
        assert get_count_and_percentage(5, 25) == {"count": 5, "percentage": 20.0}

    def test_get_payment_delivered_quantity_status_and_value(self) -> None:
        with self.assertRaisesMessage(Exception, "Invalid delivered quantity"):
            get_payment_delivered_quantity_status_and_value(None, Decimal(10.00))
        with self.assertRaisesMessage(Exception, "Invalid delivered quantity"):
            get_payment_delivered_quantity_status_and_value("", Decimal(10.00))
        assert get_payment_delivered_quantity_status_and_value(-1, Decimal(10.00)) == (
            Payment.STATUS_ERROR,
            None,
        )
        assert get_payment_delivered_quantity_status_and_value(0, Decimal(10.00)) == (
            Payment.STATUS_NOT_DISTRIBUTED,
            0,
        )
        assert get_payment_delivered_quantity_status_and_value(5.00, Decimal(10.00)) == (
            Payment.STATUS_DISTRIBUTION_PARTIAL,
            Decimal(5.00),
        )
        assert get_payment_delivered_quantity_status_and_value(10.00, Decimal(10.00)) == (
            Payment.STATUS_DISTRIBUTION_SUCCESS,
            Decimal(10.00),
        )
        with self.assertRaisesMessage(Exception, "Invalid delivered quantity"):
            get_payment_delivered_quantity_status_and_value(20.00, Decimal(10.00))


@pytest.mark.django_db
class TestToDict:
    def test_to_dict_with_nested_fields_multi(self):
        create_afghanistan()
        program = ProgramFactory()
        household = HouseholdFactory(program=program)
        IndividualFactory(household=household, program=program)
        IndividualFactory(household=household, program=program)

        result = to_dict(
            household,
            fields=["id"],
            dict_fields={"individuals": ["full_name", "birth_date"]},
        )

        assert "individuals" in result
        assert len(result["individuals"]) == 2
        assert all("full_name" in ind for ind in result["individuals"])

    def test_to_dict_with_nested_dotted_fields(self):
        create_afghanistan()
        program = ProgramFactory()
        individual = IndividualFactory(program=program)

        result = to_dict(
            individual,
            fields=["id"],
            dict_fields={"household": ["program.name"]},
        )

        assert "household" in result
        assert "name" in result["household"]
