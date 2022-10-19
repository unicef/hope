from django.urls import reverse_lazy
from django.views import generic

from hct_mis_api.apps.changelog.forms import ChangelogForm
from hct_mis_api.apps.changelog.models import Changelog
from hct_mis_api.apps.core.permissions_views_mixins import ViewPermissionsMixinBase


class ChangelogListView(ViewPermissionsMixinBase, generic.ListView):
    queryset = Changelog.objects.filter(active=True)
    form_class = ChangelogForm


class ChangelogDetailView(ViewPermissionsMixinBase, generic.DetailView):
    model = Changelog
    form_class = ChangelogForm
