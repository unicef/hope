import datetime
from unittest import mock
from unittest.mock import patch

from django.forms import model_to_dict
from flags.models import FlagState
from freezegun import freeze_time
import pytest

from extras.test_utils.factories import (
    AreaFactory,
    AreaTypeFactory,
    BusinessAreaFactory,
    CountryFactory,
    HouseholdCollectionFactory,
    HouseholdFactory,
    IndividualCollectionFactory,
    IndividualFactory,
    IndividualRoleInHouseholdFactory,
    PendingHouseholdFactory,
    PendingIndividualFactory,
    ProgramFactory,
    RegistrationDataImportFactory,
    SanctionListFactory,
)
from hope.apps.household.const import BROTHER_SISTER, COUSIN, HEAD, NON_BENEFICIARY, ROLE_ALTERNATE
from hope.apps.registration_data.tasks.rdi_merge import RdiMergeTask
from hope.models import Household, Individual, KoboImportedSubmission, PendingHousehold, RegistrationDataImport
from hope.models.utils import MergeStatusModel

pytestmark = [pytest.mark.django_db, pytest.mark.usefixtures("mock_elasticsearch")]


@pytest.fixture
def afghanistan_country() -> object:
    return CountryFactory(name="Afghanistan", short_name="Afghanistan", iso_code2="AF", iso_code3="AFG", iso_num="0004")


@pytest.fixture
def business_area() -> object:
    business_area = BusinessAreaFactory(slug="afghanistan", name="Afghanistan")
    business_area.postpone_deduplication = True
    business_area.save(update_fields=["postpone_deduplication"])
    return business_area


@pytest.fixture
def program(business_area: object) -> object:
    return ProgramFactory(business_area=business_area)


@pytest.fixture
def rdi(business_area: object, program: object) -> object:
    registration_data_import = RegistrationDataImportFactory(business_area=business_area, program=program)
    registration_data_import.business_area.postpone_deduplication = True
    registration_data_import.business_area.save(update_fields=["postpone_deduplication"])
    return registration_data_import


@pytest.fixture
def areas(afghanistan_country: object) -> dict:
    area_type_level_1 = AreaTypeFactory(name="State1", area_level=1, country=afghanistan_country)
    area_type_level_2 = AreaTypeFactory(name="State2", area_level=2, country=afghanistan_country)
    area_type_level_3 = AreaTypeFactory(name="State3", area_level=3, country=afghanistan_country)
    area_type_level_4 = AreaTypeFactory(name="State4", area_level=4, country=afghanistan_country)

    area1 = AreaFactory(name="City Test1", area_type=area_type_level_1, p_code="area1")
    area2 = AreaFactory(name="City Test2", area_type=area_type_level_2, p_code="area2", parent=area1)
    area3 = AreaFactory(name="City Test3", area_type=area_type_level_3, p_code="area3", parent=area2)
    area4 = AreaFactory(name="City Test4", area_type=area_type_level_4, p_code="area4", parent=area3)
    return {"area1": area1, "area2": area2, "area3": area3, "area4": area4}


@pytest.fixture
def pending_head_individual(rdi: object, business_area: object, program: object) -> object:
    return PendingIndividualFactory(
        full_name="Benjamin Butler",
        given_name="Benjamin",
        family_name="Butler",
        relationship=HEAD,
        birth_date=datetime.date(1962, 2, 2),
        sex="MALE",
        registration_data_import=rdi,
        business_area=business_area,
        program=program,
        email="fake_email_1@com",
        wallet_name="Wallet Name 1",
        blockchain_name="Blockchain Name 1",
        wallet_address="Wallet Address 1",
        unicef_id="IND-9",
        household=None,
    )


@pytest.fixture
def pending_household_factory(rdi: object, business_area: object, program: object):
    def _create(head: object, **kwargs) -> PendingHousehold:
        defaults = {
            "registration_data_import": rdi,
            "business_area": business_area,
            "program": program,
            "head_of_household": head,
            "create_role": False,
        }
        defaults.update(kwargs)
        return PendingHouseholdFactory(**defaults)

    return _create


