import logging

from hct_mis_api.apps.grievance.models import GrievanceTicket
from hct_mis_api.apps.household.documents import get_individual_doc
from hct_mis_api.apps.household.models import Individual
from hct_mis_api.apps.payment.models import PaymentPlan
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.registration_data.admin import RegistrationDataImportAdmin
from hct_mis_api.apps.registration_data.models import RegistrationDataImport
from hct_mis_api.apps.registration_datahub import models as datahub_models
from hct_mis_api.apps.registration_datahub.documents import get_imported_individual_doc
from hct_mis_api.apps.utils.elasticsearch_utils import (
    remove_elasticsearch_documents_by_matching_ids,
)

logger = logging.getLogger(__name__)


def delete_plans_and_rdi() -> None:
    delete_plans_and_rdi_for_nigeria()
    delete_rdi_for_palestine()


def delete_plans_and_rdi_for_nigeria() -> None:
    # delete data for Nigeria
    program_nigeria = Program.objects.get(name="VCM Network for Outbreak response", business_area__slug="nigeria")
    rdi_nigeria = RegistrationDataImport.objects.get(name="VCM RDI all data Katsina", program=program_nigeria)
    pplans_ids_to_remove = ["PP-3210-24-00000021", "PP-3210-24-00000022", "PP-3210-24-00000023", "PP-3210-24-00000024"]
    pplans_to_remove = PaymentPlan.objects.filter(unicef_id__in=pplans_ids_to_remove, program=program_nigeria)

    # remove PaymentPlans
    for pplan in pplans_to_remove:
        pplan.delete(soft=False)
    logger.info(f"Deleted {pplans_to_remove.count()} PaymentPlans")

    # remove RDI and related data
    _delete_rdi(rdi=rdi_nigeria)


def delete_rdi_for_palestine() -> None:
    # delete RDI for Palestine
    program_palestine = Program.objects.get(
        name="HCT_Gaza_Response_MPCA_Oct7", business_area__slug="palestine-state-of"
    )
    rdi_palestine = RegistrationDataImport.objects.get(name="HCT_Gaza_July24_B23.1_1", program=program_palestine)
    _delete_rdi(rdi=rdi_palestine)


def _delete_rdi(rdi: RegistrationDataImport) -> None:
    rdi_datahub = datahub_models.RegistrationDataImportDatahub.objects.get(id=rdi.datahub_id)
    datahub_individuals_ids = list(
        datahub_models.ImportedIndividual.objects.filter(registration_data_import=rdi_datahub).values_list(
            "id", flat=True
        )
    )
    individuals_ids = list(Individual.objects.filter(registration_data_import=rdi).values_list("id", flat=True))
    rdi_datahub.delete()
    GrievanceTicket.objects.filter(RegistrationDataImportAdmin.generate_query_for_all_grievances_tickets(rdi)).delete()
    rdi.delete()
    # remove elastic search records linked to individuals
    business_area_slug = rdi.business_area.slug
    remove_elasticsearch_documents_by_matching_ids(
        datahub_individuals_ids, get_imported_individual_doc(business_area_slug)
    )
    remove_elasticsearch_documents_by_matching_ids(individuals_ids, get_individual_doc(business_area_slug))
    logger.info(f"Deleted RDI and related data for {rdi.name}")
