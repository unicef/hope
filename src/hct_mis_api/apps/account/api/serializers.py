from rest_framework import serializers

from hct_mis_api.apps.account.models import User


class ProfileSerializer(serializers.ModelSerializer):
    # permissions_in_scope = serializers.SerializerMethodField()
    # business_areas = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "is_superuser",
        )
