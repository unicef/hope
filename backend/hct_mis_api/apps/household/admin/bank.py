import logging

from django.contrib import admin

from hct_mis_api.apps.household.models import BankAccountInfo
from hct_mis_api.apps.utils.admin import RdiMergeStatusAdminMixin

logger = logging.getLogger(__name__)


@admin.register(BankAccountInfo)
class BankAccountAdmin(RdiMergeStatusAdminMixin):
    model = BankAccountInfo
    raw_id_fields = ("individual", "copied_from")
