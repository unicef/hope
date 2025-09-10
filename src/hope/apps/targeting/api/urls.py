from django.urls import include, path

from hope.apps.program.api.urls import program_base_router

app_name = "targeting"

program_nested_router = program_base_router.program_nested_router

urlpatterns = [
    path("", include(program_nested_router.urls)),
]
