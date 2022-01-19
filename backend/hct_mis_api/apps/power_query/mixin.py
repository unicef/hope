from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render

from admin_extra_urls.decorators import button
from admin_extra_urls.mixins import ExtraUrlMixin
from hct_mis_api.apps.power_query.models import Query


class PowerQueryMixin(ExtraUrlMixin):
    @button(permission='power_query_query_add')
    def power_query(self, request):
        ct = ContentType.objects.get_for_model(self.model)
        context = self.get_common_context(request,
                                          title='Power Queries',
                                          ct=ct,
                                          entries=Query.objects.filter(target=ct)
                                          )
        return render(request, 'power_query/list.html', context)
