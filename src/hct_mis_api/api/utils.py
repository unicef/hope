from base64 import b64encode
from typing import Any

from rest_framework import serializers
from rest_framework.authentication import SessionAuthentication


def humanize_errors(errors: dict) -> dict:
    try:
        households = errors.pop("households", [])
        errs = {}
        if len(households) == 1 and isinstance(households[0], str):
            hh_info = households
        else:
            hh_info = []
            for i, h in enumerate(households, 1):
                if h and isinstance(h, dict):
                    members = h.pop("members", [])
                    mm_info: list | dict
                    if isinstance(members, list) and len(members) == 1 and isinstance(members[0], str):
                        mm_info = members
                    else:
                        mm_info = {f"Member #{i}": [m] for i, m in enumerate(members, 1) if m}
                    if mm_info:
                        h["members"] = mm_info
                if h:
                    hh_info.append({f"Household #{i}": [h]})
        if hh_info:
            errs["households"] = hh_info
        errs.update(**errors)
        return errs
    except (ValueError, AttributeError):
        return errors


class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request: Any) -> None:
        return


class EncodedIdSerializerMixin(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()

    class Meta:
        abstract = True

    def encode_id_base64_api(self, id_string: str, model_name: str) -> str:
        return b64encode(f"{model_name}:{str(id_string)}".encode()).decode()

    def get_id(self, obj: Any) -> str:
        model_name = self.Meta.model.__name__
        return self.encode_id_base64_api(obj.id, model_name)
