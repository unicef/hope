from django.urls import path

from hct_mis_api.api.router import APIRouter

from .views import (
    ChangeStatusPaymentInstruction,
    CreatePaymentInstruction,
    SendRecordsToChangeStatusPaymentInstruction,
)

app_name = "gateway"

router = APIRouter()

urlpatterns = [
    path("instruction/create/", CreatePaymentInstruction().as_view(), name="instruction-create"),
    path("instruction/change_status/", ChangeStatusPaymentInstruction().as_view(), name="instruction-change-status"),
    path(
        "instruction/add_records/",
        SendRecordsToChangeStatusPaymentInstruction().as_view(),
        name="instruction-add-records",
    ),
]
