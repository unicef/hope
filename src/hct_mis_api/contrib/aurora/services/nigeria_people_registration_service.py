from typing import Any, Dict, Optional

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
from hct_mis_api.apps.registration_data.models import RegistrationDataImport
from hct_mis_api.contrib.aurora.services.generic_registration_service import (
    GenericRegistrationService,
    mergedicts,
)


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
            "intro-and-consent": {
                "enumerator_code": "household.flex_fields",
                "who_to_register": "household.flex_fields",
            },
            "household-info": {
                "admin1_h_c": "household.admin1",
                "admin2_h_c": "household.admin2",
                "admin3_h_c": "household.admin3",
                "admin4_h_c": "household.admin4",
            },
            "individual-details": {
                "given_name_i_c": "individual.given_name",
                "family_name_i_c": "individual.family_name",
                "birth_date_i_c": "individual.birth_date",
                "gender_i_c": "individual.sex",
                "email_i_c": "individual.email",
                "phone_no_i_c": "individual.phone_no",
                "estimated_birth_date_i_c": "individual.estimated_birth_date",
                "confirm_phone_no": "individual.phone_no_alternative",
                "account_details": "account_details.data",
            },
        }

        mapping = mergedicts(default_mapping, self.registration.mapping or {}, [])

        household = self.create_household_data(record, registration_data_import, mapping)
        individuals, head, pr_collector, _ = self.create_individuals(
            record,
            household,
            mapping,
        )

        individual = individuals[0]
        collector = pr_collector or head or individual
        head_of_household = head or individual
        household.head_of_household = head_of_household
        PendingIndividualRoleInHousehold.objects.create(individual=collector, household=household, role=ROLE_PRIMARY)

        record_data_dict = record.get_data()
        individual_data = record_data_dict.get(mapping["defaults"].get("individuals_key", "individual-details"), [])[0]
        self._prepare_national_id(individual_data, individual)

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
