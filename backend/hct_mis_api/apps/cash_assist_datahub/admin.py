# Register your models here.
from admin_extra_urls.api import action
from admin_extra_urls.mixins import ExtraUrlMixin
from adminfilters.filters import TextFieldFilter, AllValuesComboFilter, AllValuesRadioFilter
from django.contrib import admin

from hct_mis_api.apps.cash_assist_datahub.models import (
    CashPlan,
    Session,
    TargetPopulation,
    Programme,
    ServiceProvider,
    PaymentRecord,
)


@admin.register(Session)
class SessionAdmin(ExtraUrlMixin, admin.ModelAdmin):
    list_display = ('timestamp', 'id', 'source', 'status', 'last_modified_date', 'business_area')
    date_hierarchy = 'timestamp'
    list_filter = ('status', 'source', TextFieldFilter.factory('business_area'))
    ordering = 'timestamp',

    @action
    def inspect(self, pk):
        pass


@admin.register(CashPlan)
class CashPlanAdmin(admin.ModelAdmin):
    list_display = ('session', 'name', 'status', 'business_area', 'cash_plan_id')
    list_filter = ('status',
                   TextFieldFilter.factory('session__id'),
                   TextFieldFilter.factory('business_area'))
    date_hierarchy = 'session__timestamp'
    raw_id_fields = ('session',)


@admin.register(PaymentRecord)
class PaymentRecordAdmin(admin.ModelAdmin):
    list_display = ('session', 'business_area', 'status', 'full_name')
    raw_id_fields = ('session',)
    date_hierarchy = 'session__timestamp'
    list_filter = ('status',
                   'delivery_type',
                   TextFieldFilter.factory('session__id'),
                   TextFieldFilter.factory('business_area'))


@admin.register(ServiceProvider)
class ServiceProviderAdmin(admin.ModelAdmin):
    list_display = ('session', 'business_area', 'full_name', 'short_name', 'country')
    raw_id_fields = ('session',)
    date_hierarchy = 'session__timestamp'
    search_fields = ('full_name',)
    list_filter = (TextFieldFilter.factory('session__id'),
                   TextFieldFilter.factory('business_area'))


@admin.register(Programme)
class ProgrammeAdmin(admin.ModelAdmin):
    list_display = ('session', 'mis_id', 'ca_id', 'ca_hash_id')
    raw_id_fields = ('session',)
    date_hierarchy = 'session__timestamp'
    list_filter = (TextFieldFilter.factory('session__id'),
                   TextFieldFilter.factory('ca_hash_id'),
                   TextFieldFilter.factory('mis_id'),
                   TextFieldFilter.factory('ca_id'))


@admin.register(TargetPopulation)
class TargetPopulationAdmin(admin.ModelAdmin):
    list_display = ('session', 'mis_id', 'ca_id', 'ca_hash_id')
    raw_id_fields = ('session',)
    date_hierarchy = 'session__timestamp'
    list_filter = (TextFieldFilter.factory('session__id'),
                   TextFieldFilter.factory('ca_hash_id'),
                   TextFieldFilter.factory('mis_id'),
                   TextFieldFilter.factory('ca_id'))
