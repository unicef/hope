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
    program = serializers.CharField(source="program.name")
    sector = serializers.CharField(source="program.sector")
    admin1 = serializers.CharField(source="admin1.name")
    admin2 = serializers.CharField(source="admin2.name")
    pwd_count = serializers.SerializerMethodField()

    class Meta:
        model = Household
        fields: List[str] = [
            "id",
            "payments",
            "program",
            "size",
            "first_registration_date",
            "admin1",
            "admin2",
            "sector",
            "children_count",
            "pwd_count",
        ]

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

    def get_pwd_count(self, obj: Household) -> Optional[int]:
        pwd = sum(
            [
                obj.female_age_group_0_5_disabled_count or 0,
                obj.female_age_group_6_11_disabled_count or 0,
                obj.female_age_group_12_17_disabled_count or 0,
                obj.female_age_group_18_59_disabled_count or 0,
                obj.female_age_group_60_disabled_count or 0,
                obj.male_age_group_0_5_disabled_count or 0,
                obj.male_age_group_6_11_disabled_count or 0,
                obj.male_age_group_12_17_disabled_count or 0,
                obj.male_age_group_18_59_disabled_count or 0,
                obj.male_age_group_60_disabled_count or 0,
            ]
        )
        return pwd
