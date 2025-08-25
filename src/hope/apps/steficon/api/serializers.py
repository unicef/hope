from rest_framework import serializers

from models.steficon import Rule, RuleCommit


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
