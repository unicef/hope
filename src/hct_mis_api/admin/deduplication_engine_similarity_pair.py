import logging

from django.contrib import admin

from adminfilters.autocomplete import AutoCompleteFilter


from hct_mis_api.admin.utils import HOPEModelAdminBase

from hct_mis_api.apps.registration_data.models import (
    DeduplicationEngineSimilarityPair,
)

logger = logging.getLogger(__name__)


@admin.register(DeduplicationEngineSimilarityPair)
class DeduplicationEngineSimilarityPairAdmin(HOPEModelAdminBase):
    list_display = ("program", "individual1", "individual2", "similarity_score")
    list_filter = (("program", AutoCompleteFilter),)
    raw_id_fields = ("program", "individual1", "individual2")
    search_fields = ("program", "individual1", "individual2")
