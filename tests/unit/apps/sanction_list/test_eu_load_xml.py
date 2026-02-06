from pathlib import Path
from typing import TYPE_CHECKING, Any

import pytest

from extras.test_utils.old_factories.geo import CountryFactory
from hope.models import (
    SanctionListIndividual,
    SanctionListIndividualAliasName,
    SanctionListIndividualDateOfBirth,
    SanctionListIndividualNationalities,
)

if TYPE_CHECKING:
    from hope.apps.sanction_list.strategies.eu import EUSanctionList
    from hope.models import SanctionList


pytestmark = pytest.mark.usefixtures("django_elasticsearch_setup")


@pytest.fixture
def strategy(sanction_list: "SanctionList") -> "EUSanctionList":
    return sanction_list.strategy  # type: ignore[return-value]


@pytest.mark.elasticsearch
def test_load_file(strategy: "EUSanctionList", always_eager: Any) -> None:
    main_test_files_path = Path(__file__).parent / "test_files"
    CountryFactory(name="Iraq", short_name="Iraq", iso_code2="IQ", iso_code3="IRQ", iso_num="0368")
    CountryFactory(name="Poland", short_name="Poland", iso_code2="PL", iso_code3="POL", iso_num="0616")
    strategy.load_from_file(main_test_files_path / "eu.xml")
    assert SanctionListIndividual.objects.count() == 2
    assert SanctionListIndividualAliasName.objects.count() == 3  # we have 4 aliases, but one is double
    assert SanctionListIndividualNationalities.objects.count() == 2
    assert SanctionListIndividualDateOfBirth.objects.count() == 1
