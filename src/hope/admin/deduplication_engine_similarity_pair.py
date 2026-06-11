import logging

from adminfilters.autocomplete import AutoCompleteFilter
from django.contrib import admin

from hope.admin.utils import HOPEModelAdminBase
from hope.models import BiometricDedupeSimilarityPair

logger = logging.getLogger(__name__)


@admin.register(BiometricDedupeSimilarityPair)
class BiometricDeduplicationEngineSimilarityPairAdmin(HOPEModelAdminBase):
    list_display = ("program", "individual1", "individual2", "similarity_score")
    list_filter = (("program", AutoCompleteFilter),)
    search_fields = ("program", "individual1", "individual2")
