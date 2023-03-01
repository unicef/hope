from collections import defaultdict

from django.db.models import Count, Q, QuerySet
from django.db.transaction import atomic

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.models import User
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import StorageFileFactory
from hct_mis_api.apps.core.models import BusinessArea, StorageFile
from hct_mis_api.apps.household.fixtures import (
    BankAccountInfoFactory,
    DocumentFactory,
    DocumentTypeFactory,
    create_household,
)
from hct_mis_api.apps.household.models import Document, Household
from hct_mis_api.apps.payment.fixtures import CashPlanFactory, PaymentRecordFactory
from hct_mis_api.apps.payment.models import PaymentRecord
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.targeting.models import TargetPopulation
from hct_mis_api.apps.targeting.services.targeting_stats_refresher import refresh_stats


def find_edopomoga_households() -> QuerySet[Household]:
    storage_file = StorageFile.objects.get(pk=3)
    return Household.objects.filter(storage_obj=storage_file, business_area__slug="ukraine").distinct()


def find_households_without_documents_or_iban() -> QuerySet[Household]:
    households_loaded_via_sf = (
        find_edopomoga_households()
        .filter(
            Q(
                Q(head_of_household__documents__document_number="0000000000")
                | Q(head_of_household__bank_account_info__bank_account_number="")
            ),
        )
        .distinct()
    )
    return households_loaded_via_sf


def find_paid_households() -> QuerySet[Household]:
    storage_file = StorageFile.objects.get(pk=3)
    households_loaded_via_sf = find_edopomoga_households()
    tax_ids_of_inds_loaded_via_sf = Document.objects.filter(
        individual__household__in=households_loaded_via_sf, type__type="TAX_ID"
    ).values_list("document_number", flat=True)
    hh_ids_not_loaded_via_sf = Household.objects.filter(
        Q(
            individuals__documents__document_number__in=tax_ids_of_inds_loaded_via_sf,
        )
        & ~Q(storage_obj=storage_file)
    ).values_list("id", flat=True)
    payment_records = PaymentRecord.objects.filter(
        household__id__in=hh_ids_not_loaded_via_sf,
        status__in=(
            PaymentRecord.STATUS_SUCCESS,
            PaymentRecord.STATUS_DISTRIBUTION_SUCCESS,
        ),
    )
    already_paid_households = payment_records.values("household").annotate(count=Count("household")).filter(count__gt=0)
    already_paid_households_ids = [x.get("household") for x in already_paid_households]
    already_paid_pairs = Document.objects.filter(
        individual__household__in=already_paid_households_ids, type__type="TAX_ID"
    ).values("document_number", "individual__household__unicef_id")
    loaded_via_sf_pairs = Document.objects.filter(
        individual__household__in=households_loaded_via_sf, type__type="TAX_ID"
    ).values("document_number", "individual__household__unicef_id")
    already_paid_documents_dict = {
        pair["document_number"]: pair["individual__household__unicef_id"] for pair in already_paid_pairs
    }
    loaded_via_sf_documents_dict = defaultdict(list)
    for pair in loaded_via_sf_pairs:
        loaded_via_sf_documents_dict[pair["document_number"]].append(str(pair["individual__household__unicef_id"]))
    already_paid_documents_set = set(already_paid_documents_dict.keys())
    loaded_via_sf_documents_set = set(loaded_via_sf_documents_dict.keys())
    intersect_docs = already_paid_documents_set.intersection(loaded_via_sf_documents_set)

    households_already_paid = []
    for doc in intersect_docs:
        households_already_paid.extend(loaded_via_sf_documents_dict[doc])
    return Household.objects.filter(unicef_id__in=households_already_paid, storage_obj=storage_file)


def find_duplicated_households() -> QuerySet[Household]:
    storage_file = StorageFile.objects.get(pk=3)
    households_loaded_via_sf = find_edopomoga_households()
    tax_ids_of_inds_loaded_via_sf = Document.objects.filter(
        individual__household__in=households_loaded_via_sf, type__type="TAX_ID"
    ).values_list("document_number", flat=True)
    documents = set(
        Document.objects.filter(
            document_number__in=tax_ids_of_inds_loaded_via_sf,
            individual__household__storage_obj__isnull=True,
        ).values_list("document_number", flat=True)
    )
    hh_ids_not_loaded_via_sf = Household.objects.filter(
        Q(
            individuals__documents__document_number__in=tax_ids_of_inds_loaded_via_sf,
        )
        & ~Q(storage_obj=storage_file)
    ).values_list("id", flat=True)
    paid_household_ids = PaymentRecord.objects.filter(
        household__id__in=hh_ids_not_loaded_via_sf,
        status__in=(
            PaymentRecord.STATUS_SUCCESS,
            PaymentRecord.STATUS_DISTRIBUTION_SUCCESS,
        ),
    ).values_list("household__id", flat=True)
    paid_documents = set(
        Document.objects.filter(
            individual__household_id__in=paid_household_ids,
            individual__household__storage_obj__isnull=True,
        ).values_list("document_number", flat=True)
    )
    not_paid_documents = documents - paid_documents
    edopomoga_duplicates = households_loaded_via_sf.filter(
        individuals__documents__document_number__in=not_paid_documents
    )
    return edopomoga_duplicates