@pytest.fixture
def create_pending_individuals(rdi: object, business_area: object, program: object):
    def _create(household: PendingHousehold, head: object) -> list:
        return [
            head,
            PendingIndividualFactory(
                full_name="Robin Ford",
                given_name="Robin",
                family_name="Ford",
                relationship=COUSIN,
                birth_date=datetime.date(2017, 2, 15),
                sex="MALE",
                registration_data_import=rdi,
                business_area=business_area,
                program=program,
                household=household,
                email="fake_email_2@com",
                unicef_id="IND-8",
            ),
            PendingIndividualFactory(
                full_name="Timothy Perry",
                given_name="Timothy",
                family_name="Perry",
                relationship=COUSIN,
                birth_date=datetime.date(2011, 12, 21),
                sex="MALE",
                registration_data_import=rdi,
                business_area=business_area,
                program=program,
                household=household,
                email="fake_email_3@com",
            ),
            PendingIndividualFactory(
                full_name="Eric Torres",
                given_name="Eric",
                family_name="Torres",
                relationship=BROTHER_SISTER,
                birth_date=datetime.date(2006, 3, 23),
                sex="MALE",
                registration_data_import=rdi,
                business_area=business_area,
                program=program,
                household=household,
                email="fake_email_4@com",
            ),
            PendingIndividualFactory(
                full_name="Baz Bush",
                given_name="Baz",
                family_name="Bush",
                relationship=BROTHER_SISTER,
                birth_date=datetime.date(2005, 2, 21),
                sex="MALE",
                registration_data_import=rdi,
                business_area=business_area,
                program=program,
                household=household,
                email="fake_email_5@com",
            ),
            PendingIndividualFactory(
                full_name="Liz Female",
                given_name="Liz",
                family_name="Female",
                relationship=BROTHER_SISTER,
                birth_date=datetime.date(2005, 10, 10),
                sex="FEMALE",
                registration_data_import=rdi,
                business_area=business_area,
                program=program,
                household=household,
                phone_no="+41 (0) 78 927 2696",
                phone_no_alternative="+41 (0) 78 927 2696",
                phone_no_valid=None,
                phone_no_alternative_valid=None,
                email="fake_email_6@com",
            ),
            PendingIndividualFactory(
                full_name="Jenna Franklin",
                given_name="Jenna",
                family_name="Franklin",
                relationship=BROTHER_SISTER,
                birth_date=datetime.date(1996, 11, 29),
                sex="FEMALE",
                registration_data_import=rdi,
                business_area=business_area,
                program=program,
                household=household,
                phone_no="wrong-phone",
                phone_no_alternative="definitely-wrong-phone",
                phone_no_valid=None,
                phone_no_alternative_valid=None,
                email="fake_email_7@com",
            ),
            PendingIndividualFactory(
                full_name="Bob Jackson",
                given_name="Bob",
                family_name="Jackson",
                relationship=BROTHER_SISTER,
                birth_date=datetime.date(1956, 3, 3),
                sex="MALE",
                registration_data_import=rdi,
                business_area=business_area,
                program=program,
                household=household,
                email="",
            ),
        ]

    return _create


