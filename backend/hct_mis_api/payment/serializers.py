from rest_framework import serializers


class PaymentInstructionSerializer(serializers.Serializer):
    remote_id = serializers.CharField(max_length=255)
    unicef_id = serializers.CharField(max_length=255)
    status = serializers.ReadOnlyField()
    fsp = serializers.CharField(max_length=100)
    # system = serializers.CharField(max_length=100)
    tag = serializers.CharField(max_length=255, required=False)
    payload = serializers.JSONField()


class PaymentRecordSerializer(serializers.Serializer):
    uuid = serializers.UUIDField(read_only=True)
    status = serializers.ReadOnlyField()
    record_code = serializers.CharField(max_length=64)
    parent = serializers.UUIDField()
    payload = serializers.JSONField()
    # {"amount": 800, "phone_no": "166123456", "last_name": "Anderson", "first_name": "Felipe"}
