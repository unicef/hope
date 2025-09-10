from django.urls import path

from hope.apps.changelog import views

urlpatterns = (
    path("", views.ChangelogListView.as_view(), name="changelog_changelog_list"),
    path(
        "detail/<int:pk>/",
        views.ChangelogDetailView.as_view(),
        name="changelog_changelog_detail",
    ),
)
