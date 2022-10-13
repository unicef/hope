from django.urls import path, include
from hct_mis_api.apps.changelog import views


urlpatterns = (
    path("", views.ChangelogListView.as_view(), name="changelog_Changelog_list"),
    path("detail/<int:pk>/", views.ChangelogDetailView.as_view(), name="changelog_Changelog_detail")
)