@freeze_time("2022-01-01")
def test_merge_rdi_and_recalculation(
    rdi: object,
    areas: dict,
    pending_head_individual: object,
    pending_household_factory,
    create_pending_individuals,
    django_capture_on_commit_callbacks,
) -> None:
    household = pending_household_factory(
        pending_head_individual,
        admin4=areas["area4"],
        admin3=areas["area3"],
        admin2=areas["area2"],
        admin1=areas["area1"],
        zip_code="00-123",
        detail_id="123456123",
        kobo_submission_uuid="c09130af-6c9c-4dba-8c7f-1b2ff1970d19",
        kobo_submission_time="2022-02-22T12:22:22",
        flex_fields={"enumerator_id": 1234567890},
        program=rdi.program,
    )
    dct = rdi.program.data_collecting_type
    dct.recalculate_composition = True
    dct.save()

    create_pending_individuals(household, pending_head_individual)
    household.head_of_household = pending_head_individual
    household.save(update_fields=["head_of_household"])

    with django_capture_on_commit_callbacks(execute=True):
        RdiMergeTask().execute(rdi.pk)

    households = Household.objects.all()
    individuals = Individual.objects.all()

    household = households.first()

    assert households.count() == 1
    assert individuals.count() == 8
    assert household.flex_fields.get("enumerator_id") == 1234567890
    assert household.detail_id == "123456123"

    kobo_import_submission_qs = KoboImportedSubmission.objects.all()
    kobo_import_submission = kobo_import_submission_qs.first()
    assert kobo_import_submission_qs.count() == 1
    assert str(kobo_import_submission.kobo_submission_uuid) == "c09130af-6c9c-4dba-8c7f-1b2ff1970d19"
    assert kobo_import_submission.kobo_asset_id == "123456123"
    assert str(kobo_import_submission.kobo_submission_time) == "2022-02-22 12:22:22+00:00"

    individual_with_valid_phone_data = Individual.objects.filter(given_name="Liz").first()
    individual_with_invalid_phone_data = Individual.objects.filter(given_name="Jenna").first()

    assert individual_with_valid_phone_data.phone_no_valid is True
    assert individual_with_valid_phone_data.phone_no_alternative_valid is True

    assert individual_with_invalid_phone_data.phone_no_valid is False
    assert individual_with_invalid_phone_data.phone_no_alternative_valid is False

    assert Individual.objects.filter(full_name="Baz Bush").first().email == "fake_email_5@com"
    assert Individual.objects.filter(full_name="Benjamin Butler").first().email == "fake_email_1@com"
    assert Individual.objects.filter(full_name="Bob Jackson").first().email == ""
    assert Individual.objects.filter(full_name="Benjamin Butler").first().wallet_name == "Wallet Name 1"
    assert Individual.objects.filter(full_name="Benjamin Butler").first().blockchain_name == "Blockchain Name 1"
    assert Individual.objects.filter(full_name="Benjamin Butler").first().wallet_address == "Wallet Address 1"

    household_data = model_to_dict(
        household,  # type: ignore[arg-type]
        (
            "female_age_group_0_5_count",
            "female_age_group_6_11_count",
            "female_age_group_12_17_count",
            "female_age_group_18_59_count",
            "female_age_group_60_count",
            "male_age_group_0_5_count",
            "male_age_group_6_11_count",
            "male_age_group_12_17_count",
            "male_age_group_18_59_count",
            "male_age_group_60_count",
            "children_count",
            "size",
            "admin1",
            "admin2",
            "admin3",
            "admin4",
            "zip_code",
        ),
    )

    expected = {
        "female_age_group_0_5_count": 0,
        "female_age_group_6_11_count": 0,
        "female_age_group_12_17_count": 1,
        "female_age_group_18_59_count": 1,
        "female_age_group_60_count": 0,
        "male_age_group_0_5_count": 1,
        "male_age_group_6_11_count": 1,
        "male_age_group_12_17_count": 2,
        "male_age_group_18_59_count": 1,
        "male_age_group_60_count": 1,
        "children_count": 5,
        "size": 8,
        "admin1": areas["area1"].id,
        "admin2": areas["area2"].id,
        "admin3": areas["area3"].id,
        "admin4": areas["area4"].id,
        "zip_code": "00-123",
    }
    assert household_data == expected


@freeze_time("2022-01-01")
@patch("hope.apps.registration_data.tasks.rdi_merge.check_against_sanction_list_pre_merge")
def test_merge_rdi_sanction_list_check(
    sanction_execute_mock: mock.MagicMock,
    rdi: object,
    areas: dict,
    pending_head_individual: object,
    pending_household_factory,
    create_pending_individuals,
    django_capture_on_commit_callbacks,
) -> None:
    household = pending_household_factory(
        pending_head_individual,
        admin4=areas["area4"],
        admin3=areas["area3"],
        admin2=areas["area2"],
        admin1=areas["area1"],
        zip_code="00-123",
        detail_id="123456123",
        kobo_submission_uuid="c09130af-6c9c-4dba-8c7f-1b2ff1970d19",
        kobo_submission_time="2022-02-22T12:22:22",
        flex_fields={"enumerator_id": 1234567890},
    )
    sanction_list = SanctionListFactory()
    dct = rdi.program.data_collecting_type
    dct.recalculate_composition = True
    dct.save()
    rdi.screen_beneficiary = True
    rdi.save(update_fields=["screen_beneficiary"])
    program = rdi.program
    program.sanction_lists.add(sanction_list)
    program.refresh_from_db()
    create_pending_individuals(household, pending_head_individual)
    with django_capture_on_commit_callbacks(execute=True):
        RdiMergeTask().execute(rdi.pk)
    sanction_execute_mock.assert_called_once()
    sanction_execute_mock.reset_mock()


