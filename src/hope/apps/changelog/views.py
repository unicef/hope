from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic

from hope.apps.changelog.forms import ChangelogForm
from models.changelog import Changelog


class ChangelogListView(LoginRequiredMixin, generic.ListView):
    queryset = Changelog.objects.filter(active=True)
    form_class = ChangelogForm


class ChangelogDetailView(LoginRequiredMixin, generic.DetailView):
    model = Changelog
    form_class = ChangelogForm
