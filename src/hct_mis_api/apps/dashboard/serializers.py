from typing import List, Optional

from rest_framework import serializers

from hct_mis_api.apps.household.models import Household
from hct_mis_api.apps.payment.models import Payment, PaymentRecord


class PaymentSerializer(serializers.ModelSerializer):
    fsp = serializers.CharField(source="financial_service_provider.name")
    delivery_type = serializers.CharField(source="delivery_type.name", allow_null=True)

    class Meta:
        model = Payment
        fields: List[str] = [
            "delivered_quantity",
            "delivery_date",
            "delivered_quantity_usd",
            "currency",
            "fsp",
            "delivery_type",
            "status",
        ]


class PaymentRecordSerializer(serializers.ModelSerializer):
    fsp = serializers.CharField(source="service_provider.short_name")
    delivery_type = serializers.CharField(source="delivery_type.name", allow_null=True)

    class Meta:
        model = PaymentRecord
        fields: List[str] = [
            "delivered_quantity",
            "delivery_date",
            "delivered_quantity_usd",
            "currency",
            "fsp",
            "delivery_type",
            "status",
        ]


class DashboardHouseholdSerializer(serializers.ModelSerializer):
    payments = serializers.SerializerMethodField()
    business_area = serializers.CharField(source="business_area.slug")
    program = serializers.CharField(source="program.name")
    sector = serializers.CharField(source="program.sector")
    admin1 = serializers.SerializerMethodField()
    admin2 = serializers.SerializerMethodField()

    class Meta:
        model = Household
        fields: List[str] = [
            "id",
            "business_area",
            "payments",
            "program",
            "size",
            "first_registration_date",
            "admin1",
            "admin2",
            "sector",
            "children_count",
        ]

    def get_admin1(self, obj: Household) -> Optional[str]:
        if obj.admin1:
            return obj.admin1.name
        return None

    def get_admin2(self, obj: Household) -> Optional[str]:
        if obj.admin2:
            return obj.admin2.name
        return None

    def get_payments(self, obj: Household) -> List[dict]:
        payments = (
            Payment.objects.using("read_only")
            .filter(household=obj)
            .select_related("financial_service_provider", "delivery_type")
        )

        payment_records = (
            PaymentRecord.objects.using("read_only")
            .filter(household=obj)
            .select_related("service_provider", "delivery_type")
        )

        payments_data = list(PaymentSerializer(payments, many=True).data)
        payment_records_data = list(PaymentRecordSerializer(payment_records, many=True).data)

        return payments_data + payment_records_data