@freeze_time("2022-01-01")
@patch("hope.apps.registration_data.tasks.rdi_merge.check_against_sanction_list_pre_merge")
def test_merge_rdi_sanction_list_check_program_without_list(
    sanction_execute_mock: mock.MagicMock,
    rdi: object,
    areas: dict,
    pending_head_individual: object,
    pending_household_factory,
    create_pending_individuals,
    django_capture_on_commit_callbacks,
) -> None:
    household = pending_household_factory(
        pending_head_individual,
        admin4=areas["area4"],
        admin3=areas["area3"],
        admin2=areas["area2"],
        admin1=areas["area1"],
        zip_code="00-123",
        detail_id="123456123",
        kobo_submission_uuid="c09130af-6c9c-4dba-8c7f-1b2ff1970d19",
        kobo_submission_time="2022-02-22T12:22:22",
        flex_fields={"enumerator_id": 1234567890},
    )
    dct = rdi.program.data_collecting_type
    dct.recalculate_composition = True
    dct.save()

    rdi.screen_beneficiary = True
    rdi.save(update_fields=["screen_beneficiary"])
    create_pending_individuals(household, pending_head_individual)
    with django_capture_on_commit_callbacks(execute=True):
        RdiMergeTask().execute(rdi.pk)
    sanction_execute_mock.assert_not_called()


@freeze_time("2022-01-01")
@patch("hope.apps.registration_data.tasks.rdi_merge.check_against_sanction_list_pre_merge")
def test_merge_rdi_sanction_list_check_rdi_false(
    sanction_execute_mock: mock.MagicMock,
    rdi: object,
    areas: dict,
    pending_head_individual: object,
    pending_household_factory,
    create_pending_individuals,
    django_capture_on_commit_callbacks,
) -> None:
    household = pending_household_factory(
        pending_head_individual,
        admin4=areas["area4"],
        admin3=areas["area3"],
        admin2=areas["area2"],
        admin1=areas["area1"],
        zip_code="00-123",
        detail_id="123456123",
        kobo_submission_uuid="c09130af-6c9c-4dba-8c7f-1b2ff1970d19",
        kobo_submission_time="2022-02-22T12:22:22",
        flex_fields={"enumerator_id": 1234567890},
    )
    rdi.screen_beneficiary = False
    rdi.save(update_fields=["screen_beneficiary"])
    create_pending_individuals(household, pending_head_individual)
    with django_capture_on_commit_callbacks(execute=True):
        RdiMergeTask().execute(rdi.pk)
    sanction_execute_mock.assert_not_called()


@pytest.mark.parametrize("household_representation_exists", [True, False, None])
def test_merge_rdi_create_collections(
    household_representation_exists: bool | None,
    rdi: object,
    business_area: object,
    pending_head_individual: object,
    pending_household_factory,
    create_pending_individuals,
    django_capture_on_commit_callbacks,
) -> None:
    program_2 = ProgramFactory(business_area=rdi.business_area)
    rdi.data_source = RegistrationDataImport.PROGRAM_POPULATION
    rdi.save(update_fields=["data_source"])
    imported_household = pending_household_factory(
        pending_head_individual,
        unicef_id="HH-9",
        program=rdi.program,
        rdi_merge_status=MergeStatusModel.PENDING,
    )
    create_pending_individuals(imported_household, pending_head_individual)
    individual_without_collection = IndividualFactory(
        unicef_id="IND-9",
        business_area=business_area,
        program=program_2,
        household=None,
        individual_collection=None,
    )
    individual_without_collection.save(update_fields=["individual_collection"])

    individual_collection = IndividualCollectionFactory()
    IndividualFactory(
        unicef_id="IND-8",
        business_area=business_area,
        program=program_2,
        individual_collection=individual_collection,
        household=None,
    )
    household = None
    household_collection = None
    if household_representation_exists is not None:
        household = HouseholdFactory(
            head_of_household=individual_without_collection,
            business_area=business_area,
            program=program_2,
            unicef_id="HH-9",
            create_role=False,
        )
        household.household_collection = None
        household.save()
        if household_representation_exists:
            household_collection = HouseholdCollectionFactory()
            household.household_collection = household_collection
            household.save()

    with django_capture_on_commit_callbacks(execute=True):
        RdiMergeTask().execute(rdi.pk)

    individual_without_collection.refresh_from_db()
    assert individual_without_collection.individual_collection is not None
    assert individual_without_collection.individual_collection.individuals.count() == 2
    assert individual_collection.individuals.count() == 2
    if household_representation_exists is not None:
        if household_representation_exists:
            household_collection.refresh_from_db()
            assert household_collection.households.count() == 2
        else:
            household.refresh_from_db()
            assert household.household_collection is not None
            assert household.household_collection.households.count() == 2


