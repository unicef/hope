from datetime import UTC, date, datetime

from django.contrib.admin.sites import site
import pytest

from extras.test_utils.factories import SanctionListIndividualFactory
from hope.admin.sanction_list_individual import SanctionListIndividualAdmin
from hope.models import SanctionListIndividual

pytestmark = pytest.mark.django_db


@pytest.fixture
def sanction_list_individual() -> SanctionListIndividual:
    return SanctionListIndividualFactory(listed_on=datetime(2024, 1, 2, 13, 30, tzinfo=UTC))


def test_sanction_list_admin_displays_listed_on_as_date(
    sanction_list_individual: SanctionListIndividual,
) -> None:
    model_admin = SanctionListIndividualAdmin(SanctionListIndividual, site)

    assert model_admin.listed_on_date(sanction_list_individual) == date(2024, 1, 2)
