from pathlib import Path
from typing import TYPE_CHECKING, Any

from django.core.management import call_command
import pytest

from hope.models.sanction_list_individual import SanctionListIndividual
from hope.models.sanction_list_individual_alias_name import SanctionListIndividualAliasName
from hope.models.sanction_list_individual_date_of_birth import SanctionListIndividualDateOfBirth
from hope.models.sanction_list_Individual_nationalities import SanctionListIndividualNationalities

if TYPE_CHECKING:
    from hope.apps.sanction_list.strategies.eu import EUSanctionList
    from hope.models.sanction_list import SanctionList


pytestmark = pytest.mark.usefixtures("django_elasticsearch_setup")


@pytest.fixture
def strategy(sanction_list: "SanctionList") -> "EUSanctionList":
    return sanction_list.strategy  # type: ignore[return-value]


@pytest.mark.elasticsearch
def test_load_file(strategy: "EUSanctionList", always_eager: Any) -> None:
    main_test_files_path = Path(__file__).parent / "test_files"
    call_command("loadcountries")
    strategy.load_from_file(main_test_files_path / "eu.xml")
    assert SanctionListIndividual.objects.count() == 2
    assert SanctionListIndividualAliasName.objects.count() == 3  # we have 4 aliases, but one is double
    assert SanctionListIndividualNationalities.objects.count() == 2
    assert SanctionListIndividualDateOfBirth.objects.count() == 1
