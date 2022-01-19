from django.urls import path

from .views import api, report

urlpatterns = [
    path("report/<int:pk>/", report),
    path("data/<int:pk>/", api),
]
