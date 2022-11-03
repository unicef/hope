from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect

from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.accountability.models import SampleFileExpiredException, Survey
from hct_mis_api.apps.core.utils import decode_id_string


@login_required
def download_cash_plan_payment_verification(request, survey_id):
    survey = get_object_or_404(Survey, id=decode_id_string(survey_id))

    if not request.user.has_permission(Permissions.ACCOUNTABILITY_SURVEY_VIEW_DETAILS.name, survey.business_area):
        raise PermissionDenied("Permission Denied: User does not have correct permission.")

    try:
        if sample_file_path := survey.sample_file_path():
            return redirect(sample_file_path)
        return HttpResponse("Sample file doesn't exist", status=404)
    except SampleFileExpiredException:
        return HttpResponse("Sample file expired", status=400)
