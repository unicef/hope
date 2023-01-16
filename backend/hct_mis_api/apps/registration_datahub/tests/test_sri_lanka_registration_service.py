import datetime

from django.test import TestCase
from django.utils import timezone

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.household.models import IDENTIFICATION_TYPE_NATIONAL_ID
from hct_mis_api.apps.registration_datahub.models import (
    ImportedBankAccountInfo,
    ImportedDocument,
    ImportedDocumentType,
    ImportedHousehold,
    ImportedIndividual,
    ImportedIndividualRoleInHousehold,
    Record,
)
from hct_mis_api.apps.registration_datahub.services.flex_registration_service import (
    SriLankaRegistrationService,
)


class TestUkrainianRegistrationService(TestCase):
    databases = {
        "default",
        "registration_datahub",
    }
    fixtures = ("hct_mis_api/apps/geo/fixtures/data.json",)

    @classmethod
    def setUp(cls) -> None:
        ImportedDocumentType.objects.create(
            type=IDENTIFICATION_TYPE_NATIONAL_ID,
            label=IDENTIFICATION_TYPE_NATIONAL_ID,
        )

        BusinessArea.objects.create(
            **{
                "code": "0780",
                "name": "Sri Lanka",
                "long_name": "THE DEMOCRATIC SOCIALIST REPUBLIC OF SRI LANKA",
                "region_code": "64",
                "region_name": "SAR",
                "slug": "sri-lanka",
                "has_data_sharing_agreement": True,
            },
        )

        children_info = [
            {
                "gender_i_c": "male",
                "full_name_i_c": "Alexis",
                "birth_date_i_c": "2022-01-04",
                "relationship_i_c": "son_daughter",
            }
        ]

        caretaker_info = [
            {
                "gender_i_c": "female",
                "full_name_i_c": "Alexis",
                "birth_date_i_c": "1989-01-04",
                "has_nic_number_i_c": "n",
                "who_answers_phone_i_c": "mother/caretaker",
            }
        ]

        collector_info = [
            {
                "bank_name": "7472",
                "gender_i_c": " male",
                "phone_no_i_c": "+94788908046",
                "full_name_i_c": "Dome",
                "birth_date_i_c": "1980-01-04",
                "bank_description": "Axis Bank",
                "relationship_i_c": "brother_sister",
                "confirm_nic_number": "123456789V",
                "national_id_no_i_c": "123456789V",
                "branch_or_branch_code": "7472_002",
                "who_answers_this_phone": "alternate collector",
                "confirm_alternate_collector_phone_number": "+94788908046",
                "does_the_mothercaretaker_have_her_own_active_bank_account_not_samurdhi": "n",
            }
        ]

        localization_info = [
            {
                "admin2_h_c": "LK71",
                "admin3_h_c": "LK7163",
                "admin4_h_c": "LK7163105",
                "address_h_c": "Alexis",
                "moh_center_of_reference": "MOH279",
            }
        ]

        defaults = {
            "registration": 1,
            "timestamp": timezone.make_aware(datetime.datetime(2022, 4, 1)),
        }

        records = [
            Record(
                **defaults,
                source_id=1,
                fields={
                    "children-info": children_info,
                    "id_enumerator": "1992",
                    "caretaker-info": caretaker_info,
                    "collector-info": collector_info,
                    "localization-info": localization_info,
                    "prefered_language_of_contact": "ta",
                },
            ),
        ]

        cls.records = Record.objects.bulk_create(records)
        cls.user = UserFactory.create()

    def test_import_data_to_datahub(self) -> None:
        service = SriLankaRegistrationService()
        rdi = service.create_rdi(self.user, f"sri_lanka rdi {datetime.datetime.now()}")
        records_ids = [x.id for x in self.records]
        service.process_records(rdi.id, records_ids)

        self.records[0].refresh_from_db()
        self.assertEqual(Record.objects.filter(id__in=records_ids, ignored=False).count(), 1)

        self.assertEqual(ImportedHousehold.objects.count(), 1)
        self.assertEqual(ImportedIndividualRoleInHousehold.objects.count(), 1)
        self.assertEqual(ImportedBankAccountInfo.objects.count(), 1)
        self.assertEqual(ImportedDocument.objects.count(), 1)

        self.assertEqual(
            ImportedIndividual.objects.filter(relationship="HEAD").first().flex_fields, {"has_nic_number_i_c": "n"}
        )

        self.assertEqual(
            ImportedIndividual.objects.filter(full_name="Dome").first().flex_fields,
            {
                "confirm_nic_number": "123456789V",
                "branch_or_branch_code": "7472_002",
                "who_answers_this_phone": "alternate collector",
                "confirm_alternate_collector_phone_number": "+94788908046",
                "does_the_mothercaretaker_have_her_own_active_bank_account_not_samurdhi": "n",
            },
        )
