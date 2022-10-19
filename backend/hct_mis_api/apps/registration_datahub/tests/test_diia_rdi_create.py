from django.core.exceptions import ValidationError
from django.forms import model_to_dict

from django_countries.fields import Country

from hct_mis_api.apps.core.base_test_case import BaseElasticSearchTestCase
from hct_mis_api.apps.household.models import (
    DISABLED,
    IDENTIFICATION_TYPE_TAX_ID,
    MARITAL_STATUS_CHOICE,
    NOT_DISABLED,
    RELATIONSHIP_CHOICE,
)
from hct_mis_api.apps.registration_datahub.models import (
    DiiaHousehold,
    ImportedDocument,
    ImportedHousehold,
    ImportedIndividual,
    RegistrationDataImportDatahub,
)


class TestRdiDiiaCreateTask(BaseElasticSearchTestCase):
    databases = "__all__"
    fixtures = [
        "hct_mis_api/apps/geo/fixtures/data.json",
        "hct_mis_api/apps/core/fixtures/data.json",
        "hct_mis_api/apps/registration_datahub/fixtures/diiadata.json",
        "hct_mis_api/apps/registration_datahub/fixtures/diiadata_stg.json",
    ]

    @classmethod
    def setUpTestData(cls):
        from hct_mis_api.apps.registration_datahub.tasks.rdi_diia_create import (
            RdiDiiaCreateTask,
        )

        cls.RdiDiiaCreateTask = RdiDiiaCreateTask
        super().setUpTestData()

    def test_execute_correct_data(self):
        rdi = self.RdiDiiaCreateTask().create_rdi(None, "Test import Diia")
        self.RdiDiiaCreateTask().execute(rdi.pk, diia_hh_ids=[1, 2])

        households = ImportedHousehold.objects.all()
        individuals = ImportedIndividual.objects.all()

        self.assertEqual(2, DiiaHousehold.objects.filter(status=DiiaHousehold.STATUS_IMPORTED).count())

        self.assertEqual(2, households.count())
        self.assertEqual(5, individuals.count())

        individual = individuals.get(full_name="Erik Duarte")
        self.assertEqual(3, individual.documents.count())
        self.assertEqual(1, individual.bank_account_info.count())
        self.assertEqual(
            str(individual.documents.filter(document_number="VPO-DOC-2222").first().doc_date), "2022-04-29"
        )
        self.assertEqual(
            individual.documents.filter(document_number="123412341234999222").first().type.type,
            IDENTIFICATION_TYPE_TAX_ID,
        )

        individual_2 = individuals.get(full_name="Sam Bautista")
        self.assertEqual(str(individual_2.birth_date), "2009-06-16")

        individuals_obj_data = model_to_dict(
            individual,
            ("sex", "age", "marital_status", "relationship", "middle_name"),
        )
        expected = {
            "relationship": "HEAD",
            "sex": "MALE",
            "middle_name": "Mid",
            "marital_status": "MARRIED",
        }
        self.assertEqual(individuals_obj_data, expected)

        household_obj_data = model_to_dict(individual.household, ("country", "size", "diia_rec_id", "address"))
        expected = {
            "country": Country(code="UA"),
            "size": 3,
            "diia_rec_id": "222222",
            "address": "Ліста майдан, 3, кв. 257, 78242, Мелітополь, Чернівецька область, Ukraine",
        }
        self.assertEqual(household_obj_data, expected)

    def test_execute_staging_data_tax_id_error(self):
        self.assertEqual(0, ImportedHousehold.objects.all().count())
        self.assertEqual(0, ImportedIndividual.objects.all().count())

        rdi = self.RdiDiiaCreateTask().create_rdi(None, "Test import Diia")
        self.RdiDiiaCreateTask().execute(rdi.pk, diia_hh_ids=[991, 992, 993, 994])

        self.assertEqual(DiiaHousehold.objects.filter(status=DiiaHousehold.STATUS_IMPORTED).count(), 3)
        self.assertEqual(DiiaHousehold.objects.filter(status=DiiaHousehold.STATUS_TAX_ID_ERROR).count(), 1)
        self.assertEqual(ImportedDocument.objects.filter(document_number="1234567892222").count(), 1)
        self.assertEqual(ImportedHousehold.objects.all().count(), 3)
        self.assertEqual(ImportedIndividual.objects.all().count(), 9)
        self.assertEqual(
            RegistrationDataImportDatahub.objects.get(id=rdi.datahub_id).import_data.number_of_households, 3
        )
        self.assertEqual(
            RegistrationDataImportDatahub.objects.get(id=rdi.datahub_id).import_data.number_of_individuals, 9
        )
        rdi.refresh_from_db()
        self.assertEqual(rdi.number_of_households, 3)
        self.assertEqual(rdi.number_of_individuals, 9)

    def test_create_duplicated_imported_households(self):
        self.assertEqual(0, ImportedHousehold.objects.all().count())
        self.assertEqual(0, ImportedIndividual.objects.all().count())

        rdi = self.RdiDiiaCreateTask().create_rdi(None, "Test import Diia")
        self.RdiDiiaCreateTask().execute(rdi.pk, diia_hh_ids=[1, 2])

        self.assertEqual(2, ImportedHousehold.objects.all().count())
        self.assertEqual(5, ImportedIndividual.objects.all().count())
        rdi = self.RdiDiiaCreateTask().create_rdi(None, "Test import Diia 2")

        with self.assertRaisesRegex(ValidationError, ".*Rdi doesn't found any records within status to import.*"):
            self.RdiDiiaCreateTask().execute(rdi.pk, diia_hh_ids=[1, 2])

        self.assertEqual(2, ImportedHousehold.objects.all().count())
        self.assertEqual(5, ImportedIndividual.objects.all().count())

    def test_execute_staging_data_mark_registration_data_import(self):
        rdi = self.RdiDiiaCreateTask().create_rdi(None, "Test import Diia")
        self.RdiDiiaCreateTask().execute(rdi.pk, diia_hh_ids=[991, 992, 993])
        self.assertEqual(
            DiiaHousehold.objects.filter(registration_data_import__isnull=False, id__in=[991, 992, 993]).count(), 3
        )

    def test_execute_staging_data_choices_conversion(self):
        rdi = self.RdiDiiaCreateTask().create_rdi(None, "Test import Diia")
        self.RdiDiiaCreateTask().execute(rdi.pk, diia_hh_ids=[991, 992, 993])

        self.assertEqual(ImportedIndividual.objects.filter(disability=DISABLED).count(), 1)
        self.assertEqual(ImportedIndividual.objects.filter(disability=NOT_DISABLED).count(), 8)
        self.assertEqual(
            ImportedIndividual.objects.filter(relationship__in=[x[0] for x in RELATIONSHIP_CHOICE]).count(), 9
        )
        self.assertEqual(
            ImportedIndividual.objects.filter(marital_status__in=[x[0] for x in MARITAL_STATUS_CHOICE]).count(), 9
        )
