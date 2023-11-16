import logging
from dataclasses import dataclass, field
from functools import partial
from typing import Dict, List, Union

from django.conf import settings

from elasticsearch import Elasticsearch, helpers
from elasticsearch_dsl import Document

from hct_mis_api.apps.household.documents import (
    HouseholdDocument,
    IndividualDocumentAfghanistan,
    IndividualDocumentOthers,
    IndividualDocumentUkraine,
)
from hct_mis_api.apps.household.models import Household, Individual

logger = logging.getLogger(__name__)

es_conn = Elasticsearch(settings.ELASTICSEARCH_HOST)


class ElasticSearchMixin:
    def prepare(self, obj: Union[Household, Individual]) -> None:
        data = self.document.prepare(obj)
        doc = {
            "_op_type": "update",
            "_index": self.document.Index.name,
            "_id": str(obj.id),
            "doc": data,
            "doc_as_upsert": True,
        }
        self.documents_to_update.append(doc)

    def process(self) -> None:
        if self.documents_to_update:
            try:
                helpers.bulk(es_conn, self.documents_to_update)
            except Exception:
                logger.error(f"Updating {','.join([str(_id) for _id in self.ids])} of {self.document.__name__} failed")

            logger.info(f"{type(self.document).__name__} have been updated.")
        else:
            logger.info(f"Nothing to update for index: {self.document.Index.name}")


@dataclass
class AfghanistanIndividualHelper(ElasticSearchMixin):
    document: Document = IndividualDocumentAfghanistan()
    documents_to_update: List[Dict] = field(default_factory=list)


@dataclass
class UkraineIndividualHelper(ElasticSearchMixin):
    document: Document = IndividualDocumentUkraine()
    documents_to_update: list = field(default_factory=list)


@dataclass
class OthersIndividualHelper(ElasticSearchMixin):
    document: Document = IndividualDocumentOthers
    documents_to_update: list = field(default_factory=list)


@dataclass
class HouseholdHelper(ElasticSearchMixin):
    document: Document = HouseholdDocument()
    documents_to_update: list = field(default_factory=list)


def bulk_upsert(ids: List[str], model: Union[Household, Individual]) -> None:
    if model == Household:
        queryset = Household.objects.filter(unicef_id__in=ids).select_related("business_area")
        household_helper = HouseholdHelper()
        for obj in queryset:
            household_helper.prepare(obj)
        household_helper.process()
        return
    else:
        queryset = Individual.objects.filter(unicef_id__in=ids).select_related("business_area")
        mapper = {
            "afghanistan": AfghanistanIndividualHelper(),
            "ukraine": UkraineIndividualHelper(),
            "others": OthersIndividualHelper(),
        }
        for obj in queryset:
            mapper.get(obj.business_area.slug, "others").prepare(obj)
        mapper["afghanistan"].process()
        mapper["ukraine"].process()
        mapper["others"].process()
        return


bulk_upsert_individuals = partial(bulk_upsert, model=Individual)
bulk_upsert_households = partial(bulk_upsert, model=Household)