def test_merging_external_collector(
    rdi: object,
    areas: dict,
    pending_head_individual: object,
    pending_household_factory,
    create_pending_individuals,
    django_capture_on_commit_callbacks,
) -> None:
    household = pending_household_factory(
        pending_head_individual,
        admin4=areas["area4"],
        zip_code="00-123",
    )
    create_pending_individuals(household, pending_head_individual)
    external_collector = PendingIndividualFactory(
        full_name="External Collector",
        given_name="External",
        family_name="Collector",
        relationship=NON_BENEFICIARY,
        birth_date=datetime.date(1962, 2, 2),
        sex="OTHER",
        registration_data_import=rdi,
        business_area=rdi.business_area,
        program=rdi.program,
        email="xd@com",
        household=None,
    )
    IndividualRoleInHouseholdFactory(
        individual=external_collector,
        household=household,
        role=ROLE_ALTERNATE,
        rdi_merge_status=MergeStatusModel.PENDING,
    )
    with django_capture_on_commit_callbacks(execute=True):
        RdiMergeTask().execute(rdi.pk)


@patch.dict(
    "os.environ",
    {
        "DEDUPLICATION_ENGINE_API_KEY": "dedup_api_key",
        "DEDUPLICATION_ENGINE_API_URL": "http://dedup-fake-url.com",
    },
)
@mock.patch(
    "hope.apps.registration_data.services.biometric_deduplication.BiometricDeduplicationService.report_individuals_status"
)
@mock.patch(
    "hope.apps.registration_data.services.biometric_deduplication.BiometricDeduplicationService.create_grievance_tickets_for_duplicates"
)
@mock.patch(
    "hope.apps.registration_data.services.biometric_deduplication.BiometricDeduplicationService.update_rdis_deduplication_statistics"
)
def test_merge_biometric_deduplication_enabled(
    update_rdis_deduplication_statistics_mock: mock.Mock,
    create_grievance_tickets_for_duplicates_mock: mock.Mock,
    report_individuals_status_mock: mock.Mock,
    rdi: object,
    areas: dict,
    pending_head_individual: object,
    pending_household_factory,
    create_pending_individuals,
    django_capture_on_commit_callbacks,
) -> None:
    FlagState.objects.get_or_create(
        name="BIOMETRIC_DEDUPLICATION_REPORT_INDIVIDUALS_STATUS",
        condition="boolean",
        value="True",
        required=False,
    )

    program = rdi.program
    program.biometric_deduplication_enabled = True
    program.save(update_fields=["biometric_deduplication_enabled"])
    household = pending_household_factory(
        pending_head_individual,
        admin4=areas["area4"],
        zip_code="00-123",
    )
    create_pending_individuals(household, pending_head_individual)
    with django_capture_on_commit_callbacks(execute=True):
        RdiMergeTask().execute(rdi.pk)
    create_grievance_tickets_for_duplicates_mock.assert_called_once_with(rdi)
    update_rdis_deduplication_statistics_mock.assert_called_once_with(program, exclude_rdi=rdi)

    args, _ = report_individuals_status_mock.call_args
    assert args[0] == program.slug
    assert set(args[1]) == {
        str(_id) for _id in Individual.objects.filter(registration_data_import=rdi).values_list("id", flat=True)
    }
    assert args[2] == "merged"


def test_merge_empty_rdi(rdi: object, django_capture_on_commit_callbacks) -> None:
    with django_capture_on_commit_callbacks(execute=True):
        RdiMergeTask().execute(rdi.pk)
    rdi.refresh_from_db()
    assert rdi.status == RegistrationDataImport.MERGED