def create_tp_with_hhs_ids(name: str, households: QuerySet[Household]) -> None:
    tp = TargetPopulation()
    tp.name = name
    tp.created_by = User.objects.get(email="jan.romaniak@tivix.com")
    tp.business_area = BusinessArea.objects.get(slug="ukraine")
    tp.program = Program.objects.get(name="edopomoga")
    tp.status = TargetPopulation.STATUS_LOCKED
    tp.save()
    tp.households.set(households)
    tp = refresh_stats(tp)
    tp.save()


@atomic
def create_tps() -> None:
    households_without_documents_or_iban = (find_households_without_documents_or_iban().distinct()).values_list(
        "id", flat=True
    )
    print(f"households_without_documents_or_iban: {households_without_documents_or_iban.count()}")
    create_tp_with_hhs_ids(
        "eDopomoga 1.12.2022 without tax id or iban",
        households_without_documents_or_iban,
    )
    household_already_received_assistance = (
        find_paid_households()
        .exclude(id__in=households_without_documents_or_iban)
        .distinct()
        .values_list("id", flat=True)
    )
    print(
        "household_already_received_assistance",
        household_already_received_assistance.count(),
    )
    create_tp_with_hhs_ids(
        "eDopomoga 1.12.2022 already received assistance",
        household_already_received_assistance,
    )
    duplicated_households_but_not_received_assistance = (
        (
            find_duplicated_households().exclude(
                id__in=households_without_documents_or_iban.union(household_already_received_assistance)
            )
        )
        .distinct()
        .values_list("id", flat=True)
    )
    print(
        "duplicated_households_but_not_received_assistance",
        duplicated_households_but_not_received_assistance.count(),
    )
    create_tp_with_hhs_ids(
        "eDopomoga 1.12.2022 duplicated in unicef but never received assistance",
        duplicated_households_but_not_received_assistance,
    )
    qs = find_edopomoga_households()
    print(f"all households: {qs.count()}")
    print(
        households_without_documents_or_iban.union(
            household_already_received_assistance,
            duplicated_households_but_not_received_assistance,
        ).count()
    )
    all_other_edopomoga_households = (
        qs.exclude(
            id__in=households_without_documents_or_iban.union(
                household_already_received_assistance,
                duplicated_households_but_not_received_assistance,
            )
        )
        .distinct()
        .values_list("id", flat=True)
    )
    print("all_other_edopomoga_households", all_other_edopomoga_households.count())
    create_tp_with_hhs_ids(
        "eDopomoga 1.12.2022 not meeting any of the criteria",
        all_other_edopomoga_households,
    )


