from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

from django.core.management import call_command
from django.utils import timezone
import pytest
from strategy_field.utils import fqn

from extras.test_utils.factories.core import create_afghanistan
from hope.apps.sanction_list.strategies.un import UNSanctionList
from hope.apps.sanction_list.tasks.load_xml import LoadSanctionListXMLTask
from hope.models.sanction_list_individual import SanctionListIndividual

if TYPE_CHECKING:
    from hope.models.program import Program
    from hope.models.sanction_list import SanctionList


pytestmark = pytest.mark.usefixtures("django_elasticsearch_setup")


@pytest.fixture
def sanction_list(db: Any) -> "SanctionList":
    from test_utils.factories.sanction_list import SanctionListFactory

    return SanctionListFactory(strategy=fqn(UNSanctionList))


@pytest.fixture
def program(db: Any, sanction_list: "SanctionList") -> "Program":
    from extras.test_utils.factories.program import ProgramFactory

    call_command("loadcountries")
    create_afghanistan()
    program = ProgramFactory()
    program.sanction_lists.add(sanction_list)
    return program


@pytest.mark.elasticsearch
def test_execute(sanction_list: "SanctionList", program: "Program") -> None:
    main_test_files_path = Path(__file__).parent / "test_files"
    # Test #1
    task = LoadSanctionListXMLTask(sanction_list)
    task.load_from_file(main_test_files_path / "original-consolidated.xml")

    individuals = SanctionListIndividual.all_objects.all()
    assert individuals.count() == 1

    kpi_33_documents = individuals.get(reference_number="KPi.111").documents.all()
    assert kpi_33_documents.count() == 2

    # Test #2
    task = LoadSanctionListXMLTask(sanction_list)
    task.load_from_file(file_path=main_test_files_path / "updated-consolidated.xml")

    all_individuals = SanctionListIndividual.all_objects.all()
    assert all_individuals.count() == 1

    active_individuals = SanctionListIndividual.objects.filter(active=True)
    assert active_individuals.count() == 1

    updated_individual = active_individuals.get(reference_number="KPi.111")
    assert updated_individual.third_name == "TEST"
    assert updated_individual.listed_on == timezone.make_aware(datetime(year=2016, month=11, day=11))
    assert updated_individual.documents.all().count() == 3

    test_doc = updated_individual.documents.get(document_number="111222333555")
    assert test_doc.type_of_document == "Passport"

    # Test #3
    task = LoadSanctionListXMLTask(sanction_list)
    task.load_from_file(file_path=main_test_files_path / "updated2-consolidated.xml")

    all_individuals = SanctionListIndividual.all_objects.all()
    assert all_individuals.count() == 1

    active_individuals = SanctionListIndividual.objects.filter(active=True)
    assert active_individuals.count() == 1

    updated_individual = active_individuals.get(reference_number="KPi.111")
    assert updated_individual.listed_on == timezone.make_aware(datetime(year=2016, month=11, day=11))
