from rest_framework import serializers


class DashboardBaseSerializer(serializers.Serializer):
    total_delivered_quantity_usd = serializers.DecimalField(max_digits=12, decimal_places=2)
    payments = serializers.IntegerField()
    individuals = serializers.IntegerField()
    households = serializers.IntegerField()
    children_counts = serializers.IntegerField()
    year = serializers.IntegerField()
    program = serializers.CharField()
    sector = serializers.CharField()
    status = serializers.CharField()
    fsp = serializers.CharField()
    delivery_types = serializers.CharField()
    pwd_counts = serializers.IntegerField()
    reconciled = serializers.IntegerField()
    finished_payment_plans = serializers.IntegerField()
    total_payment_plans = serializers.IntegerField()


class DashboardHouseholdSerializer(DashboardBaseSerializer):
    month = serializers.CharField()
    admin1 = serializers.CharField()
    currency = serializers.CharField()
    total_delivered_quantity = serializers.DecimalField(max_digits=12, decimal_places=2)


class DashboardGlobalSerializer(DashboardBaseSerializer):
    country = serializers.CharField()
