from extras.test_utils.factories import FlexibleAttributeForPDUFactory
from hope.models import FlexibleAttributeGroup, PeriodicFieldData, Program


def generate_pdu_data() -> None:
    test_program = Program.objects.get(business_area__slug="afghanistan", name="Test Program")
    group = FlexibleAttributeGroup.objects.create(name="Group 1", label={"english": "english"})
    pdu_data = PeriodicFieldData.objects.create(
        subtype="STRING",
        number_of_rounds=12,
        rounds_names=["test1", "test2", "test3..."],
    )
    FlexibleAttributeForPDUFactory(
        program=test_program,
        pdu_data=pdu_data,
        label="Test pdu 1",
        hint={"English(EN)": "Test pdu 1"},
        group=group,
    )
