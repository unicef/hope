from django.urls import include, path

from hope.apps.accountability.api.views import (
    FeedbackViewSet,
    MessageViewSet,
    SurveyViewSet,
)
from hope.apps.core.api.urls import get_business_area_nested_router
from hope.apps.program.api.urls import program_base_router

app_name = "accountability"

business_area_nested_router = get_business_area_nested_router()
business_area_nested_router.register(
    "feedbacks",
    FeedbackViewSet,
    basename="feedbacks",
)

program_nested_router = program_base_router.program_nested_router
program_nested_router.register(
    "feedbacks",
    FeedbackViewSet,
    basename="feedbacks-per-program",
)
program_nested_router.register(
    "messages",
    MessageViewSet,
    basename="messages",
)
program_nested_router.register(
    "surveys",
    SurveyViewSet,
    basename="surveys",
)

urlpatterns = [
    path("", include(business_area_nested_router.urls)),
    path("", include(program_nested_router.urls)),
]
