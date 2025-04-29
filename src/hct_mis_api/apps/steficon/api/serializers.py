from rest_framework import serializers

from hct_mis_api.apps.steficon.models import Rule, RuleCommit


class RuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rule
        fields = (
            "id",
            "name",
            "description",
            "type",
        )


class RuleCommitSerializer(serializers.ModelSerializer):
    rule = RuleSerializer(read_only=True)

    class Meta:
        model = RuleCommit
        fields = (
            "id",
            "version",
            "rule",
        )
