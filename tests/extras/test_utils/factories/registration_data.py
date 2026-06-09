"""Registration data related factories."""

from decimal import Decimal
from typing import Any

import factory
from factory.django import DjangoModelFactory

from hope.models import (
    BusinessArea,
    DeduplicationEngineSimilarityPair,
    ImportData,
    KoboImportData,
    RegistrationDataImport,
    User,
)

from .account import UserFactory
from .core import BusinessAreaFactory
from .program import ProgramFactory


class ImportDataFactory(DjangoModelFactory):
    class Meta:
        model = ImportData

    status = ImportData.STATUS_PENDING
    data_type = ImportData.XLSX
    business_area_slug = ""
    file = factory.django.FileField(filename="test_data.xlsx")


class KoboImportDataFactory(DjangoModelFactory):
    class Meta:
        model = KoboImportData

    status = ImportData.STATUS_FINISHED
    data_type = ImportData.JSON
    business_area_slug = "afghanistan"
    kobo_asset_id = factory.Sequence(lambda n: f"kobo_asset_{n}")
    only_active_submissions = True
    pull_pictures = True


class RegistrationDataImportFactory(DjangoModelFactory):
    class Meta:
        model = RegistrationDataImport

    name = factory.Sequence(lambda n: f"RDI {n}")
    data_source = RegistrationDataImport.XLS
    status = RegistrationDataImport.MERGED
    number_of_individuals = 1
    number_of_households = 1
    imported_by = factory.SubFactory(UserFactory)
    business_area = factory.SubFactory(BusinessAreaFactory)
    program = factory.SubFactory(ProgramFactory, business_area=factory.SelfAttribute("..business_area"))


class DeduplicationEngineSimilarityPairFactory(DjangoModelFactory):
    class Meta:
        model = DeduplicationEngineSimilarityPair

    program = factory.SubFactory(ProgramFactory)
    individual1 = factory.SubFactory(
        "extras.test_utils.factories.household.IndividualFactory",
        program=factory.SelfAttribute("..program"),
    )
    individual2 = factory.SubFactory(
        "extras.test_utils.factories.household.IndividualFactory",
        program=factory.SelfAttribute("..program"),
    )
    similarity_score = Decimal("55.55")
    status_code = DeduplicationEngineSimilarityPair.StatusCode.STATUS_200

    @classmethod
    def _create(cls, model_class: Any, *args: Any, **kwargs: Any) -> DeduplicationEngineSimilarityPair:
        individual1 = kwargs.get("individual1")
        individual2 = kwargs.get("individual2")
        if individual1 and individual2 and individual1.id > individual2.id:
            kwargs["individual1"], kwargs["individual2"] = individual2, individual1

        return super()._create(model_class, *args, **kwargs)


def _generate_rdi_dedup_demo(ba: BusinessArea, user_root: User) -> None:
    # Seeds a second program with biometric dedup enabled, an IN_REVIEW RDI
    # carrying real pending households/individuals, and one similarity pair so
    # the biometric review screen renders without a live engine roundtrip.
    # Lazy imports to avoid a circular dependency with old_factories.household.
    from extras.test_utils.factories import (
        PendingHouseholdFactory,
        PendingIndividualFactory,
    )
    from hope.apps.household.const import HOST
    from hope.models import (
        BeneficiaryGroup,
        DataCollectingType,
        DeduplicationEngineSimilarityPair,
        PaymentPlanPurpose,
    )

    default_purpose, _ = PaymentPlanPurpose.objects.get_or_create(name="Default Purpose")
    dedup_program = ProgramFactory.create(
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
        payment_plan_purposes=[default_purpose],
    )

    dedup_rdi = RegistrationDataImportFactory.create(
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
        hh = PendingHouseholdFactory.create(
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
        head = PendingIndividualFactory.create(**head_kwargs)
        PendingIndividualFactory.create(
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

    def _make_cw_rdi(name: str, country_workspace_id: str, num_households: int, cw_id_prefix: str) -> None:
        rdi = RegistrationDataImportFactory.create(
            name=name,
            status=RegistrationDataImport.LOADING,
            import_date="2026-04-23T09:00:00.000Z",
            imported_by=user_root,
            data_source="API",
            country_workspace_id=country_workspace_id,
            number_of_individuals=num_households * 2,
            number_of_households=num_households,
            batch_duplicates=0,
            batch_possible_duplicates=0,
            batch_unique=num_households * 2,
            golden_record_duplicates=0,
            golden_record_possible_duplicates=0,
            golden_record_unique=num_households * 2,
            pull_pictures=True,
            business_area=ba,
            screen_beneficiary=False,
            excluded=False,
            program=dedup_program,
            erased=False,
            refuse_reason=None,
        )
        for hh_idx in range(num_households):
            hh = PendingHouseholdFactory.create(
                registration_data_import=rdi,
                program=dedup_program,
                business_area=ba,
                size=2,
                residence_status=HOST,
            )
            head = PendingIndividualFactory.create(
                household=hh,
                registration_data_import=rdi,
                program=dedup_program,
                business_area=ba,
                relationship="HEAD",
                country_workspace_id=f"{cw_id_prefix}-{hh_idx * 2}",
            )
            PendingIndividualFactory.create(
                household=hh,
                registration_data_import=rdi,
                program=dedup_program,
                business_area=ba,
                relationship="SON_DAUGHTER",
                country_workspace_id=f"{cw_id_prefix}-{hh_idx * 2 + 1}",
            )
            hh.head_of_household = head
            hh.save()

    _make_cw_rdi("CW stub: 3 findings", "cw-stub-rdi-a", 2, "cw-ind-a")
    _make_cw_rdi("CW stub: empty", "cw-stub-rdi-b", 1, "cw-ind-b")
    _make_cw_rdi("CW stub: paginated", "cw-stub-rdi-c", 3, "cw-ind-c")
    _make_cw_rdi("CW stub: missing on engine", "cw-stub-rdi-d", 1, "cw-ind-d")