class TestTpsCreation(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.storage_file = StorageFileFactory(id=3)
        UserFactory(email="jan.romaniak@tivix.com")
        cls.business_area = BusinessArea.objects.create(
            slug="ukraine",
            code="1234",
            name="Ukraine",
            long_name="the long name of ukraine",
            region_code="3245",
            region_name="UA",
            has_data_sharing_agreement=True,
        )
        ProgramFactory(business_area=cls.business_area, name="edopomoga")

        cls.cash_plan = CashPlanFactory(business_area=cls.business_area)
        cls.document_type = DocumentTypeFactory(type="TAX_ID")

        cls.setup_test_data_for_empty_tax_id_or_iban()
        cls.setup_already_paid()
        cls.setup_duplicated()

    @classmethod
    def setup_test_data_for_empty_tax_id_or_iban(cls) -> None:
        cls.household_edopomoga_empty_tax_id, (cls.individual_edopomoga_empty_tax_id,) = create_household(
            household_args={"size": 1, "business_area": cls.business_area}
        )
        cls.household_edopomoga_empty_tax_id.storage_obj = cls.storage_file
        cls.household_edopomoga_empty_tax_id.save()
        cls.individual_edopomoga_empty_tax_id.documents.add(
            DocumentFactory(
                individual=cls.individual_edopomoga_empty_tax_id, type=cls.document_type, document_number="0000000000"
            )
        )
        BankAccountInfoFactory(individual=cls.individual_edopomoga_empty_tax_id)
        cls.household_edopomoga_empty_iban, (cls.individual_edopomoga_empty_iban,) = create_household(
            household_args={"size": 1, "business_area": cls.business_area}
        )
        cls.household_edopomoga_empty_iban.storage_obj = cls.storage_file
        cls.household_edopomoga_empty_iban.save()
        cls.individual_edopomoga_empty_iban.documents.add(
            DocumentFactory(
                individual=cls.individual_edopomoga_empty_iban, type=cls.document_type, document_number="ASF123123"
            )
        )
        BankAccountInfoFactory(individual=cls.individual_edopomoga_empty_iban, bank_account_number="")

    @classmethod
    def setup_already_paid(cls) -> None:
        DOCUMENT_NUMBER_ONE = "1234567890"
        ##
        cls.household_edopomoga_already_paid, (cls.individual_edopomoga_already_paid,) = create_household(
            household_args={"size": 1, "business_area": cls.business_area}
        )
        cls.household_edopomoga_already_paid.storage_obj = cls.storage_file
        cls.household_edopomoga_already_paid.save()
        cls.individual_edopomoga_already_paid.documents.add(
            DocumentFactory(
                individual=cls.individual_edopomoga_already_paid,
                type=cls.document_type,
                document_number=DOCUMENT_NUMBER_ONE,
            )
        )
        BankAccountInfoFactory(individual=cls.individual_edopomoga_already_paid)
        cls.household_already_paid, (cls.individual_already_paid,) = create_household(
            household_args={"size": 1, "business_area": cls.business_area}
        )
        cls.household_already_paid.storage_obj = None
        cls.household_already_paid.save()
        PaymentRecordFactory(
            household=cls.household_already_paid,
            full_name=cls.individual_already_paid.full_name,
            business_area=cls.business_area,
            cash_plan=cls.cash_plan,
            status=PaymentRecord.STATUS_SUCCESS,
        )
        cls.individual_already_paid.documents.add(
            DocumentFactory(
                individual=cls.individual_already_paid, type=cls.document_type, document_number=DOCUMENT_NUMBER_ONE
            )
        )

    @classmethod
    def setup_duplicated(cls) -> None:
        DOCUMENT_NUMBER_TWO = "213821382138"
        ##
        cls.household_edopomoga_duplicated, (cls.individual_edopomoga_duplicated,) = create_household(
            household_args={"size": 1, "business_area": cls.business_area}
        )
        cls.household_edopomoga_duplicated.storage_obj = cls.storage_file
        cls.household_edopomoga_duplicated.save()
        cls.individual_edopomoga_duplicated.documents.add(
            DocumentFactory(
                individual=cls.individual_edopomoga_duplicated,
                type=cls.document_type,
                document_number=DOCUMENT_NUMBER_TWO,
            )
        )
        BankAccountInfoFactory(individual=cls.individual_edopomoga_duplicated)
        cls.household_duplicated, (cls.individual_duplicated,) = create_household(
            household_args={"size": 1, "business_area": cls.business_area}
        )
        cls.household_duplicated.storage_obj = None
        cls.household_duplicated.save()
        cls.individual_duplicated.documents.add(
            DocumentFactory(
                individual=cls.individual_already_paid, type=cls.document_type, document_number=DOCUMENT_NUMBER_TWO
            )
        )

    def test_households_without_documents_or_iban(self) -> None:
        found_empty_tax_id_or_iban = list(find_households_without_documents_or_iban().values_list("id", flat=True))
        self.assertIn(self.household_edopomoga_empty_tax_id.id, found_empty_tax_id_or_iban)
        self.assertIn(self.household_edopomoga_empty_iban.id, found_empty_tax_id_or_iban)
        self.assertEqual(len(found_empty_tax_id_or_iban), 2)

    def test_households_already_received_support(self) -> None:
        found_paid_household = list(find_paid_households().values_list("id", flat=True))
        self.assertIn(self.household_edopomoga_already_paid.id, found_paid_household)
        self.assertEqual(len(found_paid_household), 1)

    def test_household_duplicated_not_paid(self) -> None:
        found_duplicated_household = list(find_duplicated_households().values_list("id", flat=True))
        self.assertIn(self.household_edopomoga_duplicated.id, found_duplicated_household)
        self.assertEqual(len(found_duplicated_household), 1)

    def test_create_tps(self) -> None:
        create_tps()
        empty_tax_id_or_iban_tp = TargetPopulation.objects.get(name="eDopomoga 1.12.2022 without tax id or iban")
        already_received_assistance_tp = TargetPopulation.objects.get(
            name="eDopomoga 1.12.2022 already received assistance"
        )
        duplicates_tp = TargetPopulation.objects.get(
            name="eDopomoga 1.12.2022 duplicated in unicef but never received assistance"
        )
        all_others_tp = TargetPopulation.objects.get(name="eDopomoga 1.12.2022 not meeting any of the criteria")

        all_edopomoga_households = find_edopomoga_households().count()
        self.assertEqual(all_edopomoga_households, 4)
        self.assertEqual(empty_tax_id_or_iban_tp.households.count(), 2)
        self.assertEqual(already_received_assistance_tp.households.count(), 1)
        self.assertEqual(duplicates_tp.households.count(), 1)
        self.assertEqual(all_others_tp.households.count(), all_edopomoga_households - 4)
