from django.contrib import admin

from hope.admin.utils import HOPEModelAdminBase
from hope.apps.payment.models.payment import OfflineExchangeRates


@admin.register(OfflineExchangeRates)
class OfflineExchangeRatesAdmin(HOPEModelAdminBase):
    def has_add_permission(self, request):
        return False
