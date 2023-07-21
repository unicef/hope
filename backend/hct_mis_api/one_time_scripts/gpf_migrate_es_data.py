"""
This migration has to be run after `gpf_migrate_psql_data`, because it refers to newly populated program_id
"""

import logging
from typing import Dict, List

from elasticsearch import Elasticsearch
from elasticsearch_dsl import UpdateByQuery

from hct_mis_api.apps.household.documents import HouseholdDocument, get_individual_doc
from hct_mis_api.apps.household.models import Household, Individual
from hct_mis_api.apps.program.models import Program

logger = logging.getLogger(__name__)

client = Elasticsearch("elasticsearch")


def update_body(obj_list: List[str]) -> Dict:  # noqa
    return {
        "query": {"bool": {"must_not": {"exists": {"field": "program_id"}}, "filter": {"terms": {"_id": obj_list}}}}
    }


def migrate_program_es_db(batch_size: int = 500) -> None:
    all_programs = Program.objects.all()

    for program in all_programs:
        program_id = program.id
        household_ids = list(Household.objects.filter(program_id=program_id).values_list("id", flat=True))

        source = f"ctx._source.program_id = '{program_id}'"

        i, household_ids_pages = 0, len(household_ids) // batch_size
        try:
            while i <= household_ids_pages:
                logger.info(f"Processing es data {i}/{household_ids_pages} page")
                body = update_body(obj_list=[str(_id) for _id in household_ids[batch_size * i : batch_size * (i + 1)]])
                query = (
                    UpdateByQuery(index=HouseholdDocument.Index.name)
                    .using(client)
                    .update_from_dict(body)
                    .script(source=source)
                )
                query.execute()

                i += 1

        except Exception:
            logger.error("Updating household es program_id failed")

        business_area_slug = program.business_area.slug
        individual_ids = list(Individual.objects.filter(program_id=program_id).values_list("id", flat=True))

        i, individual_ids_pages = 0, len(individual_ids) // batch_size + 1
        try:
            while i <= individual_ids_pages:
                logger.info(f"Processing es data {i}/{individual_ids_pages} page")
                body = update_body(obj_list=[str(_id) for _id in individual_ids[batch_size * i : batch_size * (i + 1)]])
                index = get_individual_doc(business_area_slug=business_area_slug).Index.name
                query = UpdateByQuery(index=index).using(client).update_from_dict(body).script(source=source)
                query.execute()

                i += 1

        except Exception:
            logger.error("Updating individual es program_id failed")
