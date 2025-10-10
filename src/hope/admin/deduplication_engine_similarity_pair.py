import logging

from adminfilters.autocomplete import AutoCompleteFilter
from django.contrib import admin

from hope.admin.utils import HOPEModelAdminBase
from hope.models.deduplication_engine_similarity_pair import DeduplicationEngineSimilarityPair

logger = logging.getLogger(__name__)


@admin.register(DeduplicationEngineSimilarityPair)
class DeduplicationEngineSimilarityPairAdmin(HOPEModelAdminBase):
    list_display = ("program", "individual1", "individual2", "similarity_score")
    list_filter = (("program", AutoCompleteFilter),)
    raw_id_fields = ("program", "individual1", "individual2")
    search_fields = ("program", "individual1", "individual2")
