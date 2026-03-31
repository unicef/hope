import pytest

from extras.test_utils.factories.account import (
    PartnerFactory,
    RoleAssignmentFactory,
    RoleFactory,
)
from hope.models import BusinessArea


@pytest.fixture
def unhcr_partner() -> None:
    """Create UNHCR partner with a role in Afghanistan."""
    partner_unhcr = PartnerFactory(name="UNHCR")
    afghanistan = BusinessArea.objects.get(slug="afghanistan")
    partner_unhcr.role_assignments.all().delete()
    partner_unhcr.allowed_business_areas.add(afghanistan)
    RoleAssignmentFactory(
        partner=partner_unhcr,
        business_area=afghanistan,
        role=RoleFactory(name="Role for UNHCR"),
        program=None,
    )
