from django.urls import include, path

from hct_mis_api.apps.changelog import views

urlpatterns = (
    path("", views.ChangelogListView.as_view(), name="changelog_Changelog_list"),
    path("detail/<int:pk>/", views.ChangelogDetailView.as_view(), name="changelog_Changelog_detail"),
)
