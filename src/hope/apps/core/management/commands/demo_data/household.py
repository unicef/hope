from extras.test_utils.factories import (
    BeneficiaryGroupFactory,
    DocumentFactory,
    DocumentTypeFactory,
    HouseholdFactory,
    IndividualFactory,
    ProgramCycleFactory,
    ProgramFactory,
    RegistrationDataImportFactory,
)
from extras.test_utils.factories.registration_data import _generate_rdi_dedup_demo
from hope.models import (
    ROLE_ALTERNATE,
    BeneficiaryGroup,
    BusinessArea,
    DataCollectingType,
    Household,
    Individual,
    IndividualRoleInHousehold,
    MergeStatusModel,
    Program,
    User,
)


def generate_beneficiary_groups() -> None:
    BeneficiaryGroupFactory(
        name="Household",
        group_label="Household",
        group_label_plural="Households",
        member_label="Individual",
        member_label_plural="Individuals",
        master_detail=True,
    )
    BeneficiaryGroupFactory(
        name="Social Workers",
        group_label="Household",
        group_label_plural="Households",
        member_label="Individual",
        member_label_plural="Individuals",
        master_detail=False,
    )


def generate_people_program() -> None:
    from hope.apps.household.const import HOST, SEEING

    ba = BusinessArea.objects.get(name="Afghanistan")
    people_program = ProgramFactory(
        name="Initial_Program_People (sw)",
        status="ACTIVE",
        start_date="2023-06-19",
        end_date="2029-12-24",
        description="qwerty",
        business_area=ba,
        budget="100000.00",
        frequency_of_payments="REGULAR",
        sector="EDUCATION",
        scope="UNICEF",
        cash_plus=False,
        data_collecting_type=DataCollectingType.objects.get(code="partial_individuals"),
        code="abc1",
        beneficiary_group=BeneficiaryGroup.objects.get(name="Social Workers"),
    )
    ProgramCycleFactory(
        program=people_program,
        unicef_id="PC-23-0060-000001",
        title="Default Program Cycle 1",
        status="DRAFT",
        start_date="2023-06-19",
        end_date="2023-12-24",
    )
    # add one individual
    household, individuals = create_household(
        household_args={
            "business_area": ba,
            "program": people_program,
            "residence_status": HOST,
        },
        individual_args={
            "full_name": "Stacey Freeman",
            "given_name": "Stacey",
            "middle_name": "",
            "family_name": "Freeman",
            "business_area": ba,
            "observed_disability": [SEEING],
        },
    )
    individual = individuals[0]
    DocumentFactory(individual=individual)


def generate_rdi() -> None:
    ba = BusinessArea.objects.get(slug="afghanistan")
    program = Program.objects.get(name="Initial_Program_People (sw)")
    user_root = User.objects.get(username="root")
    RegistrationDataImportFactory(
        name="Test people merge",
        status="MERGED",
        import_date="2022-03-30 09:22:14.870-00:00",
        imported_by=user_root,
        data_source="XLS",
        number_of_individuals=7,
        number_of_households=0,
        error_message="",
        pull_pictures=True,
        business_area=ba,
        screen_beneficiary=False,
        program=program,
    )
    RegistrationDataImportFactory(
        name="test_in_review",
        status="IN_REVIEW",
        import_date="2024-06-04T13:06:23.601Z",
        imported_by=user_root,
        data_source="XLS",
        number_of_individuals=10,
        number_of_households=0,
        batch_duplicates=0,
        batch_possible_duplicates=0,
        batch_unique=10,
        golden_record_duplicates=0,
        golden_record_possible_duplicates=0,
        golden_record_unique=10,
        pull_pictures=True,
        business_area=ba,
        screen_beneficiary=False,
        excluded=False,
        program=program,
        erased=False,
        refuse_reason=None,
    )
    _generate_rdi_dedup_demo(ba, user_root)


def generate_additional_doc_types() -> None:
    for doc_type_data in [
        {
            "label": "Disability Card",
            "key": "disability_card",
            "is_identity_document": True,
            "unique_for_individual": False,
            "valid_for_deduplication": False,
        },
        {
            "label": "Medical Certificate",
            "key": "medical_certificate",
            "is_identity_document": True,
            "unique_for_individual": False,
            "valid_for_deduplication": False,
        },
        {
            "label": "Proof of Legal Guardianship",
            "key": "proof_legal_guardianship",
            "is_identity_document": True,
            "unique_for_individual": False,
            "valid_for_deduplication": False,
        },
        {
            "label": "Temporary Protection Visa",
            "key": "temporary_protection_visa",
            "is_identity_document": True,
            "unique_for_individual": False,
            "valid_for_deduplication": False,
        },
        {
            "label": "Registration Token",
            "key": "registration_token",
            "is_identity_document": True,
            "unique_for_individual": False,
            "valid_for_deduplication": False,
        },
        {
            "label": "Receiver POI",
            "key": "receiver_poi",
            "is_identity_document": False,
            "unique_for_individual": False,
            "valid_for_deduplication": False,
        },
    ]:
        DocumentTypeFactory(**doc_type_data)


def create_household(
    household_args: dict | None = None, individual_args: dict | None = None
) -> tuple[Household, list[Individual]]:
    if household_args is None:
        household_args = {}
    if individual_args is None:
        individual_args = {}

    household_args["size"] = household_args.get("size", 2)
    household = HouseholdFactory(**household_args)

    individuals = IndividualFactory.create_batch(
        household.size, household=household, program=household.program, **individual_args
    )
    household.head_of_household = individuals[0]
    household.save()

    individuals_to_update = []
    for index, individual in enumerate(individuals):
        if index == 0:
            individual.relationship = "HEAD"
        individuals_to_update.append(individual)

    IndividualRoleInHousehold.objects.get_or_create(
        individual=individuals[1],
        household=household,
        role=ROLE_ALTERNATE,
        rdi_merge_status=MergeStatusModel.MERGED,
    )

    return household, individuals
