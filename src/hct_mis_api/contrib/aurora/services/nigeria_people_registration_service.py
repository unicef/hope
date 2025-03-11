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
                "households_key": "household-details",
                "bank_key": "ind-bank-info",
                "country": "NG",
            },
            "household": {
                "admin1_h_c": "household.admin1",
                "admin2_h_c": "household.admin2",
                "admin3_h_c": "household.admin3",
                "admin4_h_c": "household.admin4",
                "consent_h_c": "household.consent",
            },
            "individuals": {
                "given_name_i_c": "individual.given_name",
                "family_name_i_c": "individual.family_name",
                "birth_date_i_c": "individual.birth_date",
                "gender_i_c": "individual.sex",
                "email": "individual.email",
                "phone_no_i_c": "individual.phone_no",
                "estimated_birth_date_i_c": "individual.estimated_birth_date",
                "confirm_phone_no": "individual.phone_no_alternative",  # ? TODO
            },
            "flex-fields": ["org_enumerator_h_c"],
        }

        mapping = mergedicts(default_mapping, self.registration.mapping, [])
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

        record_data_dict = record.get_data()
        accounts_data = record_data_dict.get(mapping["defaults"].get("bank_key", "ind-bank-info"), [])
        if accounts_data:
            if primary_collector_account_details := accounts_data[0].get("account_details"):
                PendingDeliveryMechanismData.objects.create(
                    individual=pr_collector,
                    delivery_mechanism=DeliveryMechanism.objects.get(code="transfer_to_account"),
                    data={
                        "bank_account_number__transfer_to_account": primary_collector_account_details.get(
                            "account_number", ""
                        ),
                        "bank_name__transfer_to_account": primary_collector_account_details.get("institution_code", ""),
                    },
                )

        ind_data_dict = (
            record_data_dict.get(mapping["defaults"].get("individuals_key", "individual-details"), [])[0] or {}
        )
        self._prepare_national_id(ind_data_dict, pr_collector)

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
