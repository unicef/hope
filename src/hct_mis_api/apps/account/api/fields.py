from typing import Any

from rest_framework import serializers

from hct_mis_api.apps.core.utils import decode_id_string, encode_id_base64_required


class Base64ModelField(serializers.Field):
    def __init__(self, *, model_name: str, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.model_name = model_name

    def to_representation(self, value: str) -> str:
        return encode_id_base64_required(value, self.model_name)

    def to_internal_value(self, data: str) -> str | None:
        try:
            return decode_id_string(data)
        except Exception:
            raise serializers.ValidationError("Invalid base64 id.")
