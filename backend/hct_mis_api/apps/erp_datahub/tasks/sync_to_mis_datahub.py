from typing import Dict

from django.db.models import Q
from django.db.transaction import atomic
from django.utils import timezone

from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.erp_datahub.models import DownPayment, FundsCommitment
from hct_mis_api.apps.mis_datahub import models as mis_models


class SyncToMisDatahubTask:
    @staticmethod
    def get_model_dict(model) -> Dict:
        model_dict = {}
        model_dict.update(model.__dict__)
        if "_prefetched_objects_cache" in model_dict:
            del model_dict["_prefetched_objects_cache"]
        del model_dict["_state"]
        del model_dict["business_office_code"]
        return model_dict

    @atomic(using="cash_assist_datahub_erp")
    @atomic(using="default")
    def execute(self):
        # have to be list because it used in another database

        parent_business_area_codes = list(BusinessArea.objects.filter(is_split=True).values_list("code", flat=True))
        normal_down_payments_to_sent = DownPayment.objects.exclude(business_area__in=parent_business_area_codes).filter(
            mis_sync_flag=False
        )
        normal_funds_commitments_to_sent = FundsCommitment.objects.exclude(
            business_area__in=parent_business_area_codes
        ).filter(mis_sync_flag=False)
        down_payments_from_split_business_areas = DownPayment.objects.filter(
            business_area__in=parent_business_area_codes, mis_sync_flag=False
        ).exclude(Q(business_office_code__isnull=True) | Q(business_office_code=""))
        funds_commitments_from_split_business_areas = FundsCommitment.objects.filter(
            business_area__in=parent_business_area_codes, mis_sync_flag=False
        ).exclude(Q(business_office_code__isnull=True) | Q(business_office_code=""))

        mis_down_payments_to_create = []
        funds_commitments_to_create = []
        for down_payment in normal_down_payments_to_sent:
            mis_down_payment = mis_models.DownPayment(**SyncToMisDatahubTask.get_model_dict(down_payment))
            mis_down_payments_to_create.append(mis_down_payment)
        for funds_commitment in normal_funds_commitments_to_sent:
            mis_funds_commitment = mis_models.FundsCommitment(**SyncToMisDatahubTask.get_model_dict(funds_commitment))
            funds_commitments_to_create.append(mis_funds_commitment)
        # with changed business areas
        for down_payment in down_payments_from_split_business_areas:
            mis_down_payment = mis_models.DownPayment(**SyncToMisDatahubTask.get_model_dict(down_payment))
            mis_down_payment.business_area = down_payment.business_office_code
            mis_down_payments_to_create.append(mis_down_payment)
        for funds_commitment in funds_commitments_from_split_business_areas:
            mis_funds_commitment = mis_models.FundsCommitment(**SyncToMisDatahubTask.get_model_dict(funds_commitment))
            mis_funds_commitment.business_area = funds_commitment.business_office_code
            funds_commitments_to_create.append(mis_funds_commitment)
        mis_models.DownPayment.objects.bulk_create(mis_down_payments_to_create)
        mis_models.FundsCommitment.objects.bulk_create(funds_commitments_to_create)
        normal_down_payments_to_sent.update(mis_sync_flag=True, mis_sync_date=timezone.now())
        normal_funds_commitments_to_sent.update(mis_sync_flag=True, mis_sync_date=timezone.now())
        down_payments_from_split_business_areas.update(mis_sync_flag=True, mis_sync_date=timezone.now())
        funds_commitments_from_split_business_areas.update(mis_sync_flag=True, mis_sync_date=timezone.now())
