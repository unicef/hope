from rest_framework import serializers

from hct_mis_api.apps.core.utils import decode_id_string, encode_id_base64_required


class Base64ModelField(serializers.Field):
    def __init__(self, *, model_name, **kwargs):
        super().__init__(**kwargs)
        self.model_name = model_name

    def to_representation(self, value):
        return encode_id_base64_required(value, self.model_name)

    def to_internal_value(self, data):
        try:
            return decode_id_string(data)
        except Exception:
            raise serializers.ValidationError("Invalid base64 id.")
