from rest_framework import serializers


class DashboardHouseholdSerializer(serializers.Serializer):
    business_area_name = serializers.CharField()
    total_delivered_quantity_usd = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_delivered_quantity = serializers.DecimalField(max_digits=12, decimal_places=2)
    payments = serializers.IntegerField()
    individuals = serializers.IntegerField()
    households = serializers.IntegerField()
    children_counts = serializers.IntegerField()
    month = serializers.CharField()
    year = serializers.IntegerField()
    program = serializers.CharField()
    sector = serializers.CharField()
    status = serializers.CharField()
    admin1 = serializers.CharField()
    fsp = serializers.CharField()
    delivery_types = serializers.CharField()
    pwd_counts = serializers.IntegerField()
