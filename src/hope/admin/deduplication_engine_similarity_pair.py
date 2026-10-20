import logging

from adminfilters.autocomplete import AutoCompleteFilter
from django.contrib import admin

from hope.admin.utils import HOPEModelAdminBase
from hope.models import BiographicDedupeSimilarityPair, BiometricDedupeSimilarityPair

logger = logging.getLogger(__name__)


@admin.register(BiometricDedupeSimilarityPair)
class BiometricDeduplicationEngineSimilarityPairAdmin(HOPEModelAdminBase):
    list_display = ("program", "individual1", "individual2", "similarity_score")
    list_select_related = ("program", "individual1", "individual2")
    list_filter = (("program", AutoCompleteFilter),)
    readonly_fields = ("program", "individual1", "individual2", "similarity_score")
    search_fields = ("program__name", "individual1__unicef_id", "individual2__unicef_id")


@admin.register(BiographicDedupeSimilarityPair)
class BiographicDeduplicationEngineSimilarityPairAdmin(HOPEModelAdminBase):
    list_display = ("program", "individual1", "individual2", "similarity_score", "proximity_to_score")
    list_select_related = ("program", "individual1", "individual2")
    list_filter = (("program", AutoCompleteFilter),)
    readonly_fields = ("program", "individual1", "individual2", "similarity_score", "proximity_to_score")
    search_fields = ("program__name", "individual1__unicef_id", "individual2__unicef_id")
