from typing import Dict, List

import pytest

from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.household.fixtures import create_household
from hct_mis_api.apps.household.models import (CANNOT_DO, COMMUNICATING,
                                               DISABLED, HEARING, MEMORY,
                                               NOT_DISABLED, SEEING, SELF_CARE,
                                               WALKING, Individual)
from hct_mis_api.one_time_scripts.fix_disability_fields import \
    fix_disability_fields

pytestmark = pytest.mark.django_db


def create_invalid_individual(observed_disability: List[str], disabilities: Dict) -> Individual:
    return create_household(
        {"size": 1},
        {
            "disability": NOT_DISABLED,
            "observed_disability": observed_disability,
            **disabilities,
        },
    )[1][0]


class TestFixDisabilityFields:
    @pytest.fixture(autouse=True)
    def setUp(self) -> None:
        create_afghanistan()

    def test_fix_disability_fields(self) -> None:
        create_invalid_individual([SEEING], {"seeing_disability": CANNOT_DO})
        create_invalid_individual([HEARING], {"hearing_disability": CANNOT_DO})
        create_invalid_individual([WALKING], {"physical_disability": CANNOT_DO})
        create_invalid_individual([MEMORY], {"memory_disability": CANNOT_DO})
        create_invalid_individual([SELF_CARE], {"selfcare_disability": CANNOT_DO})
        create_invalid_individual([COMMUNICATING], {"comms_disability": CANNOT_DO})
        create_invalid_individual([], {})

        assert Individual.objects.filter(disability=NOT_DISABLED).count() == 21

        fix_disability_fields()

        assert Individual.objects.filter(disability=NOT_DISABLED).count() == 15
        assert Individual.objects.filter(disability=DISABLED).count() == 6
