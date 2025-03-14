from typing import Any, Dict, Optional

from contrib.aurora.services.generic_registration_service import (
    GenericRegistrationService,
    mergedicts,
)

from hct_mis_api.apps.core.utils import (
    IDENTIFICATION_TYPE_NATIONAL_ID,
    IDENTIFICATION_TYPE_TO_KEY_MAPPING,
)
from hct_mis_api.apps.geo.models import Country
from hct_mis_api.apps.household.models import (
    ROLE_PRIMARY,
    DocumentType,
    PendingDocument,
    PendingIndividual,
    PendingIndividualRoleInHousehold,
)
from hct_mis_api.apps.payment.models import (
    DeliveryMechanism,
    PendingDeliveryMechanismData,
)
from hct_mis_api.apps.registration_data.models import RegistrationDataImport


class NigeriaPeopleRegistrationService(GenericRegistrationService):
    def create_household_for_rdi_household(self, record: Any, registration_data_import: RegistrationDataImport) -> None:
        default_mapping = {
            "defaults": {
                "individuals_key": "individual-details",
                "households_key": "household-info",
                "intro_data_key": "intro-and-consent",
                "account_key": "account_details",
                "country": "NG",
            },
            "household": {
                "admin1_h_c": "household.admin1",
                "admin2_h_c": "household.admin2",
                "admin3_h_c": "household.admin3",
                "admin4_h_c": "household.admin4",
            },
            "individuals": {
                "given_name_i_c": "individual.given_name",
                "family_name_i_c": "individual.family_name",
                "birth_date_i_c": "individual.birth_date",
                "gender_i_c": "individual.sex",
                "email_i_c": "individual.email",
                "phone_no_i_c": "individual.phone_no",
                "estimated_birth_date_i_c": "individual.estimated_birth_date",
                "confirm_phone_no": "individual.phone_no_alternative",
            },
            "flex-fields": ["enumerator_code", "who_to_register", "frontline_worker_designation_i_f"],
        }

        mapping = mergedicts(default_mapping, self.registration.mapping, [])
        record_data_dict = record.get_data()
        household_data = record_data_dict.get(mapping["defaults"].get("households_key", "household-info"), [])
        intro_data = record_data_dict.get(mapping["defaults"].get("intro_data_key", "intro-and-consent"), [])
        individual_data = record_data_dict.get(mapping["defaults"].get("individuals_key", "individual-details"), [])

        household_data[0].update(intro_data[0])
        household = self.create_household_data(record, registration_data_import, mapping)

        individuals, head, pr_collector, _ = self.create_individuals(
            record,
            household,
            mapping,
        )

        collector = pr_collector or head or individuals[0]
        head_of_household = head or individuals[0]
        household.head_of_household = head_of_household
        PendingIndividualRoleInHousehold.objects.create(individual=collector, household=household, role=ROLE_PRIMARY)

        accounts_data = individual_data[0].get(mapping["defaults"].get("account_key", "account_details"), {})
        if accounts_data:
            PendingDeliveryMechanismData.objects.create(
                individual=pr_collector,
                delivery_mechanism=DeliveryMechanism.objects.get(code="transfer_to_account"),
                data={
                    "bank_account_number__transfer_to_account": accounts_data.get("number", ""),
                    "bank_name__transfer_to_account": accounts_data.get("name", ""),
                    "bank_code__transfer_to_account": accounts_data.get("code", ""),
                    "account_holder_name__transfer_to_account": accounts_data.get("holder_name", ""),
                },
            )

        self._prepare_national_id(individual_data, pr_collector)

        household.registration_id = record.source_id
        household.detail_id = record.source_id
        household.save()
        record.mark_as_imported()

    def _prepare_national_id(
        self, individual_dict: Dict, imported_individual: PendingIndividual
    ) -> Optional[PendingDocument]:
        national_id = individual_dict.get("national_id_no_i_c")
        if not national_id:
            return None
        return PendingDocument.objects.create(
            program=imported_individual.program,
            document_number=national_id,
            individual=imported_individual,
            type=DocumentType.objects.get(key=IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_NATIONAL_ID]),
            country=Country.objects.get(iso_code2="NG"),
        )
