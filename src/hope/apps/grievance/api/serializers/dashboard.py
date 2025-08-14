from rest_framework import serializers


class TicketsByTypeSerializer(serializers.Serializer):
    user_generated_count = serializers.IntegerField()
    system_generated_count = serializers.IntegerField()
    closed_user_generated_count = serializers.IntegerField()
    closed_system_generated_count = serializers.IntegerField()
    user_generated_avg_resolution = serializers.FloatField()
    system_generated_avg_resolution = serializers.FloatField()


class ChartDatasetSerializer(serializers.Serializer):
    data = serializers.ListField(child=serializers.IntegerField())


class ChartDataSerializer(serializers.Serializer):
    labels = serializers.ListField(child=serializers.CharField())
    datasets = serializers.ListField(child=ChartDatasetSerializer())


class DetailedChartDatasetSerializer(serializers.Serializer):
    label = serializers.CharField()
    data = serializers.ListField(child=serializers.IntegerField())


class DetailedChartDataSerializer(serializers.Serializer):
    labels = serializers.ListField(child=serializers.CharField())
    datasets = serializers.ListField(child=DetailedChartDatasetSerializer())


class GrievanceDashboardSerializer(serializers.Serializer):
    tickets_by_type = TicketsByTypeSerializer()
    tickets_by_status = ChartDataSerializer()
    tickets_by_category = ChartDataSerializer()
    tickets_by_location_and_category = DetailedChartDataSerializer()
