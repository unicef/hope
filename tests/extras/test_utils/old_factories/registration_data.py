import time
from typing import Any

from factory.django import DjangoModelFactory
import factory.fuzzy
from faker import Faker
from pytz import utc

from extras.test_utils.old_factories.account import UserFactory
from extras.test_utils.old_factories.program import ProgramFactory
from hope.models import (
    BusinessArea,
    ImportData,
    KoboImportData,
    Program,
    RegistrationDataImport,
    User,
)

faker = Faker()


class RegistrationDataImportFactory(DjangoModelFactory):
    class Meta:
        model = RegistrationDataImport
        django_get_or_create = ("name",)

    name = factory.LazyFunction(
        lambda: f"{faker.sentence(nb_words=3, variable_nb_words=True, ext_word_list=None)} - {time.time_ns()}"
    )
    status = "IN_REVIEW"
    import_date = factory.Faker(
        "date_time_this_decade",
        before_now=True,
        tzinfo=utc,
    )
    imported_by = factory.SubFactory(UserFactory)
    data_source = factory.fuzzy.FuzzyChoice(
        RegistrationDataImport.DATA_SOURCE_CHOICE,
        getter=lambda c: c[0],
    )
    number_of_individuals = factory.fuzzy.FuzzyInteger(100, 10000)
    number_of_households = factory.fuzzy.FuzzyInteger(3, 50)
    business_area = factory.LazyAttribute(lambda o: BusinessArea.objects.first())
    program = factory.SubFactory(ProgramFactory)
    erased = False

    @classmethod
    def _create(cls, target_class: Any, *args: Any, **kwargs: Any) -> RegistrationDataImport:
        created_at = kwargs.pop("created_at", None)
        obj = super()._create(target_class, *args, **kwargs)
        if created_at:
            obj.created_at = created_at
            obj.save()
        return obj


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


def _generate_rdi_dedup_demo(ba: BusinessArea, user_root: User) -> None:
    # Seeds a second program with biometric dedup enabled, an IN_REVIEW RDI
    # carrying real pending households/individuals, and one similarity pair so
    # the biometric review screen renders without a live engine roundtrip.
    # Lazy imports to avoid a circular dependency with old_factories.household.
    from extras.test_utils.old_factories.household import (
        PendingHouseholdFactory,
        PendingIndividualFactory,
    )
    from hope.apps.household.const import HOST
    from hope.models import (
        BeneficiaryGroup,
        DataCollectingType,
        DeduplicationEngineSimilarityPair,
    )

    dedup_program = ProgramFactory(
        name="Dedup Demo Program (sw)",
        code="ddp1",
        business_area=ba,
        status="ACTIVE",
        start_date="2024-01-01",
        end_date="2029-12-31",
        description="Program for exercising the deduplication flow in local dev.",
        budget="100000.00",
        frequency_of_payments="REGULAR",
        sector="EDUCATION",
        scope="UNICEF",
        cash_plus=False,
        data_collecting_type=DataCollectingType.objects.get(code="partial_individuals"),
        beneficiary_group=BeneficiaryGroup.objects.get(name="Social Workers"),
        biometric_deduplication_enabled=True,
        cycle__unicef_id="PC-23-0060-000002",
        cycle__title="Dedup Demo Cycle 1",
        cycle__status="DRAFT",
        cycle__start_date="2024-01-01",
        cycle__end_date="2024-12-31",
    )

    dedup_rdi = RegistrationDataImportFactory(
        name="Dedup demo - in review",
        status="IN_REVIEW",
        import_date="2026-04-23T09:00:00.000Z",
        imported_by=user_root,
        data_source="XLS",
        number_of_individuals=6,
        number_of_households=3,
        batch_duplicates=0,
        batch_possible_duplicates=1,
        batch_unique=5,
        golden_record_duplicates=0,
        golden_record_possible_duplicates=1,
        golden_record_unique=5,
        pull_pictures=True,
        business_area=ba,
        screen_beneficiary=False,
        excluded=False,
        program=dedup_program,
        erased=False,
        refuse_reason=None,
        deduplication_engine_status=RegistrationDataImport.DEDUP_ENGINE_FINISHED,
    )

    pending_heads: list = []
    for i in range(3):
        hh = PendingHouseholdFactory(
            registration_data_import=dedup_rdi,
            program=dedup_program,
            business_area=ba,
            size=2,
            residence_status=HOST,
        )
        head_kwargs = {
            "household": hh,
            "registration_data_import": dedup_rdi,
            "program": dedup_program,
            "business_area": ba,
            "relationship": "HEAD",
        }
        if i == 0:
            # Name-duplicate of the merged Stacey Freeman from generate_people_program — a
            # visual cue in the list plus a plausible dedup candidate for the engine stub.
            head_kwargs.update(
                given_name="Stacey",
                middle_name="",
                family_name="Freeman",
                full_name="Stacey Freeman",
            )
        head = PendingIndividualFactory(**head_kwargs)
        PendingIndividualFactory(
            household=hh,
            registration_data_import=dedup_rdi,
            program=dedup_program,
            business_area=ba,
            relationship="SON_DAUGHTER",
        )
        hh.head_of_household = head
        hh.save()
        pending_heads.append(head)

    # Seed one similarity pair so the review screen renders without hitting the engine.
    # CheckConstraint requires individual1 < individual2 on FK id ordering.
    ind1, ind2 = sorted((pending_heads[0], pending_heads[1]), key=lambda i: str(i.id))
    DeduplicationEngineSimilarityPair.objects.get_or_create(
        program=dedup_program,
        individual1=ind1,
        individual2=ind2,
        defaults={
            "similarity_score": "95.00",
            "status_code": DeduplicationEngineSimilarityPair.StatusCode.STATUS_200,
        },
    )


class ImportDataFactory(DjangoModelFactory):
    class Meta:
        model = ImportData

    status = ImportData.STATUS_FINISHED
    business_area_slug = "afghanistan"
    data_type = ImportData.XLSX
    number_of_households = factory.fuzzy.FuzzyInteger(5, 100)
    number_of_individuals = factory.fuzzy.FuzzyInteger(10, 300)
    error = ""
    validation_errors = ""
    created_by_id = factory.LazyAttribute(lambda o: UserFactory().id)
    file = factory.django.FileField(filename="test_data.xlsx")


class KoboImportDataFactory(DjangoModelFactory):
    class Meta:
        model = KoboImportData

    status = ImportData.STATUS_FINISHED
    business_area_slug = "afghanistan"
    data_type = ImportData.JSON
    number_of_households = factory.fuzzy.FuzzyInteger(5, 100)
    number_of_individuals = factory.fuzzy.FuzzyInteger(10, 300)
    error = ""
    validation_errors = ""
    created_by_id = factory.LazyAttribute(lambda o: UserFactory().id)
    kobo_asset_id = factory.LazyFunction(lambda: f"kobo_{time.time_ns()}")
    only_active_submissions = True
    pull_pictures = True
